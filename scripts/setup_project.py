#!/usr/bin/env python3
"""
Setup script to create the complete project structure for Malg-ACTA demo
"""

import os
from pathlib import Path

def create_project_structure():
    """Create the complete directory structure"""
    
    # Project root
    root = Path("malg-acta")
    
    # Directory structure
    directories = [
        # Core directories
        "app_modules",
        "app_modules/utils",
        "app_modules/core", 
        "app_modules/models",
        "app_modules/protocols",
        "app_modules/bridges",
        "app_modules/data_storage",
        "app_modules/plugins",
        "app_modules/plugins/input",
        "app_modules/plugins/acquisition", 
        "app_modules/plugins/output",
        
        # Configuration and data
        "configs",
        "data",
        "data/reports",
        "data/reports/excel",
        "data/reports/pdf",
        "logs",
        
        # Scripts and examples
        "scripts",
        "examples",
        
        # Java components
        "gui-app",
        "gui-app/src",
        "gui-app/src/main",
        "gui-app/src/main/java",
        "gui-app/src/main/java/com",
        "gui-app/src/main/java/com/malg_acta",
        "gui-app/src/main/java/com/malg_acta/gui_app",
        "gui-app/target",
        "lib"
    ]
    
    # Create directories
    for directory in directories:
        dir_path = root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create __init__.py files for Python packages
    python_packages = [
        "app_modules",
        "app_modules/utils",
        "app_modules/core",
        "app_modules/models", 
        "app_modules/protocols",
        "app_modules/bridges",
        "app_modules/data_storage",
        "app_modules/plugins",
        "app_modules/plugins/input",
        "app_modules/plugins/acquisition",
        "app_modules/plugins/output"
    ]
    
    for package in python_packages:
        init_file = root / package / "__init__.py"
        init_file.touch()
        print(f"Created package file: {init_file}")
    
    # Create requirements.txt
    requirements = root / "requirements.txt"
    with open(requirements, 'w') as f:
        f.write("""# Malg-ACTA Requirements
pydantic>=2.0.0
python-box>=7.0.0
PyYAML>=6.0.0
weasyprint>=60.0
openpyxl>=3.1.0
""")
    print(f"Created requirements file: {requirements}")
    
    # Create .gitignore
    gitignore = root / ".gitignore"
    with open(gitignore, 'w') as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Generated files
data/reports/
data/temp_*
output.json
formular.json
*.xlsx
*.pdf

# Java
*.class
gui-app/target/
*.jar
!lib/*.jar

# OS
.DS_Store
Thumbs.db
""")
    print(f"Created .gitignore: {gitignore}")
    
    # Create README.md
    readme = root / "README.md"
    with open(readme, 'w') as f:
        f.write("""# Malg-ACTA Materials Testing System

Automated construction testing and analysis system for concrete specimen testing.

## Features

- Multiple testing protocols (cube compression, cube frost, beam compression, beam flexural)
- GUI and CLI input methods
- Excel and PDF report generation
- Pydantic data validation
- Configurable units and formatting

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Compile Java components (if using GUI):
   ```bash
   cd gui-app
   javac -cp ".:../lib/*" src/main/java/com/malg_acta/gui_app/*.java
   ```

3. Run demo:
   ```bash
   python main.py --input cli
   # or
   python main.py --input gui
   ```

## Project Structure

- `app_modules/` - Python backend modules
- `gui-app/` - Java GUI components  
- `configs/` - Configuration files
- `data/` - Data storage and reports
- `scripts/` - Utility scripts
- `logs/` - Application logs

## Demo Data

The system includes demo data for all protocols to simulate device measurements without physical hardware.
""")
    print(f"Created README: {readme}")
    
    print(f"\n✅ Project structure created successfully in: {root.absolute()}")
    print("\nNext steps:")
    print("1. Copy the Python files to their respective directories")
    print("2. Copy the Java files to gui-app/src/main/java/com/malg_acta/gui_app/")
    print("3. Copy the configuration and demo data files")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Run: python main.py --input cli")

if __name__ == "__main__":
    create_project_structure()