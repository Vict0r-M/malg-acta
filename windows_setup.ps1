# Set up of the development environment for the Malg-ACTA project:

# Set strict mode and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== Malg-ACTA Setup Script for Windows ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tested and confirmed working with:" -ForegroundColor Yellow
Write-Host "  - Python 3.13.3"
Write-Host "  - OpenJDK 21.0.6 (Temurin)"
Write-Host "  - javac 21.0.6"
Write-Host "  - Apache Maven 3.9.10"
Write-Host ""
Write-Host "Note: All receipt generation (PDF and Excel) should work without issues on Windows." -ForegroundColor Green
Write-Host ""
Write-Host "Setting up development environment..." -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to display error and exit
function Exit-WithError {
    param([string]$Message)
    Write-Host ""
    Write-Host "=== Setup Failed! ===" -ForegroundColor Red
    Write-Host $Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the project root:
if (-not (Test-Path "main.py") -or -not (Test-Path "requirements.txt")) {
    Exit-WithError "Please run this script from the malg-acta project root directory!`nExpected files: main.py, requirements.txt!"
}
Write-Host "Confirmed: Running from malg-acta project root directory." -ForegroundColor Green

# Check for required tools:
Write-Host ""
Write-Host "Checking for required tools..." -ForegroundColor Yellow

# Check Python 3:
if (-not (Test-Command "python")) {
    Exit-WithError "Python is not installed or not in PATH!`nPlease install Python 3.13+ from https://python.org"
}
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to get Python version!"
}

# Check Java:
if (-not (Test-Command "java")) {
    Exit-WithError "Java is not installed or not in PATH!`nPlease install OpenJDK 21+ from https://adoptium.net"
}
try {
    $javaVersion = & java -version 2>&1 | Select-String "openjdk version" | ForEach-Object { $_.ToString().Split('"')[1] }
    Write-Host "✓ Java found: OpenJDK $javaVersion." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to get Java version!"
}

# Check javac:
if (-not (Test-Command "javac")) {
    Exit-WithError "javac (Java compiler) is not installed or not in PATH!`nPlease install JDK (not just JRE) from https://adoptium.net"
}
try {
    $javacVersion = & javac -version 2>&1 | ForEach-Object { $_.ToString().Split(' ')[1] }
    Write-Host "✓ javac found: $javacVersion." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to get javac version!"
}

# Check Maven:
if (-not (Test-Command "mvn")) {
    Exit-WithError "Maven is not installed or not in PATH!`nPlease install Maven from https://maven.apache.org/download.cgi"
}
try {
    $mavenVersion = & mvn --version 2>&1 | Select-String "Apache Maven" | ForEach-Object { $_.ToString().Split(' ')[2] }
    Write-Host "✓ Maven found: Apache Maven $mavenVersion." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to get Maven version!"
}

Write-Host ""

# Step 1: Create Python virtual environment
Write-Host "Step 1: Creating Python virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, removing old one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

try {
    & python -m venv venv
    Write-Host "✓ Virtual environment created." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to create virtual environment!"
}

# Step 2: Activate virtual environment and install requirements
Write-Host "Step 2: Installing Python dependencies..." -ForegroundColor Cyan
try {
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip first
    & python -m pip install --upgrade pip
    
    # Install requirements
    & pip install -r requirements.txt
    Write-Host "✓ Python dependencies installed." -ForegroundColor Green
}
catch {
    Exit-WithError "Failed to install Python dependencies!"
}

# Step 3: Build GUI Java application
Write-Host "Step 3: Building GUI Java application..." -ForegroundColor Cyan
Push-Location "app_modules\input\gui\gui-app"

if (-not (Test-Path "pom.xml")) {
    Pop-Location
    Exit-WithError "pom.xml not found in GUI app directory!"
}

try {
    & mvn clean package
    Write-Host "✓ GUI application built successfully." -ForegroundColor Green
}
catch {
    Pop-Location
    Exit-WithError "GUI application build failed!"
}

# Step 4: Build CLI Java application
Write-Host "Step 4: Building CLI Java application..." -ForegroundColor Cyan
Set-Location "..\..\..\cli\cli-app"

if (-not (Test-Path "pom.xml")) {
    Pop-Location
    Exit-WithError "pom.xml not found in CLI app directory!"
}

try {
    & mvn clean package
    Write-Host "✓ CLI application built successfully." -ForegroundColor Green
}
catch {
    Pop-Location
    Exit-WithError "CLI application build failed!"
}

# Step 5: Compile Excel generation Java files
Write-Host "Step 5: Compiling Excel generation Java files..." -ForegroundColor Cyan
Set-Location "..\..\..\output\receipt_generation\excel_generation"

if (-not (Test-Path "lib")) {
    Pop-Location
    Exit-WithError "lib directory not found in excel_generation!`nPlease ensure Apache POI JAR files are in the lib\ directory!"
}

$javaFiles = Get-ChildItem -Name "*.java" -ErrorAction SilentlyContinue
if (-not $javaFiles) {
    Pop-Location
    Exit-WithError "No Java files found in excel_generation directory!"
}

try {
    & javac -cp "lib\*" *.java
    Write-Host "✓ Excel generation Java files compiled successfully." -ForegroundColor Green
}
catch {
    Pop-Location
    Exit-WithError "Excel generation Java compilation failed!"
}

# Step 6: Return to project root
Write-Host "Step 6: Returning to project root..." -ForegroundColor Cyan
Pop-Location

if (-not (Test-Path "main.py")) {
    Exit-WithError "Failed to return to project root!"
}
Write-Host "✓ Returned to project root." -ForegroundColor Green

# Step 7: Create data directories if they don't exist
Write-Host "Step 7: Creating data directories..." -ForegroundColor Cyan

$directories = @(
    "data\receipts\pdf_receipts",
    "data\receipts\excel_receipts", 
    "logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Create initial data files if they don't exist
$dataFiles = @{
    "data\clients.json" = "[]"
    "data\concrete_classes.json" = "[]"
}

foreach ($file in $dataFiles.Keys) {
    if (-not (Test-Path $file)) {
        Set-Content -Path $file -Value $dataFiles[$file]
        Write-Host "✓ Created empty $(Split-Path $file -Leaf)." -ForegroundColor Green
    }
}

Write-Host "✓ Data directories and files ready." -ForegroundColor Green

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "1. Activate the virtual environment: venv\Scripts\Activate.ps1"
Write-Host "2. Run the application: python main.py"
Write-Host ""
Write-Host "Optional: Run with custom config: python main.py --config configs\app_config.yaml"
Write-Host ""
Read-Host "Press Enter to exit"