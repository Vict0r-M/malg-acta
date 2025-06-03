"""Java bridge for communication with GUI/CLI components"""

#%% Dependencies:

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

#%% Main Class:

class JavaBridge:
    """
    Bridge for communicating with Java GUI and CLI components.
    
    Handles input/output exchange through JSON files and process execution.
    Provides methods to launch Java components and exchange data.
    """
    
    def __init__(self, ctx: Any) -> None:
        """Initialize Java bridge with context"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        
        # File paths for data exchange:
        self.input_file = Path(self.config.data_paths.input_exchange)
        self.output_file = Path(self.config.data_paths.output_exchange)
        
        # Ensure data exchange directory exists:
        self.input_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def launch_gui(self) -> bool:
        """
        Launch Java GUI application.
        
        Returns:
            True if GUI launched successfully, False otherwise
        """
        
        try:
            gui_jar = Path(self.config.java_integration.gui_jar_path)
            
            if not gui_jar.exists():
                self.logger.error(f"GUI JAR file not found: {gui_jar}")
                return False
            
            # First, ensure any old output.json is deleted
            output_file = Path("output.json")
            if output_file.exists():
                output_file.unlink()
                self.logger.info("Deleted existing output.json file")
            
            self.logger.info("Launching Java GUI...")
            
            # Launch GUI with proper JavaFX parameters
            process = subprocess.Popen([
                "java", 
                "--module-path", "javafx\\lib",
                "--add-modules", "javafx.controls,javafx.fxml,javafx.base",
                "-Djava.awt.headless=false",
                "-cp", f"lib\\*;{str(gui_jar)}", 
                self.config.java_integration.gui_class
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.logger.info("Java GUI launched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch GUI: {str(e)}")
            return False
    
    def launch_cli(self) -> bool:
        """
        Launch Java CLI application.
        
        Returns:
            True if CLI launched successfully, False otherwise
        """
        
        try:
            gui_jar = Path(self.config.java_integration.gui_jar_path)
            
            if not gui_jar.exists():
                self.logger.error(f"GUI JAR file not found: {gui_jar}")
                return False
            
            self.logger.info("Launching Java CLI...")
            
            # Launch CLI and wait for completion:
            result = subprocess.run([
                "java", "-cp", str(gui_jar),
                self.config.java_integration.cli_class
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Java CLI completed successfully")
                return True
            else:
                self.logger.error(f"CLI failed with error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to launch CLI: {str(e)}")
            return False
    
    def read_input_data(self) -> Optional[Dict[str, Any]]:
        """
        Read input data from Java application.
        
        Returns:
            Dictionary with input data or None if failed
        """
        
        try:
            if not self.input_file.exists():
                self.logger.warning(f"Input file not found: {self.input_file}")
                return None
            
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info("Successfully read input data from Java")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in input file: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read input data: {str(e)}")
            return None
    
    def write_output_data(self, data: Dict[str, Any]) -> bool:
        """
        Write output data for Java application.
        
        Args:
            data: Dictionary with output data
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Successfully wrote output data for Java")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write output data: {str(e)}")
            return False
    
    def convert_java_input_to_input_data(self, java_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Java application input format to InputData format.
        
        Args:
            java_data: Raw data from Java application
            
        Returns:
            Data formatted for InputData model
        """
        
        # Map Java field names to our InputData field names:
        protocol_mapping = {
            "Rezistență la Compresiune Cuburi": "cube_compression_testing",
            "Gelivitate Cuburi": "cube_frost_testing", 
            "Rezistență la Compresiune Prisme": "beam_compression_testing",
            "Rezistență la Încovoiere Prisme": "beam_flexural_testing"
        }
        
        try:
            converted = {
                "protocol": protocol_mapping.get(java_data.get("protocol", ""), "cube_compression_testing"),
                "client": java_data.get("client", java_data.get("beneficiar", "")),
                "concrete_class": java_data.get("concrete_class", java_data.get("concrete class", java_data.get("clasa_betonului", java_data.get("clasa", "")))),
                "sampling_date": java_data.get("sampling_date", java_data.get("probe_date", "")),
                "testing_date": java_data.get("testing_date", java_data.get("try_date", "")),
                "sampling_location": java_data.get("sampling_location", "sampling location"),  # Use default if empty
                "project_name": java_data.get("project_name", "project name"),  # Use default if empty
                "set_id": java_data.get("set_id", java_data.get("internal_code", "")),
                "set_size": java_data.get("set_size", java_data.get("numar_teste", 3)),
                "should_print": java_data.get("should_print", True),
                "output_format": ["PDF", "Excel"]  # Default formats
            }
            
            # Ensure sampling_location and project_name are not empty strings
            if not converted["sampling_location"].strip():
                converted["sampling_location"] = "sampling location"
            if not converted["project_name"].strip():
                converted["project_name"] = "project name"
            
            self.logger.info("Successfully converted Java input to InputData format")
            return converted
            
        except Exception as e:
            self.logger.error(f"Failed to convert Java input: {str(e)}")
            return {}
    
    def generate_excel_output(self, output_data: Dict[str, Any]) -> bool:
        """
        Generate Excel output using Java component.
        
        Args:
            output_data: Processed test data
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Create CSV data for Java Excel generator:
            csv_data = self._create_csv_data(output_data)
            csv_file = Path("data/temp_excel_data.csv")
            
            # Ensure data directory exists:
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            # Navigate to scripts directory and compile Java file:
            java_file = Path("scripts/CubeCompression.java")
            
            if java_file.exists():
                # Use Windows-compatible classpath syntax with absolute paths:
                lib_path = Path("lib").resolve()
                classpath = f"{lib_path}\\*"
                
                self.logger.info(f"Compiling Java with classpath: {classpath}")
                
                # Compile Java file with correct Windows classpath:
                compile_result = subprocess.run([
                    "javac", "-cp", classpath, str(java_file.resolve())
                ], capture_output=True, text=True, cwd=Path.cwd())
                
                if compile_result.returncode == 0:
                    self.logger.info("Java compilation successful")
                    
                    # Run Java program with same classpath:
                    scripts_dir = Path("scripts").resolve()
                    run_classpath = f"{classpath};{scripts_dir}"
                    
                    run_result = subprocess.run([
                        "java", "-cp", run_classpath, "CubeCompression"
                    ], capture_output=True, text=True, cwd=scripts_dir)
                    
                    if run_result.returncode == 0:
                        self.logger.info("Excel file generated successfully")
                        return True
                    else:
                        self.logger.error(f"Java execution failed: {run_result.stderr}")
                        self.logger.error(f"Java stdout: {run_result.stdout}")
                else:
                    self.logger.error(f"Java compilation failed: {compile_result.stderr}")
                    self.logger.error(f"Compilation stdout: {compile_result.stdout}")
            else:
                self.logger.error(f"Java file not found: {java_file}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to generate Excel output: {str(e)}")
            return False
    
    def generate_pdf_output(self, output_data: Dict[str, Any]) -> bool:
        """
        Generate PDF output using Python script.
        
        Args:
            output_data: Processed test data
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Create JSON data for PDF generator:
            pdf_data = self._create_pdf_data(output_data)
            
            # Write temporary JSON file:
            temp_json = Path("data/temp_pdf_data.json")
            temp_json.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_json, 'w', encoding='utf-8') as f:
                json.dump(pdf_data, f, indent=2, ensure_ascii=False)
            
            # Run PDF generation script:
            pdf_script = Path(self.config.output_generation.pdf_script)
            
            if pdf_script.exists():
                result = subprocess.run([
                    sys.executable, str(pdf_script), str(temp_json)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("PDF file generated successfully")
                    return True
                else:
                    self.logger.error(f"PDF generation failed: {result.stderr}")
            else:
                self.logger.error(f"PDF script not found: {pdf_script}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to generate PDF output: {str(e)}")
            return False
    
    def _create_csv_data(self, output_data: Dict[str, Any]) -> str:
        """Create CSV data for Java Excel generator"""
        
        input_data = output_data["input_data"]
        specimens = output_data["specimens"]
        
        lines = [
            f"Indicativ,{input_data['set_id']}",
            f"Data Confectionarii,{input_data['sampling_date']}", 
            f"Data Incercarii,{input_data['testing_date']}"
        ]
        
        # Weight data:
        weight_line = "Greutate"
        for specimen in specimens:
            if specimen.get("scale_data"):
                weight_line += f",{specimen['scale_data']['mass']}"
            else:
                weight_line += ",0"
        lines.append(weight_line)
        
        # Force data:
        force_line = "kN"
        for specimen in specimens:
            if specimen.get("press_data"):
                # Convert N to kN:
                force_kn = specimen['press_data']['load'] / 1000.0
                force_line += f",{force_kn:.1f}"
            else:
                force_line += ",0"
        lines.append(force_line)
        
        return "\n".join(lines)
    
    def _create_pdf_data(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON data for PDF generator"""
        
        input_data = output_data["input_data"]
        specimens = output_data["specimens"]
        
        # Convert to format expected by PDF generator:
        pdf_data = {
            "probe_date": input_data["sampling_date"],
            "beneficiar": input_data["client"],
            "clasa_betonului": input_data["concrete_class"],
            "numar_teste": len(specimens),
            "internal_code": input_data["set_id"],
            "try_date": input_data["testing_date"],
            "tests": []
        }
        
        for specimen in specimens:
            test_data = {}
            
            if specimen.get("scale_data"):
                mass_kg = specimen["scale_data"]["mass"]
                test_data["scale_data"] = f"{mass_kg * 1000:.1f} g H"
            
            if specimen.get("press_data"):
                load_n = specimen["press_data"]["load"]
                strength = specimen["press_data"]["strength"]
                test_data["compression_data"] = {
                    "kN": f"{load_n / 1000.0:08.1f}",
                    "MPa": f"{strength:07.2f}"
                }
            
            pdf_data["tests"].append(test_data)
        
        return pdf_data

#%%