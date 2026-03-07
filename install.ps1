# MasterMind Framework - Windows Installer
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan @"

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MasterMind Framework - Installer                     ║
║     AI-powered expert brains for software development     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

"@

# Configuration
$REPO_URL = "https://github.com/rap77/mastermind-framework.git"
$INSTALL_DIR = "$env:USERPROFILE\.mastermind-framework"
$BIN_DIR = "$env:USERPROFILE\.local\bin"

function Test-CommandExists {
    param([string]$Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
        return $false
    } catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput Blue "➜ $Message"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput Green "✓ $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput Yellow "⚠ $Message"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput Red "✗ $Message"
}

# Step 1: Check dependencies
Write-Step "Checking system dependencies..."

$missingDeps = @()

if (-not (Test-CommandExists "git")) {
    $missingDeps += "git"
}

if ($missingDeps.Count -gt 0) {
    Write-Error "Missing required dependencies: $($missingDeps -join ', ')"
    Write-Output ""
    Write-Output "Please install them first:"
    Write-Output "  1. Install Git for Windows: https://git-scm.com/download/win"
    Write-Output "  2. Restart PowerShell and run this script again"
    exit 1
}

Write-Success "Dependencies found"

# Step 2: Install uv
Write-Step "Installing uv package manager..."

if (Test-CommandExists "uv") {
    Write-Success "uv already installed"
} else {
    Write-Step "Downloading uv installer..."
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Success "uv installed"

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + $env:Path
}

# Verify uv
if (-not (Test-CommandExists "uv")) {
    Write-Error "uv not found in PATH"
    Write-Output ""
    Write-Output "Close and restart PowerShell to apply PATH changes"
    exit 1
}

# Step 3: Clone or update repository
Write-Step "Setting up MasterMind Framework..."

if (Test-Path $INSTALL_DIR) {
    Write-Step "Updating existing installation..."
    Set-Location $INSTALL_DIR
    git pull origin master
    Write-Success "Repository updated"
} else {
    Write-Step "Cloning repository..."
    git clone $REPO_URL $INSTALL_DIR
    Write-Success "Repository cloned"
}

# Step 4: Install Python 3.14+
Write-Step "Ensuring Python 3.14+ availability..."

$pythonVersion = uv python find 3.14 2>$null

if (-not $pythonVersion) {
    Write-Step "Python 3.14 not found, installing via uv..."
    uv python install 3.14
    $pythonVersion = uv python find 3.14
}

Write-Success "Python 3.14 ready: $pythonVersion"

# Step 5: Install mastermind globally
Write-Step "Installing MasterMind Framework globally..."

Set-Location $INSTALL_DIR
uv pip install --global -e .

Write-Success "Installation complete"

# Step 6: Get uv global bin location and add to PATH
Write-Step "Configuring PATH..."

# Get uv global bin directory
$uvGlobalBin = "$env:APPDATA\uv\bin"

# Check if uv global bin is in PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$uvGlobalBin*") {
    Write-Warning "Adding to user PATH..."

    $newPath = "$uvGlobalBin;$currentPath"
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")

    Write-Success "Added to PATH (restart PowerShell to apply)"
} else {
    Write-Success "Already in PATH"
}

# Step 7: Verify installation
Write-Output ""
Write-Success "Installation complete!"
Write-Output ""

Write-ColorOutput Cyan "Available commands:"
Write-Output "  mm info              - Show framework info"
Write-Output "  mm install status     - Check installation status"
Write-Output "  mm brain status       - Check brain status"
Write-Output ""

Write-ColorOutput Cyan "To use in a project:"
Write-Output "  cd C:\path\to\your-project"
Write-Output "  mm install init"
Write-Output ""

if (-not (Test-CommandExists "mm")) {
    Write-Warning "Restart PowerShell to use 'mm' command"
}

Write-ColorOutput Green "Happy coding! 🚀"
