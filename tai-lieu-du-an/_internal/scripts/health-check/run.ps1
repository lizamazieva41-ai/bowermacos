# run.ps1 — BrowserManager Health Check Wrapper (PowerShell)
# Usage: .\run.ps1 [-Port 40000] [-Token "your-token"] [-Quick] [-Json]
# Requires: Node.js >=18 in PATH

[CmdletBinding()]
param(
    [int]$Port = 40000,
    [string]$Token = "",
    [switch]$Quick,
    [switch]$Json,
    [int]$TimeoutMs = 30000
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot

# ── Check Node.js ──────────────────────────────────────────────────────────────
try {
    $nodeVersion = (node --version 2>$null)
    $nodeMajor = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
    if ($nodeMajor -lt 18) {
        Write-Error "Node.js >= 18 required. Found: $nodeVersion"
        exit 2
    }
} catch {
    Write-Error "Node.js not found in PATH. Install from https://nodejs.org"
    exit 2
}

# ── Install dependencies if needed ─────────────────────────────────────────────
$packageJson = Join-Path $ScriptDir "package.json"
$nodeModules = Join-Path $ScriptDir "node_modules"

if (-not (Test-Path $nodeModules)) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    Push-Location $ScriptDir
    npm install --quiet
    Pop-Location
}

# ── Token resolution ─────────────────────────────────────────────────────────
if (-not $Token) {
    $Token = $env:BM_TOKEN
    if (-not $Token) {
        # Try to read from agent config file
        $configPath = Join-Path $env:APPDATA "BrowserManager\config.yaml"
        if (Test-Path $configPath) {
            $configContent = Get-Content $configPath -Raw
            if ($configContent -match 'api_token:\s*(.+)') {
                $Token = $Matches[1].Trim()
                Write-Host "Token loaded from config.yaml" -ForegroundColor Green
            }
        }
    }
}

if (-not $Token) {
    Write-Warning "No API token found. Set BM_TOKEN environment variable or use -Token parameter."
    Write-Warning "Example: .\run.ps1 -Token `"your-32-char-token-here`""
}

# ── Build arguments ──────────────────────────────────────────────────────────
$nodeArgs = @("health-check.js", "--port", $Port, "--timeout", $TimeoutMs)

if ($Token) {
    $nodeArgs += @("--token", $Token)
}
if ($Quick) {
    $nodeArgs += "--quick"
}
if ($Json) {
    $nodeArgs += "--json"
}

# ── Run ─────────────────────────────────────────────────────────────────────
Push-Location $ScriptDir
try {
    $env:BM_PORT = $Port
    node @nodeArgs
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

# ── Exit codes ───────────────────────────────────────────────────────────────
switch ($exitCode) {
    0 { Write-Host "" ; exit 0 }
    1 { Write-Host "One or more health checks failed." -ForegroundColor Red ; exit 1 }
    2 { Write-Host "Agent is not reachable at http://127.0.0.1:$Port" -ForegroundColor Red ; exit 2 }
    3 { Write-Host "Invalid or missing API token." -ForegroundColor Red ; exit 3 }
    default { exit $exitCode }
}
