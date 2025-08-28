param(
    [string]$Root,
    [string]$ConfigPath
)

$ErrorActionPreference = "Stop"

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
if (-not $ConfigPath) { $ConfigPath = Join-Path -Path $PSScriptRoot -ChildPath "config.json" }

if (-not (Test-Path -Path $ConfigPath)) { Write-Error "Không tìm thấy config: $ConfigPath"; exit 1 }
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json

$reportPath = Join-Path -Path $Root -ChildPath "reports\xml_diff.json"
if (-not (Test-Path -Path $reportPath)) { Write-Error "Không tìm thấy báo cáo: $reportPath. Hãy chạy tools/xml_inspect.ps1 trước."; exit 1 }
$report = Get-Content -Path $reportPath -Raw | ConvertFrom-Json

# Baseline fingerprint từ REAL (nếu có)
$baselinePath = Join-Path -Path $Root -ChildPath "reports\baseline_real.json"
$baseline = $null
if (Test-Path -Path $baselinePath) {
    $baseline = Get-Content -Path $baselinePath -Raw | ConvertFrom-Json
}

# Tập tên file có khác biệt theo cặp REAL/FAKE (Recommend != empty)
$mismatch = @{}
foreach ($p in $report.pairs) {
    if ($p.Recommend -and $p.Recommend.Trim().Length -gt 0) {
        $key = "$($p.Company)|$($p.Name)"
        $mismatch[$key] = $true
    }
}

$dryRun = $true
if ($config.policy -and $config.policy.dryRun -ne $null) { $dryRun = [bool]$config.policy.dryRun }
$enforceOnFake = $false
if ($config.policy -and $config.policy.enforceOnFake -ne $null) { $enforceOnFake = [bool]$config.policy.enforceOnFake }
$baseUrl = $config.policy.syncthing.baseUrl
$apiKey  = $config.policy.syncthing.apiKey
$folderId = $config.policy.syncthing.folderId
$folderRoot = $config.policy.syncthing.folderRoot

if (-not $folderRoot -or $folderRoot.Trim().Length -eq 0) { $folderRoot = $Root }

$plan = @()
$denied = @()
foreach ($row in $report.rows) {
    if ($row.Type -ne "FAKE") { continue }
    $key = "$($row.Company)|$($row.Name)"
    $isPlanned = $false

    # 1) Nếu có pairs mismatch theo tên file → thêm vào kế hoạch
    if ($mismatch.ContainsKey($key)) {
        $isPlanned = $true
    }

    # 2) Fallback: nếu nằm trong thư mục 'fake' và fingerprint KHÔNG khớp với bất kỳ REAL cùng công ty
    if (-not $isPlanned -and $baseline) {
        $companyBaseline = $baseline | Where-Object { $_.Company -eq $row.Company }
        $match = $false
        foreach ($b in $companyBaseline) {
            if ($b.Fingerprint -eq $row.Fingerprint) { $match = $true; break }
        }
        if (-not $match) { $isPlanned = $true }
    }

    # 3) Option A tuyệt đối: nếu enforceOnFake=true, bất kỳ file trong fake/ đều vào kế hoạch
    if (-not $isPlanned -and $enforceOnFake) { $isPlanned = $true }

    if (-not $isPlanned) { continue }

    # Tính relative path theo folderRoot (dùng regex để bỏ \ hoặc / đầu chuỗi)
    $rel = $row.Path
    if ($rel -like "$folderRoot*") { $rel = $row.Path.Substring($folderRoot.Length) -replace '^[\\/]+' , '' }

    $reason = "Fingerprint not in REAL baseline"
    if ($mismatch.ContainsKey($key)) { $reason = "Pairs mismatch (fields)" }
    elseif ($enforceOnFake) { $reason = "Policy A: enforce revert for any file in fake/" }

    $plan += [pscustomobject]@{
        Company = $row.Company
        Name = $row.Name
        Path = $row.Path
        RelativePath = $rel
        Action = "REVERT"
        Reason = $reason
    }
}

if ($plan.Count -eq 0) { Write-Output "Không có mục nào cần revert theo tiêu chí hiện tại."; exit 0 }

Write-Output "=== KẾ HOẠCH REVERT (dryRun=$dryRun) ==="
$plan | Sort-Object Company, Name | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output

if ($dryRun) { exit 0 }

# Thực thi gọi Syncthing REST
if (-not $baseUrl -or -not $apiKey -or -not $folderId) {
    Write-Error "Thiếu cấu hình Syncthing (baseUrl/apiKey/folderId). Không thể thực thi revert."
    exit 2
}

foreach ($p in $plan) {
    $uri = "$baseUrl/rest/db/revert?folder=$folderId&path=$([uri]::EscapeDataString($p.RelativePath))"
    try {
        Invoke-RestMethod -Method Post -Uri $uri -Headers @{ 'X-API-Key' = $apiKey } | Out-Null
        Write-Output "ĐÃ REVERT: $($p.RelativePath)"
    } catch {
        Write-Warning "Lỗi revert $($p.RelativePath): $($_.Exception.Message)"
    }
}
