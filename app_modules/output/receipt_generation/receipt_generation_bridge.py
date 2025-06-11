"""Receipt generation bridge"""

#%% Dependencies:

import csv
import jpype
from pathlib import Path
from typing import Any, Dict

#%% Receipt Generation Bridge:

class ReceiptGenerationBridge:
    """Integrates existing functionality to isolate the bad receipt generation code"""

    def __init__(self):
        self.ctx = None
        self.config = None
        self.jvm_started = False

        # Protocol mapping for file selection:
        self.protocol_mapping = {'cube_compression_testing': 'cube_compression',
                                 'cube_frost_testing': 'cube_compression',  # Same as cube compression
                                 'beam_compression_testing': 'beam_compression',
                                 'beam_flexural_testing': 'beam_flexural'}


    def setup(self, ctx: Any, config: Any) -> None:
        """Setup receipt generation bridge with context and configuration"""

        self.ctx = ctx
        self.config = config

        try:
            self.ctx.logger.info("Setting up receipt generation bridge...")

            # Ensure output directories exist:
            self._ensure_output_directories()

            self.ctx.logger.info("Receipt generation bridge setup completed")

        except Exception as e:
            error_msg = f"Failed to setup receipt generation bridge: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def generate_receipt(self, set_data: Any,  # Complete SetData instance 
                         output_format: str    # "PDF" or "Excel"
                        ) -> Path:             # Path to generated receipt file
        """Generate receipt for the given set data"""

        try:
            protocol = set_data.input_data.protocol
            self.ctx.logger.info(f"Generating {output_format} receipt for {protocol}")

            # Convert data model to receipt format:
            receipt_data = self._convert_to_receipt_format(set_data)

            if output_format == "PDF":
                return self._generate_pdf_receipt(receipt_data, protocol)
            elif output_format == "Excel":
                return self._generate_excel_receipt(receipt_data, protocol)
            else:
                raise self.ctx.errors.OutputError(f"Unsupported output format: {output_format}")

        except Exception as e:
            error_msg = f"Failed to generate {output_format} receipt: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _convert_to_receipt_format(self, set_data: Any) -> Dict:
        """Convert SetData to receipt format"""

        try:
            input_data = set_data.input_data
            specimens = set_data.specimens

            # Build tests array in receipt format:
            tests = []
            for specimen in specimens:
                test_data = {
                    "scale_data": str(int(specimen.scale_data.mass * 1000)) if specimen.scale_data else "0",
                    "compression_data": {
                        "kN": f"{specimen.press_data.load / 1000:.1f}" if specimen.press_data else "0.0",
                        "MPa": f"{specimen.press_data.strength:.2f}" if specimen.press_data else "0.00"
                    }
                }
                tests.append(test_data)

            protocol_names = {'cube_compression_testing': 'Rezistență la Compresiune Cuburi',
                              'cube_frost_testing': 'Gelivitate Cuburi',
                              'beam_compression_testing': 'Rezistență la Compresiune Prisme', 
                              'beam_flexural_testing': 'Rezistență la Încovoiere Prisme'}

            receipt_format = {"protocol": protocol_names.get(input_data.protocol, input_data.protocol),
                              "client": input_data.client,
                              "concrete_class": input_data.concrete_class,
                              "sampling_date": input_data.sampling_date,
                              "testing_date": input_data.testing_date,
                              "project_title": input_data.project_title,
                              "element": input_data.element,
                              "set_id": input_data.set_id,
                              "set_size": input_data.set_size,
                              "tests": tests,
                              "should_print": input_data.should_print,
                              "output_format": input_data.output_format}

            self.ctx.logger.info(f"Converted data for {len(tests)} specimens")
            return receipt_format

        except Exception as e:
            error_msg = f"Failed to convert data format: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _generate_pdf_receipt(self, data: Dict, protocol: str) -> Path:
        """Generate PDF receipt"""

        try:
            # Map protocol to receipt PDF modules:
            protocol_key = self.protocol_mapping.get(protocol, 'cube_compression')

            if protocol_key == 'cube_compression':
                from app_modules.output.receipt_generation.pdf_generation.CubeCompression import process_test_data, create_pdf_with_reportlab
            elif protocol_key == 'beam_compression':
                from app_modules.output.receipt_generation.pdf_generation.BeamCompression import process_test_data, create_pdf_with_reportlab
            elif protocol_key == 'beam_flexural':
                from app_modules.output.receipt_generation.pdf_generation.BeamFlexural import process_test_data, create_pdf_with_reportlab
            else:
                raise self.ctx.errors.OutputError(f"Unknown protocol for PDF generation: {protocol}")

            # Process data:
            processed_data = process_test_data(data)

            # Generate PDF:
            pdf_path = create_pdf_with_reportlab(data, processed_data)

            # Convert to Path object and verify:
            result_path = Path(pdf_path)
            if not result_path.exists():
                raise self.ctx.errors.OutputError(f"PDF was not created at expected path: {result_path}")

            self.ctx.logger.info(f"PDF receipt generated successfully: {result_path.name}")
            return result_path

        except ImportError as e:
            error_msg = f"Could not import PDF generation module: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)
        except Exception as e:
            error_msg = f"PDF generation failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _generate_excel_receipt(self, data: Dict, protocol: str) -> Path:
        """Generate Excel receipt"""

        try:
            # Start JVM if needed:
            if not self.jvm_started:
                self._start_jvm()

            # Create CSV file for Java consumption:
            csv_path = self._create_csv_for_java(data)

            # Map protocol to Java class names:
            protocol_key = self.protocol_mapping.get(protocol, 'cube_compression')
            class_mapping = {'cube_compression': 'CubeCompression',
                             'beam_compression': 'BeamCompression', 
                             'beam_flexural': 'BeamFlexural'}

            java_class_name = class_mapping.get(protocol_key, 'CubeCompression')

            # Load and execute Java class:
            try:
                self.ctx.logger.info(f"Attempting to load Java class: {java_class_name}")
                java_class = jpype.JClass(java_class_name)
                self.ctx.logger.info(f"Successfully loaded class: {java_class}")

                # Log CSV contents for debugging:
                if csv_path.exists():
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        csv_contents = f.read()
                        self.ctx.logger.info(f"CSV contents:\n{csv_contents}")

                # Execute main method:
                self.ctx.logger.info("Executing Java main method...")
                java_class.main([])
                self.ctx.logger.info("Java execution completed")

            except Exception as e:
                self.ctx.logger.error(f"Failed to execute Java class {java_class_name}: {str(e)}")

                # Log more details about the error:
                import traceback
                self.ctx.logger.error(f"Full exception: {traceback.format_exc()}")

                # Try alternative class loading approach:
                try:
                    self.ctx.logger.info("Trying alternative class loading...")
                    Class = jpype.JClass("java.lang.Class")
                    java_class = Class.forName(java_class_name)
                    self.ctx.logger.info(f"Found class via Class.forName: {java_class}")

                    # Get main method and invoke it
                    method = java_class.getMethod("main", jpype.JClass("[Ljava.lang.String;"))
                    method.invoke(None, jpype.JArray(jpype.JString)(0))

                except Exception as e2:
                    self.ctx.logger.error(f"Alternative class loading also failed: {str(e2)}")
                    raise self.ctx.errors.OutputError(f"Java class {java_class_name} execution failed: {str(e)}")

            # Determine expected output file:
            expected_files = {'cube_compression': 'cube_compression_receipt.xlsx',
                              'beam_compression': 'beam_compression_receipt.xlsx',
                              'beam_flexural': 'beam_flexural_receipt.xlsx'}

            expected_file = expected_files.get(protocol_key, 'cube_compression_receipt.xlsx')
            excel_dir = self.config.data_storage.receipts_dir / "excel_receipts"
            result_path = excel_dir / expected_file

            if not result_path.exists():
                raise self.ctx.errors.OutputError(f"Excel file was not created at expected path: {result_path}")

            # Cleanup temporary CSV:
            csv_path.unlink(missing_ok=True)

            self.ctx.logger.info(f"Excel receipt generated successfully: {result_path.name}")
            return result_path

        except Exception as e:
            error_msg = f"Excel generation failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _create_csv_for_java(self, data: Dict) -> Path:
        """Create CSV file for Java Excel generator"""

        try:
            csv_path = Path("press_data.csv")  # Java expects this exact name, lol

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header information:
                writer.writerow(["indicativ_serie", data["set_id"]])
                writer.writerow(["data_confectionarii", data["sampling_date"]])
                writer.writerow(["data_incercarii", data["testing_date"]])

                # Process test data:
                tests = data["tests"]
                self.ctx.logger.info(f"Processing {len(tests)} test specimens for CSV")

                # Determine expected count based on protocol:
                protocol_key = self.protocol_mapping.get(data.get("protocol", ""), 'cube_compression')

                if protocol_key == 'cube_compression':
                    # Cube compression expects exactly 3 specimens
                    target_count = 3
                elif protocol_key == 'beam_compression':
                    # Beam compression expects 6 specimens (2 measurements each)
                    target_count = 6
                else:
                    # Beam flexural expects 3 specimens
                    target_count = 3

                # Build data arrays with proper handling of partial results:
                weights = []
                forces = []

                # Add actual test data:
                for test in tests[:target_count]:  # Don't exceed target count
                    if test["scale_data"] and test["scale_data"] != "0":
                        weights.append(round(float(test["scale_data"]) / 1000, 3))  # Convert to kg
                    else:
                        weights.append("")  # Empty cell for missing scale data

                    if test["compression_data"]["kN"] and test["compression_data"]["kN"] != "0.0":
                        forces.append(round(float(test["compression_data"]["kN"]) * 1000, 0))  # Convert to N
                    else:
                        forces.append("")  # Empty cell for missing press data

                # Pad with empty cells if we have fewer specimens than target:
                while len(weights) < target_count:
                    weights.append("")  # Empty cell
                    forces.append("")   # Empty cell

                # Write data rows:
                writer.writerow(["greutate"] + weights)
                writer.writerow(["kN"] + forces)

                self.ctx.logger.info(f"Created CSV with {target_count} columns (actual data: {len(tests)})")
                self.ctx.logger.info(f"Weights: {weights}")
                self.ctx.logger.info(f"Forces: {forces}")

            self.ctx.logger.info(f"Created CSV file for Java: {csv_path}")
            return csv_path

        except Exception as e:
            error_msg = f"Failed to create CSV file: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _start_jvm(self) -> None:
        """Start JVM for Java Excel generation"""

        try:
            if jpype.isJVMStarted():
                self.jvm_started = True
                self.ctx.logger.info("JVM already started, using existing JVM for Excel generation")

                # Verify that Excel classes are available:
                self._verify_excel_classes()
                return

            # This should not happen with unified JVM startup, but handle it gracefully:
            self.ctx.logger.warning("JVM not started - this should not happen with unified startup")

            # Build classpath for Apache POI and Java classes:
            receipt_dir = Path(__file__).parent / "receipt_generation" / "excel_generation"
            lib_dir = receipt_dir / "lib"

            # Find all JAR files:
            jar_files = list(lib_dir.glob("*.jar"))

            # Build classpath: Java class directory + all JARs (use absolute paths):
            classpath = [str(receipt_dir.absolute())]
            if jar_files:
                classpath.extend([str(jar.absolute()) for jar in jar_files])
            else:
                self.ctx.logger.warning("No JAR files found in lib directory - Excel generation may fail")

            self.ctx.logger.info(f"Excel directory: {receipt_dir.absolute()}")
            self.ctx.logger.info(f"Starting JVM with classpath: {classpath}")

            # Check if Java files are compiled:
            class_files = list(receipt_dir.glob("*.class"))

            if not class_files:
                error_msg = f"No compiled .class files found in {receipt_dir}. Please compile Java files manually."
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.ConfigurationError(error_msg)

            self.ctx.logger.info(f"Found .class files: {[f.name for f in class_files]}")

            jpype.startJVM(classpath=classpath, convertStrings=False)
            self.jvm_started = True
            self.ctx.logger.info("JVM started successfully for Excel generation")

        except Exception as e:
            error_msg = f"Failed to start JVM: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def _verify_excel_classes(self) -> None:
        """Verify that Excel generation classes are available in the current JVM"""

        try:
            # Try to load the main Excel classes to verify they're in the classpath:
            test_classes = ['CubeCompression', 'BeamCompression', 'BeamFlexural']

            for class_name in test_classes:
                try:
                    jpype.JClass(class_name)
                    self.ctx.logger.info(f"Verified Excel class availability: {class_name}")
                except Exception as e:
                    self.ctx.logger.warning(f"Excel class {class_name} not available: {str(e)}")

        except Exception as e:
            self.ctx.logger.warning(f"Could not verify Excel classes: {str(e)}")


    def _ensure_output_directories(self) -> None:
        """Ensure output directories exist"""

        try:
            receipts_dir = self.config.data_storage.receipts_dir
            pdf_dir = receipts_dir / "pdf_receipts"
            excel_dir = receipts_dir / "excel_receipts"

            pdf_dir.mkdir(parents=True, exist_ok=True)
            excel_dir.mkdir(parents=True, exist_ok=True)

            self.ctx.logger.info("Output directories ensured")

        except Exception as e:
            error_msg = f"Failed to create output directories: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def cleanup(self) -> None:
        """Clean shutdown of receipt generation resources"""

        try:
            if self.jvm_started and jpype.isJVMStarted():
                jpype.shutdownJVM()
                self.jvm_started = False
                self.ctx.logger.info("JVM shutdown completed")

        except Exception as e:
            self.ctx.logger.warning(f"Error during receipt generation cleanup: {str(e)}")

#%%