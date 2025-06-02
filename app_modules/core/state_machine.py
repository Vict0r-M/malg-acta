"""State machine for materials testing workflow"""

#%% Dependencies:

import json
from pathlib import Path
from typing import Dict, Any, Optional

#%% Main Class:

class StateMachine:
    """
    Main workflow controller for materials testing application.
    
    Orchestrates the complete testing workflow from input collection
    through device measurements to output generation.
    """
    
    def __init__(self, ctx: Any, java_bridge: Any) -> None:
        """Initialize state machine with context and bridge"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        self.java_bridge = java_bridge
        
        # State tracking:
        self.current_state = "idle"
        self.current_batch = None
        self.current_set = None
        
        # Load demo data:
        self.demo_data = self._load_demo_data()
        
    def run_demo_workflow(self, input_method: str = "cli") -> bool:
        """
        Run complete demo workflow.
        
        Args:
            input_method: "cli" or "gui" for input method
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            self.logger.info(f"Starting demo workflow with {input_method} input")
            
            # Step 1: Get input data
            if not self._handle_input_phase(input_method):
                return False
            
            # Step 2: Process testing
            if not self._handle_testing_phase():
                return False
            
            # Step 3: Generate outputs
            if not self._handle_output_phase():
                return False
            
            self.logger.info("Demo workflow completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Demo workflow failed: {str(e)}")
            return False
    
    def _handle_input_phase(self, input_method: str) -> bool:
        """Handle input data collection phase"""
        
        try:
            self.current_state = "input"
            self.logger.info("Entering input phase")
            
            # Launch appropriate input method:
            if input_method == "gui":
                if not self.java_bridge.launch_gui():
                    self.logger.error("Failed to launch GUI")
                    return False
                    
                # Wait for user to complete form and check for output:
                self.logger.info("GUI launched. Please complete the form and check for output.json")
                input_file = Path("output.json")
                
            else:  # CLI
                if not self.java_bridge.launch_cli():
                    self.logger.error("Failed to launch CLI")
                    return False
                    
                input_file = Path("formular.json")
            
            # Read and validate input data:
            if not input_file.exists():
                self.logger.error(f"Input file not found: {input_file}")
                return False
            
            with open(input_file, 'r', encoding='utf-8') as f:
                java_input = json.load(f)
            
            # Convert and validate input data:
            converted_input = self.java_bridge.convert_java_input_to_input_data(java_input)
            
            if not converted_input:
                self.logger.error("Failed to convert input data")
                return False
            
            # Create InputData object:
            from ..models.input_data import InputData
            self.input_data = InputData(**converted_input)
            
            self.logger.info("Input phase completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Input phase failed: {str(e)}")
            return False
    
    def _handle_testing_phase(self) -> bool:
        """Handle testing and measurement phase"""
        
        try:
            self.current_state = "testing"
            self.logger.info("Entering testing phase")
            
            # Select appropriate protocol:
            protocol = self._get_protocol(self.input_data.protocol)
            if not protocol:
                return False
            
            # Validate requirements:
            if not protocol.validate_requirements(self.input_data):
                self.logger.error("Protocol requirements validation failed")
                return False
            
            # Create specimens from demo data:
            specimens = protocol.create_specimens_from_demo_data(
                self.demo_data, self.input_data.set_size
            )
            
            if not specimens:
                self.logger.error("Failed to create specimens")
                return False
            
            # Create set data:
            from ..models.set_data import SetData
            self.current_set = SetData(
                input_data=self.input_data,
                specimens=specimens
            )
            
            # Process the set:
            self.processing_results = protocol.process_set(self.current_set)
            
            if not self.processing_results:
                self.logger.error("Set processing failed")
                return False
            
            self.logger.info("Testing phase completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Testing phase failed: {str(e)}")
            return False
    
    def _handle_output_phase(self) -> bool:
        """Handle output generation phase"""
        
        try:
            self.current_state = "output"
            self.logger.info("Entering output phase")
            
            success = True
            
            # Generate requested output formats:
            if "Excel" in self.input_data.output_format:
                if not self.java_bridge.generate_excel_output(self.processing_results):
                    self.logger.error("Excel generation failed")
                    success = False
                else:
                    self.logger.info("Excel output generated successfully")
            
            if "PDF" in self.input_data.output_format:
                if not self.java_bridge.generate_pdf_output(self.processing_results):
                    self.logger.error("PDF generation failed")
                    success = False
                else:
                    self.logger.info("PDF output generated successfully")
            
            # Update registry:
            self._update_registry()
            
            self.current_state = "complete"
            self.logger.info("Output phase completed")
            return success
            
        except Exception as e:
            self.logger.error(f"Output phase failed: {str(e)}")
            return False
    
    def _get_protocol(self, protocol_name: str) -> Optional[Any]:
        """Get protocol implementation by name"""
        
        try:
            if protocol_name == "cube_compression_testing":
                from ..protocols.cube_compression import CubeCompressionProtocol
                return CubeCompressionProtocol(self.ctx)
            
            elif protocol_name == "cube_frost_testing":
                # For demo, use same protocol as cube compression:
                from ..protocols.cube_compression import CubeCompressionProtocol
                protocol = CubeCompressionProtocol(self.ctx)
                # Override protocol name for demo:
                protocol.protocol_config = self.config.protocols.cube_frost_testing
                return protocol
            
            elif protocol_name == "beam_compression_testing":
                # Simplified beam protocol for demo:
                from ..protocols.cube_compression import CubeCompressionProtocol
                protocol = CubeCompressionProtocol(self.ctx)
                protocol.protocol_config = self.config.protocols.beam_compression_testing
                return protocol
            
            elif protocol_name == "beam_flexural_testing":
                # Simplified beam protocol for demo:
                from ..protocols.cube_compression import CubeCompressionProtocol
                protocol = CubeCompressionProtocol(self.ctx)
                protocol.protocol_config = self.config.protocols.beam_flexural_testing
                return protocol
            
            else:
                self.logger.error(f"Unknown protocol: {protocol_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create protocol {protocol_name}: {str(e)}")
            return None
    
    def _load_demo_data(self) -> Dict[str, Any]:
        """Load demo data for simulated measurements"""
        
        try:
            demo_file = Path(self.config.data_paths.demo_data)
            
            if not demo_file.exists():
                self.logger.error(f"Demo data file not found: {demo_file}")
                return {}
            
            with open(demo_file, 'r', encoding='utf-8') as f:
                demo_data = json.load(f)
            
            self.logger.info("Demo data loaded successfully")
            return demo_data
            
        except Exception as e:
            self.logger.error(f"Failed to load demo data: {str(e)}")
            return {}
    
    def _update_registry(self) -> None:
        """Update testing registry with completed test"""
        
        try:
            registry_file = Path(self.config.data_paths.registry_file)
            
            # Load existing registry:
            registry = []
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            
            # Add new entry:
            registry_entry = {
                "timestamp": self.input_data.testing_date,
                "client": self.input_data.client,
                "set_id": self.input_data.set_id,
                "protocol": self.input_data.protocol,
                "concrete_class": self.input_data.concrete_class,
                "specimen_count": self.input_data.set_size,
                "sample_age_days": self.input_data.get_sample_age()
            }
            
            registry.append(registry_entry)
            
            # Save updated registry:
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Registry updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update registry: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        
        return {
            "current_state": self.current_state,
            "has_input_data": hasattr(self, 'input_data'),
            "has_current_set": self.current_set is not None,
            "has_results": hasattr(self, 'processing_results')
        }

#%%