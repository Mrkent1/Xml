param(
    [string]$Root,
    [string[]]$Companies
)

$ErrorActionPreference = "Stop"

# Options: -Root "C:\\...\\SYNC TAXX" -Companies @("cty ...","Cty ...")

try {
    if (-not $Root -or -not (Test-Path -Path $Root)) {
        # Mặc định: thư mục gốc là cha của thư mục scripts (tools)
        $Root = Split-Path -Parent $PSScriptRoot
    }
    Write-Output ("[INFO] Root: " + $Root)

    if (-not $Companies) {
        # Tự động lấy các thư mục công ty (cấp 1) trong Root
        $Companies = Get-ChildItem -Path $Root -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    }
    Write-Output ('[INFO] Companies: ' + ($Companies -join ', '))

    $reportDir = Join-Path -Path $Root -ChildPath "reports"
    if (-not (Test-Path -Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }

    Add-Type -AssemblyName System.Xml

    function Try-Xml([string]$path) {
        try {
            $xml = New-Object System.Xml.XmlDocument
            $xml.PreserveWhitespace = $true
            $xml.Load($path)
            return $xml
        } catch {
            return $null
        }
    }

    function Get-XmlValues($xml, $ns, [string]$xpath) {
        $nodes = $xml.SelectNodes($xpath, $ns)
        if (-not $nodes) { return "" }
        $vals = @()
        foreach ($n in $nodes) {
            if ($n.NodeType -eq [System.Xml.XmlNodeType]::Attribute) { $vals += $n.Value }
            else { $vals += ($n.InnerText -as [string]) }
        }
        (($vals -join "|") -replace "\s+"," " -replace "^\s+|\s+$","")
    }

    $candidateXPaths = @(
        @{name="mst"; xpath="//t:NNT/t:mst"},
        @{name="pbanDVu"; xpath="//t:TTinChung/t:TTinDVu/t:pbanDVu"},
        @{name="pbanTKhaiXML"; xpath="//t:TTinTKhaiThue//t:pbanTKhaiXML"},
        @{name="ngayLapTKhai"; xpath="//t:TTinTKhaiThue//t:ngayLapTKhai"},
        @{name="kyKKhai"; xpath="//t:KyKKhaiThue/t:kyKKhai"},
        @{name="kieuKy"; xpath="//t:KyKKhaiThue/t:kieuKy"},
        @{name="maTKhai"; xpath="//t:TTinTKhaiThue//t:maTKhai"},
        @{name="tenCQTNoiNop"; xpath="//t:TTinTKhaiThue//t:tenCQTNoiNop"},
        @{name="HSoKhaiThue_id"; xpath="//t:HSoKhaiThue/@id"},
        @{name="ds_DigestValue"; xpath="//ds:Signature/ds:SignedInfo/ds:Reference/ds:DigestValue"},
        @{name="ds_SignatureValue"; xpath="//ds:Signature/ds:SignatureValue"},
        @{name="ds_X509SubjectName"; xpath="//ds:Signature/ds:KeyInfo/ds:X509Data/ds:X509SubjectName"}
    )

    $rows = @()
    $pairs = @()

    foreach ($c in $Companies) {
        $base = Join-Path -Path $Root -ChildPath $c
        if (-not (Test-Path -Path $base)) { Write-Warning ("[WARN] Missing company dir: " + $base); continue }
        $fakeDir = Join-Path -Path $base -ChildPath "fake"

        $realFiles = Get-ChildItem -Path $base -File -ErrorAction SilentlyContinue
        $fakeFiles = Get-ChildItem -Path $fakeDir -File -ErrorAction SilentlyContinue

        Write-Output ('[INFO] Company: ' + $c)
        Write-Output ('        Base: ' + $base)
        Write-Output ('        Fake: ' + $fakeDir + ' (exists=' + (Test-Path -Path $fakeDir) + ')')
        Write-Output ('        Real files: ' + ($realFiles | Measure-Object | Select-Object -ExpandProperty Count))
        Write-Output ('        Fake files: ' + ($fakeFiles | Measure-Object | Select-Object -ExpandProperty Count))

        foreach ($f in ($realFiles + $fakeFiles)) {
            $xml = Try-Xml $f.FullName
            if (-not $xml) { Write-Output ('[SKIP] Not XML: ' + $f.FullName); continue }

            $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
            $ns.AddNamespace("t","http://kekhaithue.gdt.gov.vn/TKhaiThue")
            $ns.AddNamespace("ds","http://www.w3.org/2000/09/xmldsig#")

            $vals = @{}
            foreach ($cx in $candidateXPaths) {
                $vals[$cx.name] = Get-XmlValues $xml $ns $cx.xpath
            }

            $concat = ($vals.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ";"
            $sha = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($concat))).Replace("-","")
            $type = if ((Split-Path $f.DirectoryName -Leaf) -ieq "fake") { "FAKE" } else { "REAL" }

            $rows += [pscustomobject]@{
                Company=$c
                Type=$type
                Name=$f.Name
                Path=$f.FullName
                Size=$f.Length
                LastWrite=($f.LastWriteTime)
                Fingerprint=$sha
                mst=$vals["mst"]
                pbanDVu=$vals["pbanDVu"]
                pbanTKhaiXML=$vals["pbanTKhaiXML"]
                ngayLapTKhai=$vals["ngayLapTKhai"]
                kyKKhai=$vals["kyKKhai"]
                kieuKy=$vals["kieuKy"]
                maTKhai=$vals["maTKhai"]
                tenCQTNoiNop=$vals["tenCQTNoiNop"]
                ds_DigestValue=$vals["ds_DigestValue"]
                ds_X509SubjectName=$vals["ds_X509SubjectName"]
            }
        }

        $byName = $rows | Where-Object { $_.Company -eq $c } | Group-Object Name
        foreach ($g in $byName) {
            $r = $g.Group | Where-Object Type -eq "REAL"
            $k = $g.Group | Where-Object Type -eq "FAKE"
            if ($r.Count -eq 1 -and $k.Count -eq 1) {
                $fields = @("mst","pbanDVu","pbanTKhaiXML","ngayLapTKhai","kyKKhai","tenCQTNoiNop","ds_DigestValue","ds_X509SubjectName")
                $diffs = @()
                foreach ($fld in $fields) { if ($r[0].$fld -ne $k[0].$fld) { $diffs += $fld } }
                $pairs += [pscustomobject]@{ Company=$c; Name=$g.Name; Recommend=($diffs -join ", ") }
            }
        }
    }

    $out = @{ rows = $rows; pairs = $pairs; generatedAt = (Get-Date).ToString("s") }
    $json = $out | ConvertTo-Json -Depth 6
    $outFile = Join-Path -Path $reportDir -ChildPath "xml_diff.json"
    $json | Out-File -FilePath $outFile -Encoding utf8

    Write-Output ('[INFO] Rows parsed: ' + ($rows | Measure-Object | Select-Object -ExpandProperty Count))
    Write-Output ('[INFO] Pairs suggested: ' + ($pairs | Measure-Object | Select-Object -ExpandProperty Count))
    Write-Output ('=== REPORT WRITTEN: ' + $outFile + ' ===')
    if ($rows.Count -gt 0) {
        Write-Output '=== SUMMARY ==='
        $rows | Sort-Object Company, Name, Type | Format-Table Company,Type,Name,Size,LastWrite -AutoSize | Out-String -Width 4096 | Write-Output
        Write-Output '=== PAIR RECOMMENDATIONS (REAL vs FAKE) ==='
        $pairs | Sort-Object Company, Name | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output
    } else {
        Write-Warning 'No XML parsed. Please check files and format.'
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}


