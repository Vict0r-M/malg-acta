"""CLI bridge - command line interface input strategy"""

#%% Dependencies:

import time
import queue
from pathlib import Path
from typing import Any, Optional

import jpype
from jpype.types import *

#%% CLI Bridge Strategy (Implements InputStrategy):

class CLIBridge:
    """CLI input strategy implementation using Java application and JPype1"""

    def __init__(self):
        """Initialize CLI bridge with default state"""

        self.ctx = None
        self.data_queue = queue.Queue()
        self.cli_instance = None
        self.java_input_class = None
        self.jvm_started = False

        self.session_active = False
        self.interface_locked = False
        self.continue_testing = True  # Flag to control testing continuation


    def setup(self, ctx: Any) -> None:
        """Setup CLI bridge with context and initialize Java CLI application"""

        self.ctx = ctx

        try:
            self.ctx.logger.info("Setting up CLI bridge...")

            # Start JVM with proper classpath:
            self._start_jvm()

            # Load CLI class:
            self._load_cli_class()

            # Mark session as active:
            self.session_active = True
            self.continue_testing = True

            self.ctx.logger.info("CLI bridge setup completed successfully")

        except Exception as e:
            error_msg = f"Failed to setup CLI bridge: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def get_user_input(self) -> dict:
        """Get user input through CLI interface. Runs CLI application and waits for completion"""

        try:
            if not self.session_active:
                error_msg = "CLI session not active - call setup() first"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.DeviceError(error_msg)

            self.ctx.logger.info("CLI ready for user input", target="user")
            self.ctx.logger.info("Starting CLI input collection...")

            # Clear any previous data in queue:
            while not self.data_queue.empty():
                try:
                    self.data_queue.get_nowait()
                except queue.Empty:
                    break

            # Run CLI interactive mode - this will block until user completes input:
            result = self._run_cli_interactive()

            if not result:
                error_msg = "CLI input was cancelled by user"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.ValidationError(error_msg)

            self.ctx.logger.info("User completed CLI input")

            # Interface is now locked (show testing status):
            self.interface_locked = True
            self._show_testing_status()

            return result

        except Exception as e:
            if isinstance(e, (self.ctx.errors.ValidationError, self.ctx.errors.DeviceError)):
                raise
            error_msg = f"CLI input failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def unlock_interface(self) -> None:
        """
        Unlock CLI interface after testing completes
        Asks user whether to continue with another test or exit application
        """

        try:
            if not self.interface_locked:
                self.ctx.logger.warning("Attempted to unlock interface that wasn't locked")
                return

            self.ctx.logger.info("Testing completed", target="user")
            self.ctx.logger.info("Unlocking CLI interface...")

            # Ask user whether to continue or exit:
            continue_choice = self._ask_continue_or_exit()

            if continue_choice:
                self.interface_locked = False
                self.continue_testing = True
                self.ctx.logger.info("Ready for next testing cycle", target="user")
            else:
                self.ctx.logger.info("User chose to exit application", target="user")
                self.session_active = False
                self.continue_testing = False

        except Exception as e:
            error_msg = f"Failed to unlock CLI interface: {str(e)}"
            self.ctx.logger.error(error_msg)
            self.session_active = False
            self.continue_testing = False
            raise self.ctx.errors.DeviceError(error_msg)


    def cleanup(self) -> None:
        """Clean shutdown of CLI and JVM resources"""

        try:
            if self.ctx:
                self.ctx.logger.info("Shutting down CLI bridge...")

            # Mark session as inactive:
            self.session_active = False

            # Shutdown JVM:
            if self.jvm_started and jpype.isJVMStarted():
                jpype.shutdownJVM()
                self.jvm_started = False

            if self.ctx:
                self.ctx.logger.info("CLI bridge shutdown completed")

        except Exception as e:
            if self.ctx:
                self.ctx.logger.warning(f"Error during CLI bridge cleanup: {str(e)}")


    def _start_jvm(self) -> None:
        """Start JVM with proper classpath for CLI application"""

        if jpype.isJVMStarted():
            self.jvm_started = True
            self.ctx.logger.info("JVM already started, skipping CLI JVM initialization")
            return

        try:
            # Determine paths relative to malg-acta project root:
            cli_app_path = Path(__file__).parent / "cli-app"

            # Use the fat JAR that includes all dependencies:
            fat_jar_path = cli_app_path / "target" / "cli-app-0.0.1-SNAPSHOT-jar-with-dependencies.jar"

            if not fat_jar_path.exists():
                error_msg = f"Fat JAR not found at {fat_jar_path}. Please run 'mvn package' first."
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.DeviceError(error_msg)

            classpath = [str(fat_jar_path)]

            self.ctx.logger.info(f"Starting JVM with classpath: {classpath}")

            # Apply retry logic from config:
            retry_count = getattr(self.ctx.config.input, 'retry_count', 3)

            for attempt in range(retry_count):
                try:
                    jpype.startJVM(classpath=classpath)
                    self.jvm_started = True
                    self.ctx.logger.info("JVM started successfully")
                    return

                except Exception as e:
                    if attempt == retry_count - 1:
                        raise
                    self.ctx.logger.warning(f"JVM start attempt {attempt + 1} failed: {str(e)}, retrying...")
                    time.sleep(1)  # Brief delay before retry

        except Exception as e:
            error_msg = f"Failed to start JVM: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _load_cli_class(self) -> None:
        """Load the Java CLI class"""

        try:
            self.ctx.logger.info("Loading InputCLI class...")
            self.java_input_class = jpype.JClass("com.malg_acta.cli_app.InputCLI")
            self.ctx.logger.info("InputCLI class loaded successfully")

        except Exception as e:
            error_msg = f"Failed to load InputCLI class: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _run_cli_interactive(self) -> Optional[dict]:
        """Run the Java CLI application interactively and capture data directly"""

        if not self.java_input_class:
            error_msg = "CLI class not loaded"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)

        try:
            self.ctx.logger.info("Starting Java CLI application...")
            java_data_object = self.java_input_class.collectUserInput()

            if java_data_object is None:
                error_msg = "CLI input was cancelled by user"
                self.ctx.logger.info(error_msg)
                raise self.ctx.errors.ValidationError(error_msg)

            # Convert Java DataClassCLI object to Python dictionary:
            python_data = self._convert_java_object_to_dict(java_data_object)

            self.ctx.logger.info("CLI data collection completed")
            return python_data

        except Exception as e:
            error_msg = f"Error running CLI application: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _convert_java_object_to_dict(self, java_data_object) -> dict:
        """Convert Java DataClassCLI object to Python dictionary using JPype"""

        try:
            # Extract data from Java object using getter methods:
            python_data = {
                'protocol': str(java_data_object.getProtocol()),
                'client': str(java_data_object.getClient()),
                'concrete_class': str(java_data_object.getConcreteClass()),
                'sampling_date': str(java_data_object.getSamplingDate()),
                'testing_date': str(java_data_object.getTestingDate()),
                'project_title': str(java_data_object.getProjectTitle()),
                'element': str(java_data_object.getElement()),
                'set_id': str(java_data_object.getSetId()),
                'set_size': int(java_data_object.getSetSize()),
                'should_print': bool(java_data_object.isShouldPrint()),
                'output_format': self._convert_java_list_to_python(java_data_object.getOutputFormat())
            }

            # Validate required fields:
            required_fields = ['protocol', 'client', 'concrete_class', 'sampling_date', 'set_id']
            missing_fields = [field for field in required_fields if not python_data.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            self.ctx.logger.info("Java object converted to Python dictionary successfully")
            return python_data

        except Exception as e:
            error_msg = f"Failed to convert Java object to dictionary: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ValidationError(error_msg)


    def _convert_java_list_to_python(self, java_list) -> list:
        """Convert Java List to Python list"""

        try:
            if java_list is None:
                return []

            # Convert Java list to Python list:
            python_list = []
            for i in range(java_list.size()):
                python_list.append(str(java_list.get(i)))

            return python_list

        except Exception as e:
            self.ctx.logger.warning(f"Failed to convert Java list: {str(e)}")
            return []


    def _show_testing_status(self) -> None:
        """Show testing status message in CLI"""

        try:
            print("\n" + "="*50)
            print("   TESTING IN PROGRESS...")
            print("   Please follow the instructions displayed below.")
            print("="*50 + "\n")

        except Exception as e:
            # Don't raise error for status display - it's not critical:
            self.ctx.logger.warning(f"Failed to show testing status: {str(e)}")


    def _ask_continue_or_exit(self) -> bool:
        """Ask user whether to continue with another test or exit application"""

        try:
            print("\n" + "="*50)
            print("   TESTING COMPLETED")
            print("="*50)

            while True:
                try:
                    choice = input("\nDo you want to start another test? (y/n): ").strip().lower()

                    if choice in ['y', 'yes', 'da']:
                        return True
                    elif choice in ['n', 'no', 'nu']:
                        return False
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")

                except KeyboardInterrupt:
                    print("\nExiting application...")
                    return False
                except EOFError:
                    print("\nInput stream closed. Exiting application...")
                    return False

        except Exception as e:
            error_msg = f"Error asking user for continuation: {str(e)}"
            self.ctx.logger.error(error_msg)
            # Default to exit on error:
            return False


    def get_queued_data(self) -> Optional[dict]:
        """Get data from the queue (non-blocking) - for compatibility"""

        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None


    def is_session_active(self) -> bool:
        """Check if CLI session is still active and user wants to continue"""

        return self.session_active and self.continue_testing


    def wants_to_continue(self) -> bool:
        """Check if user wants to continue testing"""

        return self.continue_testing


    def __enter__(self):
        """Context manager entry"""

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self.cleanup()

#%%