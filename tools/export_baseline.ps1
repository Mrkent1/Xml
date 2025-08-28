param(
    [string]$Root
)

$ErrorActionPreference = "Stop"

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }

$reportPath = Join-Path -Path $Root -ChildPath "reports\xml_diff.json"
if (-not (Test-Path -Path $reportPath)) { Write-Error "Report not found: $reportPath. Run tools/xml_inspect.ps1 first."; exit 1 }

$report = Get-Content -Path $reportPath -Raw | ConvertFrom-Json

$coreFields = @("mst","pbanDVu","pbanTKhaiXML","ngayLapTKhai","kyKKhai","kieuKy","maTKhai","tenCQTNoiNop","ds_DigestValue","ds_X509SubjectName")

$baseline = @()
foreach ($row in $report.rows) {
    if ($row.Type -ne "REAL") { continue }
    $item = [ordered]@{}
    $item.Company = $row.Company
    $item.Name = $row.Name
    $item.Path = $row.Path
    $item.Fingerprint = $row.Fingerprint
    foreach ($k in $coreFields) { $item[$k] = $row.$k }
    $baseline += [pscustomobject]$item
}

$outDir = Join-Path -Path $Root -ChildPath "reports"
if (-not (Test-Path -Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$outFile = Join-Path -Path $outDir -ChildPath "baseline_real.json"
$baseline | ConvertTo-Json -Depth 6 | Out-File -FilePath $outFile -Encoding utf8

Write-Output ("Baseline written: " + $outFile)

