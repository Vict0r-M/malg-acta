"""Input interface - unified bridge for CLI and GUI input methods using plugin architecture"""

#%% Dependencies:

from typing import Any, Protocol
from pydantic import ValidationError

#%% Bridge Protocol:

class InputStrategy(Protocol):
    """Protocol defining what any input plugin must implement"""

    def setup(self, ctx: Any) -> None:
        """Setup strategy with context (config, logger, etc.)"""
        ...


    def get_user_input(self) -> dict:
        """Get user input using this strategy and return raw data"""
        ...


    def unlock_interface(self) -> None:
        """
        GUI: Ready for next cycle
        CLI: Asks user whether to continue or exit
        """
        ...


    def cleanup(self) -> None:
        """Cleanup resources when application shuts down"""
        ...

#%% Actual Interface/Service:

class InputInterface:
    """Provides clean API for state machine: get user input, signal when testing completes"""

    def __init__(self, ctx: Any,          # Context object containing config, logger, errors, typing
                 input_data_class: type,  # InputData Pydantic class for validation
                 plugin_manager: Any):    # PluginManager instance for loading input strategies
        """Initialize input interface with dependency injection"""

        self.ctx = ctx
        self.InputData = input_data_class
        self.plugin_manager = plugin_manager

        # Get input method from config and load appropriate strategy:
        self.input_method = ctx.config.input.method

        try:
            # Use plugin manager to get the strategy based on config:
            self.strategy = self.plugin_manager.get_strategy("input", self.input_method)

            # Setup the strategy with context:
            self.strategy.setup(ctx)

            # Setup user message routing in logger:
            self._setup_user_messaging()

            self.ctx.logger.info(f"InputInterface initialized with {self.input_method} strategy")

        except Exception as e:
            error_msg = f"Failed to initialize input strategy '{self.input_method}': {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def _setup_user_messaging(self) -> None:
        """Configure user message routing in logger for the selected strategy"""

        try:
            # Create user message function based on input method:
            if self.input_method == "gui":

                def user_message_func(level: str, message: str) -> None:
                    """Send message to GUI log panel with safety checks"""
                    try:
                        # Check if GUI strategy has the required method:
                        if hasattr(self.strategy, 'log_to_gui'):
                            self.strategy.log_to_gui(level, message)
                        else:
                            # GUI not ready yet - messages will still go to dev log:
                            pass
                    except Exception as e:
                        # If GUI logging fails, don't raise - just warn developers:
                        self.ctx.logger.warning(f"GUI user message failed: {str(e)}")

            else:  # CLI

                def user_message_func(level: str, message: str) -> None:
                    """Send message to CLI console for user with safety checks"""
                    try:
                        # For CLI, print directly to console with level prefix:
                        print(f"[{level}] {message}")
                    except Exception as e:
                        # If console output fails, warn developers:
                        self.ctx.logger.warning(f"CLI user message failed: {str(e)}")

            # Register with logger:
            self.ctx.logger.user_message_handler = user_message_func
            self.ctx.logger.info("User message routing configured successfully")

        except Exception as e:
            error_msg = f"Failed to setup user messaging: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def get_user_input(self) -> Any:
        """Get user input through strategy and return InputData instance. Signals the start of testing"""

        try:
            self.ctx.logger.info("Starting user input collection")
            self.ctx.logger.info("Please provide the required information", target="user")

            # Get raw data from strategy:
            raw_data = self.strategy.get_user_input()

            self.ctx.logger.info("Raw user data collected, processing...")

            # Transform and validate data
            transformed_data = self._transform_data(raw_data)

            # Create InputData instance with proper Pydantic error handling:
            try:
                input_data = self.InputData(**transformed_data)
                self.ctx.logger.info("User input validation successful", target="both")
                return input_data  # InputData instance populated from user input

            except ValidationError as e:
                # Apply the Pydantic error handling pattern:
                error_msg = f"Input validation failed: {str(e)}"
                self.ctx.logger.error(error_msg, target="both")
                raise self.ctx.errors.ValidationError(error_msg)

        except Exception as e:
            # Don't re-wrap custom errors:
            if isinstance(e, (self.ctx.errors.ValidationError, 
                              self.ctx.errors.DeviceError, 
                              self.ctx.errors.ConfigurationError)):
                raise
            # Wrap unexpected errors:
            error_msg = f"Failed to collect user input: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def unlock_interface(self) -> None:
        """
        Signal that testing has completed and unlock the interface:
        GUI: Ready for next testing cycle
        CLI: Asks user whether to continue or exit application
        """

        try:
            self.ctx.logger.info("Testing completed, unlocking interface", target="user")
            self.strategy.unlock_interface()
            self.ctx.logger.info("Interface unlocked successfully")

        except Exception as e:
            error_msg = f"Failed to unlock interface: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _transform_data(self, raw_data: dict  #  Raw data from GUI or CLI strategy
                       ) -> dict:             #  Transformed data ready for InputData creation
        """Transform interface-specific data to InputData format with enhanced validation"""

        try:
            # Protocol mapping (Romanian → English):
            protocol_mapping = {'Rezistență la Compresiune Cuburi': 'cube_compression_testing',
                                'Gelivitate Cuburi': 'cube_frost_testing', 
                                'Rezistență la Compresiune Prisme': 'beam_compression_testing',
                                'Rezistență la Încovoiere Prisme': 'beam_flexural_testing'}

            # Validate raw data structure:
            if not isinstance(raw_data, dict):
                raise ValueError(f"Expected dictionary, got {type(raw_data)}")

            # Transform based on interface type:
            if self.input_method == "gui":
                return self._transform_gui_data(raw_data, protocol_mapping)
            else:
                return self._transform_cli_data(raw_data, protocol_mapping)

        except Exception as e:
            error_msg = f"Data transformation failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ValidationError(error_msg)


    def _transform_gui_data(self, gui_data: dict, protocol_mapping: dict) -> dict:
        """Transform GUI-specific data structure with validation"""

        # Handle output formats from GUI checkboxes:
        output_formats = []
        output_format_obj = gui_data.get('output_format', {})

        if isinstance(output_format_obj, dict):
            if output_format_obj.get('pdf', False):
                output_formats.append('PDF')
            if output_format_obj.get('excel', False):
                output_formats.append('Excel')

        if not output_formats:
            output_formats = ['PDF']  # Default fallback

        # Map protocol with validation:
        protocol = gui_data.get('protocol', '')
        mapped_protocol = protocol_mapping.get(protocol, protocol)

        if mapped_protocol not in protocol_mapping.values():
            self.ctx.logger.warning(f"Unknown protocol mapping: {protocol} -> {mapped_protocol}")

        # Validate required fields before transformation
        required_fields = ['client', 'concrete_class', 'sampling_date', 'set_id']
        missing_fields = [field for field in required_fields if not gui_data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        transformed = {'protocol': mapped_protocol,
                       'client': gui_data.get('client', '').strip(),
                       'concrete_class': gui_data.get('concrete_class', '').strip(),
                       'sampling_date': gui_data.get('sampling_date', '').strip(),
                       'testing_date': gui_data.get('testing_date', '').strip(),
                       'project_title': gui_data.get('project_title', '').strip(),
                       'element': gui_data.get('element', '').strip(),
                       'set_id': gui_data.get('set_id', '').strip(),
                       'set_size': int(gui_data.get('set_size', 1)),
                       'should_print': bool(gui_data.get('should_print', False)),
                       'output_format': output_formats}

        self.ctx.logger.info("GUI data transformed successfully")
        return transformed


    def _transform_cli_data(self, cli_data: dict, protocol_mapping: dict) -> dict:
        """Transform CLI-specific data structure with validation"""

        # Map protocol with validation:
        protocol = cli_data.get('protocol', '')
        mapped_protocol = protocol_mapping.get(protocol, protocol)

        if mapped_protocol not in protocol_mapping.values():
            self.ctx.logger.warning(f"Unknown protocol mapping: {protocol} -> {mapped_protocol}")

        # Handle output formats from CLI (assuming it's already a list or string):
        output_format = cli_data.get('output_format', ['PDF'])
        if isinstance(output_format, str):
            output_format = [output_format]
        elif not isinstance(output_format, list):
            output_format = ['PDF']

        # Validate required fields before transformation:
        required_fields = ['client', 'concrete_class', 'sampling_date', 'set_id']
        missing_fields = [field for field in required_fields if not cli_data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        transformed = {'protocol': mapped_protocol,
                       'client': cli_data.get('client', '').strip(),
                       'concrete_class': cli_data.get('concrete_class', '').strip(),
                       'sampling_date': cli_data.get('sampling_date', '').strip(),
                       'testing_date': cli_data.get('testing_date', '').strip(),
                       'project_title': cli_data.get('project_title', '').strip(),
                       'element': cli_data.get('element', '').strip(),
                       'set_id': cli_data.get('set_id', '').strip(),
                       'set_size': int(cli_data.get('set_size', 1)),
                       'should_print': bool(cli_data.get('should_print', False)),
                       'output_format': output_format}

        self.ctx.logger.info("CLI data transformed successfully")
        return transformed


    def close(self) -> None:
        """Clean shutdown of interface and strategy"""

        try:
            self.ctx.logger.info("Shutting down input interface...")
            self.strategy.cleanup()
            self.ctx.logger.info("Input interface shutdown completed")

        except Exception as e:
            self.ctx.logger.warning(f"Error during input interface shutdown: {str(e)}")


    def __enter__(self):
        """Context manager entry"""

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self.close()

#%%