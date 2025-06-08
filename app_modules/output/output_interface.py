import json
import os
import csv
import jpype
import jpype.imports
from jpype.types import *
from typing import Dict, List, Any, Optional
import logging
import glob

from app_modules.models.set_data import SetData
from app_modules.output.receipt_generation.pdf_generation import CubeCompression
from app_modules.output.receipt_generation.pdf_generation import BeamCompression
from app_modules.output.receipt_generation.pdf_generation import BeamFlexural

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputInterface:
    """
    Unified interface for generating concrete test reports in PDF or Excel format.
    Uses Python for PDF generation and Java (via JPype) for Excel generation.
    """
    
    def __init__(self, raw_data: SetData):

        self.jvm_started = False
        self.raw_data = raw_data
        self.output_format = raw_data.input_data.get("output_format")
        self.protocol = raw_data.input_data.get("protocol")
        
    def start_jvm(self):
        """Start the JVM for Java Excel generation if not already started."""
        if not jpype.isJVMStarted():
            try:
                # Add Apache POI jars to classpath
                lib_dir = os.path.abspath(r"receipt_generation\excel_generation\lib")  # Where your jars are stored
                jars = glob.glob(os.path.join(lib_dir, "*.jar"))
                classpath = [r"receipt_generation\excel_generation"] + jars
                
                jpype.startJVM(classpath=classpath)
                self.jvm_started = True
                logger.info("JVM started successfully")
            except Exception as e:
                logger.error(f"Failed to start JVM: {e}")
                raise
    
    def shutdown_jvm(self):
        """Shutdown the JVM."""
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            self.jvm_started = False
            logger.info("JVM shutdown")
    
    def process_test_data_for_pdf(self) -> Dict[str, Any]:
        """
        Process raw test data for PDF generation (Python version).
        
        Args:
            raw_data: Raw test data dictionary
            
        Returns:
            Processed data dictionary
        """
        tests = self.raw_data["tests"]
        weights = [round(float(test["scale_data"]) / 1000, 2) for test in tests]
        forces = [round(float(test["compression_data"]["kN"]) * 1000, 2) for test in tests]
        pressures = [round(float(test["compression_data"]["MPa"]), 2) for test in tests]
        cube_volume = 0.003375  # 150mm cube volume in m³
        densities = [round(weight / cube_volume, 2) for weight in weights]

        return {
            "weights": weights,
            "forces": forces,
            "pressures": pressures,
            "densities": densities,
            "averages": {
                "weight": round(sum(weights) / len(weights), 2),
                "force": round(sum(forces) / len(forces), 2),
                "pressure": round(sum(pressures) / len(pressures), 2),
                "density": round(sum(densities) / len(densities), 2),
            }
        }
    
    def create_csv_for_java(self, csv_filename: str = "press_data.csv"):
        """
        Create CSV file for Java Excel generator.
        
        Args:
            raw_data: Raw test data dictionary
            csv_filename: Output CSV filename
        """
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(["indicativ_serie", self.raw_data.input_data.get("set_id", "")])
                writer.writerow(["data_confectionarii", self.raw_data.input_data.get("sampling_date", "")])
                writer.writerow(["data_incercarii", self.raw_data.input_data.get("testing_date", "")])
                
                # Process test data
                tests = self.raw_data.input_data["tests"]
                weights = [round(float(test["scale_data"]) / 1000, 3) for test in tests]  # Convert to kg
                forces = [round(float(test["compression_data"]["kN"]) * 1000, 0) for test in tests]  # Convert to N
                
                # Write data rows
                writer.writerow(["greutate"] + weights)
                writer.writerow(["kN"] + forces)
                
            logger.info(f"CSV file created: {csv_filename}")
            
        except Exception as e:
            logger.error(f"Failed to create CSV file: {e}")
            raise
    
    def generate_pdf_report(self):
        """
        Generate PDF receipt using your existing Python code

        Args:
            receipt_data: JSON data for the receipt
            output_file: Output PDF file path

        Returns:
            bool: True if successful, False otherwise
        """
        try:

            if self.protocol == "Rezistență la Compresiune Cuburi" or self.protocol == "Gelivitate Cuburi":
                file = CubeCompression
            elif self.protocol == "Rezistență la Compresiune Prisme":
                file = BeamCompression
            elif self.protocol == "Rezistență la Încovoiere Prisme":
                file = BeamFlexural

            # Process the data using your existing function
            processed_data = file.process_test_data(self.raw_data.input_data)

            # Generate PDF using your existing function
            result_path = file.create_pdf_with_reportlab(self.raw_data.input_data, processed_data)

            # Move the generated file to the desired output location if different
            if result_path and os.path.exists(result_path):
                print(f"PDF generated successfully")
            else:
                raise FileNotFoundError("PDF generation completed but file not found")

        except ImportError as e:
            print(f"Could not import your PDF module: {str(e)}")
            print("Make sure your PDF generation module is in the Python path")
            raise

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise
    
    def generate_excel_report(self):
        """
        Generate Excel report using Java via JPype.
        
        Args:
            raw_data: Raw test data dictionary
            
        Returns:
            Path to generated Excel file
        """
        try:
            # Start JVM if not already started
            if not self.jvm_started:
                self.start_jvm()
            
            # Create CSV file for Java consumption
            csv_filename = "press_data.csv"
            self.create_csv_for_java(csv_filename)
            
            # Import and run Java class
            from java.lang import System
            from java.io import File

            if self.protocol == "Rezistență la Compresiune Cuburi" or self.protocol == "Gelivitate Cuburi":
                classname = "CubeCompression"
                filename = "cube_compression"
            elif self.protocol == "Rezistență la Compresiune Prisme":
                classname = "BeamCompression"
                filename = "beam_compression"
            elif self.protocol == "Rezistență la Încovoiere Prisme":
                classname = "BeamFlexural"
                filename = "beam_flexural"

            # Load and execute the Java class
            protocolclass = jpype.JClass(classname)
            
            # Execute the main method
            protocolclass.main([])
            
            output_file = f"{filename}_receipt.xlsx"
            if os.path.exists(output_file):
                logger.info(f"Excel report generated")
            else:
                raise FileNotFoundError("Excel file was not created")
                
        except Exception as e:
            logger.error(f"Failed to generate Excel report: {e}")
            raise
    
    def generate_report(self):
        """
        Generate concrete test report in specified format.
        
        Args:
            raw_data: Raw test data dictionary
            output_format: "pdf" or "excel"
            
        Returns:
            Path to generated report file
        """

        if "PDF" in self.output_format:
            self.generate_pdf_report()
        elif "Excel" in self.output_format:
            self.generate_excel_report()
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup JVM."""
        if self.jvm_started:
            self.shutdown_jvm()

def main():
    """
    Example usage - you'll need to provide actual data and format
    """
    # Example: Replace with your actual data source
    try:
        # You need to load your actual raw_data here

        input_data = {
          "protocol" : "Rezistență la Încovoiere Prisme",
          "client" : "AGREMIN SRL",
          "concrete_class" : "C 8/10",
          "sampling_date" : "04.06.2025",
          "testing_date" : "08.06.2025",
          "project_title" : "gwer",
          "element" : "bws",
          "set_id" : "13",
          "set_size" : 3,
          "tests": [
                    {
                        "scale_data": "7649.0",
                        "compression_data": {
                            "kN": "00701.0",
                            "MPa": "0031.15"
                        }
                    },
                    {
                        "scale_data": "7550.0",
                        "compression_data": {
                            "kN": "00681.6",
                            "MPa": "0030.28"
                        }
                    },
                    {
                        "scale_data": "7608.5",
                        "compression_data": {
                            "kN": "00716.1",
                            "MPa": "0031.83"
                        }
                    }
                ],
          "should_print" : False,
          "output_format" : [ "PDF" ]
        }

        # Create SetData instance
        raw_data = SetData(input_data=input_data)

        # Using context manager to ensure proper cleanup
        with OutputInterface(raw_data) as interface:
            result_path = interface.generate_report()
            print(f"Report generated: {result_path}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()