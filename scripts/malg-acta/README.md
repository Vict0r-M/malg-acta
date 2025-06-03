# Malg-ACTA Materials Testing System

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
