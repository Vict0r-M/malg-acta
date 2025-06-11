"""Input state - collects user data for testing"""

#%% Dependencies:

from typing import Any, Tuple

#%% Input State:

class InputState:
    """Bridges between idle state and acquisition state with validated user data"""

    def __init__(self, input_interface: Any, input_data_class: type):

        self.input_interface = input_interface
        self.input_data_class = input_data_class
        self.state_name = "input_state"
        self.input_data = None


    def enter(self, ctx: Any, data: Any = None) -> None:
        """Enter input state - prepare for user data collection"""

        try:
            ctx.logger.info("Entering input state - ready for user data")

            # Handle data from previous state:
            if data:
                # If coming from idle state with pre-submitted GUI data:
                if isinstance(data, dict) and 'data' in data:
                    self._pre_submitted_data = data
                    ctx.logger.info("Received pre-submitted data from GUI")
                # If coming from error state with recoverable error:
                elif isinstance(data, dict) and data.get("retry_input"):
                    ctx.logger.info("Retrying input collection after error", target="user")
                # If coming with pre-filled data:
                elif hasattr(data, 'protocol'):
                    ctx.logger.info("Resuming with partially filled data", target="user")
            else:
                self._pre_submitted_data = None

            # Reset input data:
            self.input_data = None

            ctx.logger.info("Ready to collect testing parameters", target="user")

        except Exception as e:
            error_msg = f"Error entering input state: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.StateMachineError(error_msg)


    def execute(self, ctx: Any        # Context object
               ) -> Tuple[str, Any]:  # (next_state_name, validated_input_data)
        """Execute input state logic - collect and validate user data"""

        try:
            ctx.logger.info("Starting user data collection")

            # Check if we have pre-submitted data from idle state (GUI case):
            if hasattr(self, '_pre_submitted_data') and self._pre_submitted_data:
                ctx.logger.info("Using pre-submitted data from GUI")
                raw_data = self._pre_submitted_data['data']
                self._pre_submitted_data = None  # Clear it

                # Transform and validate the pre-submitted data:
                input_method = ctx.config.input.method
                if input_method == "gui":
                    transformed_data = self.input_interface._transform_gui_data(raw_data, {
                        'Rezistență la Compresiune Cuburi': 'cube_compression_testing',
                        'Gelivitate Cuburi': 'cube_frost_testing', 
                        'Rezistență la Compresiune Prisme': 'beam_compression_testing',
                        'Rezistență la Încovoiere Prisme': 'beam_flexural_testing'
                    })

                    # Create InputData instance:
                    self.input_data = self.input_data_class(**transformed_data)
                else:
                    # Fallback to normal collection
                    self.input_data = self.input_interface.get_user_input()
            else:
                # Normal data collection via input interface:
                self.input_data = self.input_interface.get_user_input()

            # Log successful collection:
            ctx.logger.info(f"Collected input data for protocol: {self.input_data.protocol}")
            ctx.logger.info(f"Set ID: {self.input_data.set_id}, Size: {self.input_data.set_size}")
            ctx.logger.info(f"Client: {self.input_data.client}")

            # Validate protocol-specific requirements:
            self._validate_protocol_requirements(ctx, self.input_data)

            # Log successful validation:
            ctx.logger.info("Input validation completed successfully")
            ctx.logger.info("Starting testing workflow...", target="user")

            # Transition to acquisition state with validated data:
            return ("acquisition_state", self.input_data)

        except ctx.errors.ValidationError as e:
            # Handle validation errors - stay in input state for retry:
            ctx.logger.error(f"Input validation failed: {str(e)}", target="both")
            return ("input_state", {"retry_input": True, "error": str(e)})

        except ctx.errors.DeviceError as e:
            # Handle device/interface errors - transition to error state:
            ctx.logger.error(f"Input interface error: {str(e)}")
            return ("error_state", {"error": e, "source_state": "input_state", "recoverable": True})

        except KeyboardInterrupt:
            # Handle user cancellation - return to idle:
            ctx.logger.info("User cancelled input collection")
            ctx.logger.info("Returning to idle state", target="user")
            return ("idle_state", {"user_cancelled": True})

        except Exception as e:
            # Handle unexpected errors:
            ctx.logger.exception(f"Unexpected error in input state: {str(e)}")
            error_obj = ctx.errors.StateMachineError(f"Input collection failed: {str(e)}")
            return ("error_state", {"error": error_obj, "source_state": "input_state", "recoverable": False})


    def exit(self, ctx: Any) -> None:
        """Exit input state"""

        try:
            ctx.logger.info("Exiting input state")

            # Log collected data summary for debugging:
            if self.input_data:
                ctx.logger.info(f"Input data collected: {self.input_data.protocol} for {self.input_data.set_size} specimens")

        except Exception as e:
            ctx.logger.warning(f"Error exiting input state: {str(e)}")


    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """Check if transition to target state is allowed from input state"""

        # From input state, we can go to:
        # - acquisition_state (normal flow with valid data)
        # - error_state (on errors)
        # - idle_state (on user cancellation)
        # - input_state (on validation errors for retry)
        allowed_transitions = ["acquisition_state", "error_state", "idle_state", "input_state"]
        return target_state in allowed_transitions


    def _validate_protocol_requirements(self, ctx: Any, input_data: Any) -> None:
        """Validate protocol-specific requirements and constraints"""

        try:
            protocol = input_data.protocol

            # Protocol-specific validation:
            if protocol == "cube_compression_testing":
                self._validate_cube_compression(ctx, input_data)
            elif protocol == "cube_frost_testing":
                self._validate_cube_frost(ctx, input_data)
            elif protocol == "beam_compression_testing":
                self._validate_beam_compression(ctx, input_data)
            elif protocol == "beam_flexural_testing":
                self._validate_beam_flexural(ctx, input_data)
            else:
                raise ctx.errors.ValidationError(f"Unknown protocol: {protocol}")

            ctx.logger.info(f"Protocol-specific validation passed for {protocol}")

        except ctx.errors.ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            error_msg = f"Protocol validation failed: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.ValidationError(error_msg)


    def _validate_cube_compression(self, ctx: Any, input_data: Any) -> None:
        """Validate cube compression testing requirements"""

        # Cube compression uses both scale and press:
        if input_data.set_size > 20:  # Reasonable limit for cube testing
            raise ctx.errors.ValidationError("Cube compression: maximum 20 specimens per set")
        
        ctx.logger.info("Cube compression validation: requires scale and press measurements")


    def _validate_cube_frost(self, ctx: Any, input_data: Any) -> None:
        """Validate cube frost testing requirements"""

        # Cube frost uses both scale and press, specimens must be in specific order:
        if input_data.set_size > 20:
            raise ctx.errors.ValidationError("Cube frost: maximum 20 specimens per set")
        
        ctx.logger.info("Cube frost validation: requires scale and press measurements in specific order")


    def _validate_beam_compression(self, ctx: Any, input_data: Any) -> None:
        """Validate beam compression testing requirements"""

        # Beam compression uses press only, requires two measurements per specimen:
        if input_data.set_size > 10:  # Fewer beams since each needs two press measurements
            raise ctx.errors.ValidationError("Beam compression: maximum 10 specimens per set")

        ctx.logger.info("Beam compression validation: requires two press measurements per specimen")


    def _validate_beam_flexural(self, ctx: Any, input_data: Any) -> None:
        """Validate beam flexural testing requirements"""

        # Beam flexural uses press only, one measurement per specimen:
        if input_data.set_size > 15:
            raise ctx.errors.ValidationError("Beam flexural: maximum 15 specimens per set")

        ctx.logger.info("Beam flexural validation: requires one press measurement per specimen")

#%%