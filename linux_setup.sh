#!/bin/bash

# Set up of the development environment for the Malg-ACTA project:

set -e  # Exit on any error

echo "=== Malg-ACTA Setup Script for Linux ==="
echo
echo "Tested and confirmed working with:"
echo "  - Python 3.13.3"
echo "  - OpenJDK 21.0.6 (Temurin)"
echo "  - javac 21.0.6"
echo "  - Apache Maven 3.9.10"
echo
echo "Note: PDF receipt generation may not work on Linux due to ReportLab font dependencies."
echo "Excel receipts should work without issues."
echo
echo "Setting up development environment..."
echo

# Check if we're in the project root:
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the malg-acta project root directory!"
    echo "Expected files: main.py, requirements.txt!"
    exit 1
fi

# Check for required tools:
echo "Checking for required tools..."

# Check Python 3:
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH!"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)."

# Check Java:
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH!"
    exit 1
fi
echo "✓ Java found: $(java -version 2>&1 | head -n 1)."

# Check javac:
if ! command -v javac &> /dev/null; then
    echo "Error: javac (Java compiler) is not installed or not in PATH!"
    exit 1
fi
echo "✓ javac found: $(javac -version 2>&1)"

# Check Maven:
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed or not in PATH!"
    echo "Please install Maven: sudo apt install maven (Ubuntu/Debian) or equivalent!"
    exit 1
fi
echo "✓ Maven found: $(mvn -version | head -n 1)."

echo

# Create Python virtual environment:
echo "Step 1: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✓ Virtual environment created."

# Activate virtual environment and install requirements:
echo "Step 2: Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip first:
pip install --upgrade pip

# Install requirements:
pip install -r requirements.txt
echo "✓ Python dependencies installed."

# Build GUI Java application:
echo "Step 3: Building GUI Java application..."
cd app_modules/input/gui/gui-app

# Check if pom.xml exists:
if [ ! -f "pom.xml" ]; then
    echo "Error: pom.xml not found in GUI app directory!"
    exit 1
fi

mvn clean package
if [ $? -ne 0 ]; then
    echo "Error: GUI application build failed!"
    exit 1
fi
echo "✓ GUI application built successfully."

# Build CLI Java application:
echo "Step 4: Building CLI Java application..."
cd ../../cli/cli-app

# Check if pom.xml exists:
if [ ! -f "pom.xml" ]; then
    echo "Error: pom.xml not found in CLI app directory!"
    exit 1
fi

mvn clean package
if [ $? -ne 0 ]; then
    echo "Error: CLI application build failed!"
    exit 1
fi
echo "✓ CLI application built successfully."

# Compile Excel generation Java files:
echo "Step 5: Compiling Excel generation Java files..."
cd ../../../output/receipt_generation/excel_generation

# Check if lib directory exists:
if [ ! -d "lib" ]; then
    echo "Error: lib directory not found in excel_generation!"
    echo "Please ensure Apache POI JAR files are in the lib/ directory!"
    exit 1
fi

# Check if Java files exist:
if ! ls *.java &> /dev/null; then
    echo "Error: No Java files found in excel_generation directory!"
    exit 1
fi

# Compile Java files:
javac -cp "lib/*" *.java
if [ $? -ne 0 ]; then
    echo "Error: Excel generation Java compilation failed!"
    exit 1
fi
echo "✓ Excel generation Java files compiled successfully."

# Return to project root:
echo "Step 6: Returning to project root..."
cd ../../../..

# Verify we're back in the right place:
if [ ! -f "main.py" ]; then
    echo "Error: Failed to return to project root!"
    exit 1
fi

echo "✓ Returned to project root."

# Create data directories if they don't exist:
echo "Step 7: Creating data directories..."
mkdir -p data/receipts/pdf_receipts
mkdir -p data/receipts/excel_receipts
mkdir -p logs

# Create initial data files if they don't exist:
if [ ! -f "data/clients.json" ]; then
    echo '[]' > data/clients.json
    echo "✓ Created empty clients.json."
fi

if [ ! -f "data/concrete_classes.json" ]; then
    echo '[]' > data/concrete_classes.json
    echo "✓ Created empty concrete_classes.json."
fi

echo "✓ Data directories and files ready."

echo
echo "=== Setup Complete! ==="
echo
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate;"
echo "2. Run the application: python main.py."
echo
echo "Optional: Run with custom config: python main.py --config configs/app_config.yaml."
echo