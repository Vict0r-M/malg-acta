"""Acquisition state - handles data collection from devices (mock implementation for 1.0.0)"""

#%% Dependencies:

import time
import random
from typing import Any, Tuple

#%% Acquisition State:

class AcquisitionState:
    """
    Acquisition state: coordinates device communication and data collection
    Mock implementation for 1.0.0 - simulates realistic device behavior
    """

    def __init__(self):
        """Initialize acquisition state"""
        self.state_name = "acquisition_state"
        self.input_data = None
        self.current_set = None
        self.current_specimen_index = 0
        self.protocol_handler = None

    def enter(self, ctx: Any, data: Any = None) -> None:
        """
        Enter acquisition state with validated input data
        Args:
            ctx: Context object
            data: InputData instance from input_state
        """
        try:
            ctx.logger.info("Entering acquisition state - preparing for testing")

            if not data or not hasattr(data, 'protocol'):
                raise ctx.errors.StateMachineError("Acquisition state requires valid input data")

            self.input_data = data
            ctx.logger.info(f"Starting {data.protocol} for {data.set_size} specimens")

            # Create new set data structure:
            self.current_set = self._create_set_data(ctx, data)
            self.current_specimen_index = 0

            # Initialize protocol-specific handler:
            self.protocol_handler = self._get_protocol_handler(ctx, data.protocol)

            ctx.logger.info(f"Testing {data.set_id} ready to begin", target="user")
            ctx.logger.info("Please follow the instructions for each specimen", target="user")

        except Exception as e:
            error_msg = f"Error entering acquisition state: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.StateMachineError(error_msg)

    def execute(self, ctx: Any) -> Tuple[str, Any]:
        """
        Execute acquisition logic - collect data for all specimens
        Args:
            ctx: Context object
        Returns:
            tuple: (next_state_name, complete_set_data)
        """
        try:
            ctx.logger.info("Starting specimen data collection")

            # Process each specimen in the set:
            while self.current_specimen_index < self.input_data.set_size:
                specimen_number = self.current_specimen_index + 1

                ctx.logger.info(f"Processing specimen {specimen_number}/{self.input_data.set_size}", target="user")

                # Collect data for current specimen using protocol handler:
                specimen_data = self.protocol_handler.collect_specimen_data(
                    ctx, specimen_number, self.current_specimen_index
                )

                # Add specimen to set:
                self.current_set.add_specimen(ctx, specimen_data)

                # Move to next specimen:
                self.current_specimen_index += 1

                ctx.logger.info(f"Specimen {specimen_number} data collected successfully")

            # All specimens processed:
            ctx.logger.info("All specimen data collected successfully")
            ctx.logger.info(f"Testing of set {self.input_data.set_id} completed", target="user")

            # Transition to dissemination state with complete set:
            return ("dissemination_state", self.current_set)

        except ctx.errors.DeviceError as e:
            # Handle device errors - transition to error state:
            ctx.logger.error(f"Device error during acquisition: {str(e)}", target="both")
            return ("error_state", {
                "error": e,
                "source_state": "acquisition_state",
                "partial_data": self.current_set,
                "recoverable": True
            })

        except KeyboardInterrupt:
            # Handle user interruption:
            ctx.logger.info("Testing interrupted by user")
            ctx.logger.info("Returning to idle state", target="user")
            return ("idle_state", {"testing_interrupted": True})

        except Exception as e:
            # Handle unexpected errors:
            ctx.logger.exception(f"Unexpected error during acquisition: {str(e)}")
            error_obj = ctx.errors.StateMachineError(f"Data acquisition failed: {str(e)}")
            return ("error_state", {
                "error": error_obj,
                "source_state": "acquisition_state",
                "partial_data": self.current_set,
                "recoverable": False
            })

    def exit(self, ctx: Any) -> None:
        """
        Exit acquisition state
        Args:
            ctx: Context object
        """
        try:
            ctx.logger.info("Exiting acquisition state")

            # Log completion summary:
            if self.current_set and self.current_set.is_complete():
                ctx.logger.info(f"Successfully collected data for {len(self.current_set.specimens)} specimens")

        except Exception as e:
            ctx.logger.warning(f"Error exiting acquisition state: {str(e)}")

    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """
        Check if transition to target state is allowed from acquisition
        Args:
            ctx: Context object
            target_state: Name of target state
        Returns:
            bool: True if transition is allowed
        """
        # From acquisition state, we can go to:
        # - dissemination_state (normal completion)
        # - error_state (on errors)
        # - idle_state (on user cancellation)
        allowed_transitions = ["dissemination_state", "error_state", "idle_state"]
        return target_state in allowed_transitions

    def _create_set_data(self, ctx: Any, input_data: Any) -> Any:
        """
        Create SetData instance with input data
        Args:
            ctx: Context object
            input_data: Validated input data
        Returns:
            SetData instance
        """
        try:
            # Import SetData model:
            from app_modules.models.set_data import SetData
            
            set_data = SetData(input_data=input_data)
            ctx.logger.info(f"Created set data structure for {input_data.set_size} specimens")
            return set_data

        except Exception as e:
            error_msg = f"Failed to create set data: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.StateMachineError(error_msg)

    def _get_protocol_handler(self, ctx: Any, protocol: str) -> Any:
        """
        Get protocol-specific handler for data collection
        Args:
            ctx: Context object
            protocol: Protocol name
        Returns:
            Protocol handler instance
        """
        try:
            if protocol == "cube_compression_testing":
                return CubeCompressionHandler()
            elif protocol == "cube_frost_testing":
                return CubeFrostHandler()
            elif protocol == "beam_compression_testing":
                return BeamCompressionHandler()
            elif protocol == "beam_flexural_testing":
                return BeamFlexuralHandler()
            else:
                raise ctx.errors.ProtocolError(f"Unknown protocol: {protocol}")

        except Exception as e:
            error_msg = f"Failed to create protocol handler: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.ProtocolError(error_msg)


#%% Mock Protocol Handlers:

class MockProtocolHandler:
    """Base class for mock protocol handlers"""

    def simulate_scale_reading(self, ctx: Any, specimen_number: int) -> Any:
        """Simulate scale measurement"""
        from app_modules.models.scale_data import ScaleData
        
        # Simulate realistic mass readings (2-8 kg range for concrete specimens):
        mass = random.uniform(2.5, 7.8)
        
        ctx.logger.info(f"Place specimen {specimen_number} on scale", target="user")
        time.sleep(1)  # Simulate reading time
        ctx.logger.info(f"Scale reading: {mass:.1f} kg", target="user")
        
        return ScaleData(mass=mass, mass_decimals=1, mass_unit="kg")

    def simulate_press_reading(self, ctx: Any, specimen_number: int, measurement_type: str = "single") -> Any:
        """Simulate press measurement"""
        from app_modules.models.press_data import PressData
        
        # Simulate realistic concrete strength readings:
        # Typical range: 20-60 N/mm² for concrete
        strength = random.uniform(25.0, 55.0)
        # Convert to load (assuming 150mm x 150mm specimen = 22500 mm²):
        load = strength * 22500  # Load in N
        
        ctx.logger.info(f"Place specimen {specimen_number} in press ({measurement_type})", target="user")
        time.sleep(2)  # Simulate test time
        ctx.logger.info(f"Press reading: {load:.0f} N ({strength:.2f} N/mm²)", target="user")
        
        return PressData(load=load, strength=strength, load_decimals=0, strength_decimals=2)


class CubeCompressionHandler(MockProtocolHandler):
    """Handler for cube compression testing"""

    def collect_specimen_data(self, ctx: Any, specimen_number: int, index: int) -> Any:
        """Collect scale and press data for cube compression"""
        from app_modules.models.specimen_data import SpecimenData
        
        ctx.logger.info(f"Cube compression test - specimen {specimen_number}")
        
        # Collect scale data:
        scale_data = self.simulate_scale_reading(ctx, specimen_number)
        
        # Collect press data:
        press_data = self.simulate_press_reading(ctx, specimen_number, "compression")
        
        return SpecimenData(scale_data=scale_data, press_data=press_data)


class CubeFrostHandler(MockProtocolHandler):
    """Handler for cube frost testing"""

    def collect_specimen_data(self, ctx: Any, specimen_number: int, index: int) -> Any:
        """Collect scale and press data for cube frost testing"""
        from app_modules.models.specimen_data import SpecimenData
        
        ctx.logger.info(f"Cube frost test - specimen {specimen_number} (order matters!)", target="user")
        
        # Collect scale data:
        scale_data = self.simulate_scale_reading(ctx, specimen_number)
        
        # Collect press data:
        press_data = self.simulate_press_reading(ctx, specimen_number, "frost resistance")
        
        return SpecimenData(scale_data=scale_data, press_data=press_data)


class BeamCompressionHandler(MockProtocolHandler):
    """Handler for beam compression testing"""

    def collect_specimen_data(self, ctx: Any, specimen_number: int, index: int) -> Any:
        """Collect two press measurements for beam compression"""
        from app_modules.models.specimen_data import SpecimenData
        
        ctx.logger.info(f"Beam compression test - specimen {specimen_number} (2 measurements)")
        
        # No scale measurement for beam compression
        
        # First press measurement:
        press_data_1 = self.simulate_press_reading(ctx, specimen_number, "first measurement")
        
        # Second press measurement:
        press_data_2 = self.simulate_press_reading(ctx, specimen_number, "second measurement")
        
        # For 1.0.0, store the higher value:
        if press_data_1.strength > press_data_2.strength:
            press_data = press_data_1
        else:
            press_data = press_data_2
        
        return SpecimenData(scale_data=None, press_data=press_data)


class BeamFlexuralHandler(MockProtocolHandler):
    """Handler for beam flexural testing"""

    def collect_specimen_data(self, ctx: Any, specimen_number: int, index: int) -> Any:
        """Collect single press measurement for beam flexural"""
        from app_modules.models.specimen_data import SpecimenData
        
        ctx.logger.info(f"Beam flexural test - specimen {specimen_number}")
        
        # No scale measurement for beam flexural
        
        # Single press measurement:
        press_data = self.simulate_press_reading(ctx, specimen_number, "flexural")
        
        return SpecimenData(scale_data=None, press_data=press_data)

#%%