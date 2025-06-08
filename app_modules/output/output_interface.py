import json
import os
import csv
import jpype
import jpype.imports
from jpype.types import *
from typing import Dict, List, Any, Optional
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConcreteTestReportGenerator:
    """
    Unified interface for generating concrete test reports in PDF or Excel format.
    Uses Python for PDF generation and Java (via JPype) for Excel generation.
    """
    
    def __init__(self, java_classpath: str = "."):
        """
        Initialize the report generator.
        
        Args:
            java_classpath: Path to Java classes and dependencies
        """
        self.java_classpath = java_classpath
        self.jvm_started = False
        
    def start_jvm(self):
        """Start the JVM for Java Excel generation if not already started."""
        if not jpype.isJVMStarted():
            try:
                # Add Apache POI jars to classpath
                lib_dir = os.path.abspath("lib")  # Where your jars are stored
                jars = glob.glob(os.path.join(lib_dir, "*.jar"))
                classpath = [self.java_classpath] + jars
                
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
    
    def process_test_data_for_pdf(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw test data for PDF generation (Python version).
        
        Args:
            raw_data: Raw test data dictionary
            
        Returns:
            Processed data dictionary
        """
        tests = raw_data["tests"]
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
    
    def create_csv_for_java(self, raw_data: Dict[str, Any], csv_filename: str = "press_data.csv"):
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
                writer.writerow(["indicativ_serie", raw_data.get("set_id", "")])
                writer.writerow(["data_confectionarii", raw_data.get("sampling_date", "")])
                writer.writerow(["data_incercarii", raw_data.get("testing_date", "")])
                
                # Process test data
                tests = raw_data["tests"]
                weights = [round(float(test["scale_data"]) / 1000, 3) for test in tests]  # Convert to kg
                forces = [round(float(test["compression_data"]["kN"]) * 1000, 0) for test in tests]  # Convert to N
                
                # Write data rows
                writer.writerow(["greutate"] + weights)
                writer.writerow(["kN"] + forces)
                
            logger.info(f"CSV file created: {csv_filename}")
            
        except Exception as e:
            logger.error(f"Failed to create CSV file: {e}")
            raise
    
    def generate_pdf_report(self, raw_data: Dict[str, Any]) -> str:
        """
        Generate PDF report using Python.
        
        Args:
            raw_data: Raw test data dictionary
            
        Returns:
            Path to generated PDF file
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # Register fonts if available
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
                font_name = 'DejaVuSans'
            except:
                font_name = 'Helvetica'  # Fallback to default font
                logger.warning("DejaVu fonts not found, using Helvetica")
            
            # Process data
            processed_data = self.process_test_data_for_pdf(raw_data)
            
            set_id = raw_data["set_id"]
            sampling_date = raw_data["sampling_date"]
            testing_date = raw_data["testing_date"]
            test_count = len(raw_data["tests"])
            total_cols = 4 + test_count + 1  # 4 label columns + test values + average

            weights = processed_data["weights"]
            forces = processed_data["forces"]
            pressures = processed_data["pressures"]
            densities = processed_data["densities"]
            averages = processed_data["averages"]

            # Create output directory
            filename = f"{set_id}_{testing_date.replace('/', '_').replace('-', '_')}.pdf"
            target_path = os.path.join(os.getcwd(), filename)
            doc = SimpleDocTemplate(target_path, pagesize=A4, topMargin=10*mm, bottomMargin=10*mm,
                                    leftMargin=10*mm, rightMargin=10*mm)

            table_data = []

            # Header rows
            table_data.append(["PILOT 4, Model 50 - C4642 Serial Nr. 12010780"] + [""] * (total_cols - 1))
            table_data.append(["Rezultatele încercării:"] + [""] * (total_cols - 1))
            table_data.append(["Indicativ Proba", "", "", ""] + [f"{i+1}" for i in range(test_count)] + ["Media"])

            # Helper function for building rows
            def build_row(label_parts, values):
                return label_parts + values

            # Data rows
            table_data.append(build_row(["Data confecționării", "", "", ""], [sampling_date] * test_count + [sampling_date]))
            table_data.append(build_row(["Data încercării", "", "", ""], [testing_date] * test_count + [testing_date]))
            table_data.append(build_row(["Dimensiunile cubului", "", "", "x [mm]"], ["150"] * test_count + ["150"]))
            table_data.append(build_row(["", "", "", "y [mm]"], ["150"] * test_count + ["150"]))
            table_data.append(build_row(["", "", "", "z [mm]"], ["150"] * test_count + ["150"]))
            table_data.append(build_row(["Suprafața de compresiune [mm²]", "", "", ""], ["22500"] * test_count + ["22500"]))
            table_data.append(build_row(["Greutatea cubului [Kg]", "", "", ""], [str(w) for w in weights] + [str(averages["weight"])]))
            table_data.append(build_row(["Densitatea specifică aparentă [Kg/m³]", "", "", ""], [str(d) for d in densities] + [str(averages["density"])]))
            table_data.append(build_row(["Sarcina de rupere la compresiune [N]", "", "", ""], [str(f) for f in forces] + [str(averages["force"])]))
            table_data.append(build_row(["Rezistența de rupere la compresiune [N/mm²]", "", "", ""], [str(p) for p in pressures] + [str(averages["pressure"])]))

            col_widths = [20*mm] * total_cols
            row_heights = [5.5*mm] * len(table_data)

            table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)

            table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.4, colors.black),

                    # Merge header rows
                    ('ALIGN', (0, 0), (0, 1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, 0), 'DejaVuSans-Bold'),
                    ('SPAN', (0, 0), (total_cols-1, 0)),
                    ('SPAN', (0, 1), (total_cols-1, 1)),
                    ('SPAN', (0, 2), (4, 2)),

                    # Dimensiuni cubului spans
                    ('SPAN', (0, 5), (3, 7)),

                    # Other multi-column labels
                    ('SPAN', (0, 3), (4, 3)),
                    ('SPAN', (0, 4), (4, 4)),
                    ('SPAN', (0, 8), (4, 8)),
                    ('SPAN', (0, 9), (4, 9)),
                    ('SPAN', (0, 10), (4, 10)),
                    ('SPAN', (0, 11), (4, 11)),
                    ('SPAN', (0, 12), (4, 12)),

                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ]))

            doc.build([table])
            logger.info(f"PDF generated at: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise
    
    def generate_excel_report(self, raw_data: Dict[str, Any]) -> str:
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
            self.create_csv_for_java(raw_data, csv_filename)
            
            # Import and run Java class
            from java.lang import System
            from java.io import File
            
            # Load and execute the Java class
            CubeCompression = jpype.JClass("CubeCompression")
            
            # Execute the main method
            CubeCompression.main([])
            
            output_file = "cube_compression_receipt.xlsx"
            if os.path.exists(output_file):
                logger.info(f"Excel report generated: {output_file}")
                return output_file
            else:
                raise FileNotFoundError("Excel file was not created")
                
        except Exception as e:
            logger.error(f"Failed to generate Excel report: {e}")
            raise
    
    def generate_report(self, raw_data: Dict[str, Any], output_format: str = "pdf") -> str:
        """
        Generate concrete test report in specified format.
        
        Args:
            raw_data: Raw test data dictionary
            output_format: "pdf" or "excel"
            
        Returns:
            Path to generated report file
        """
        output_format = output_format.lower()
        
        if output_format == "pdf":
            return self.generate_pdf_report(raw_data)
        elif output_format in ["excel", "xlsx"]:
            return self.generate_excel_report(raw_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup JVM."""
        if self.jvm_started:
            self.shutdown_jvm()


def main():
    """Example usage of the ConcreteTestReportGenerator."""
    
    # Sample test data structure
    sample_data = {
        "set_id": "SAMPLE_001",
        "sampling_date": "2024-01-15",
        "testing_date": "2024-01-22",
        "tests": [
            {
                "scale_data": "7850",  # grams
                "compression_data": {
                    "kN": "425.5",
                    "MPa": "18.91"
                }
            },
            {
                "scale_data": "7920",  # grams
                "compression_data": {
                    "kN": "438.2",
                    "MPa": "19.48"
                }
            },
            {
                "scale_data": "7780",  # grams
                "compression_data": {
                    "kN": "412.8",
                    "MPa": "18.35"
                }
            }
        ]
    }
    
    # Use the generator with context manager
    with ConcreteTestReportGenerator() as generator:
        print("Concrete Test Report Generator")
        print("=" * 40)
        
        while True:
            print("\nSelect output format:")
            print("1. PDF")
            print("2. Excel")
            print("3. Both")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                try:
                    pdf_path = generator.generate_report(sample_data, "pdf")
                    print(f"✅ PDF report generated: {pdf_path}")
                except Exception as e:
                    print(f"❌ Error generating PDF: {e}")
                    
            elif choice == "2":
                try:
                    excel_path = generator.generate_report(sample_data, "excel")
                    print(f"✅ Excel report generated: {excel_path}")
                except Exception as e:
                    print(f"❌ Error generating Excel: {e}")
                    
            elif choice == "3":
                try:
                    pdf_path = generator.generate_report(sample_data, "pdf")
                    excel_path = generator.generate_report(sample_data, "excel")
                    print(f"✅ PDF report generated: {pdf_path}")
                    print(f"✅ Excel report generated: {excel_path}")
                except Exception as e:
                    print(f"❌ Error generating reports: {e}")
                    
            elif choice == "4":
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()