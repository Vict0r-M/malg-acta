"""GUI bridge - JavaFX GUI input strategy"""

#%% Dependencies:

import time
import json
import queue
import threading
from typing import Any
from pathlib import Path
from datetime import datetime

import jpype
from jpype.types import *

#%% GUI Bridge Strategy (Implements InputStrategy):

class GUIBridge:
    """GUI input strategy implementation using JavaFX and JPype1"""

    def __init__(self):
        """Initialize GUI bridge with default state"""
        
        self.ctx = None
        self.data_queue = queue.Queue()
        self.app_instance = None
        self.callback_registered = False
        self.jvm_started = False



    def setup(self, ctx: Any) -> None:  # Context object containing logger, config, errors, typing
        """Setup GUI bridge with malg-acta context and initialize JavaFX application"""

        self.ctx = ctx

        try:
            self.ctx.logger.info("Setting up GUI bridge...")

            # Start JVM:
            self._start_jvm()

            # Launch JavaFX application:
            self._launch_gui()

            # Setup data submission callback:
            self._setup_callback()

            self.ctx.logger.info("GUI bridge setup completed successfully")

        except Exception as e:
            error_msg = f"Failed to setup GUI bridge: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def get_user_input(self) -> dict:
        """Get user input through GUI interface. Waits for user to submit data"""

        try:
            self.ctx.logger.info("GUI ready for user input", target="user")

            # Clear any previous data in queue:
            while not self.data_queue.empty():
                try:
                    self.data_queue.get_nowait()
                except queue.Empty:
                    break

            # Wait for user submission:
            while True:
                try:
                    # Check if GUI is still running with debug info:
                    if self.app_instance:
                        is_running = self.app_instance.isRunning()
                        self.ctx.logger.info(f"DEBUG: GUI isRunning() = {is_running}")
                        if not is_running:
                            error_msg = "GUI application was closed by user"
                            self.ctx.logger.error(error_msg)
                            raise self.ctx.errors.ValidationError(error_msg)
                    else:
                        error_msg = "GUI app_instance is None"
                        self.ctx.logger.error(error_msg)
                        raise self.ctx.errors.ValidationError(error_msg)

                    # Check for submitted data with timeout:
                    try:
                        submitted_data = self.data_queue.get(timeout=1.0)
                        self.ctx.logger.info("User submitted data through GUI")

                        # Interface submission completed:
                        return submitted_data['data']

                    except queue.Empty:
                        continue  # Continue waiting for input:

                except KeyboardInterrupt:
                    error_msg = "User interrupted GUI input"
                    self.ctx.logger.info(error_msg)
                    raise self.ctx.errors.ValidationError(error_msg)

        except Exception as e:
            if isinstance(e, (self.ctx.errors.ValidationError, self.ctx.errors.DeviceError)):
                raise
            error_msg = f"GUI input failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def unlock_interface(self) -> None:
        """Unlock GUI interface after testing completes. Ready for next testing cycle"""

        try:
            self.ctx.logger.info("Unlocking GUI interface for next cycle")
            self.ctx.logger.info("GUI interface ready for next cycle", target="user")

        except Exception as e:
            error_msg = f"Failed to unlock GUI interface: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def log_to_gui(self, level: str,      # Log level (INFO, WARNING, ERROR, etc.)
                   message: str,          # Message to log
                   timestamp: str = None  # Optional timestamp (uses current time if None)
                  ) -> None:
        """Log a message to the GUI logger panel"""

        try:
            if self.app_instance:
                if timestamp is None:
                    timestamp = datetime.now().isoformat()

                self.app_instance.logMessage(level, message, timestamp)

        except Exception as e:
            # If GUI logging fails, don't raise error, just warn developers:
            if self.ctx:
                self.ctx.logger.warning(f"Failed to log to GUI: {str(e)}")


    def cleanup(self) -> None:
        """Clean shutdown of GUI and JVM resources"""

        try:
            if self.ctx:
                self.ctx.logger.info("Shutting down GUI bridge...")

            # Close GUI application:
            if self.app_instance:
                self.app_instance.closeApplication()
                self.app_instance = None

            # Shutdown JVM:
            if self.jvm_started and jpype.isJVMStarted():
                jpype.shutdownJVM()
                self.jvm_started = False

            if self.ctx:
                self.ctx.logger.info("GUI bridge shutdown completed")

        except Exception as e:
            if self.ctx:
                self.ctx.logger.warning(f"Error during GUI bridge cleanup: {str(e)}")


    def _start_jvm(self) -> None:
        """Start JVM with proper classpath and JavaFX module configuration"""

        if self.jvm_started:
            return

        try:
            # Determine paths relative to malg-acta project root:
            gui_app_path = Path(__file__).parent / "gui-app"

            classpath = [str(gui_app_path / "target" / "classes"),
                         str(gui_app_path / "target" / "dependency" / "*")]

            # JavaFX module path for Windows/cross-platform compatibility:
            module_path = str(gui_app_path / "target" / "dependency")

            self.ctx.logger.info(f"Starting JVM with classpath: {classpath}")
            self.ctx.logger.info(f"JavaFX module path: {module_path}")

            # Apply retry logic from config:
            retry_count = getattr(self.ctx.config.input, 'retry_count', 3)

            for attempt in range(retry_count):
                try:
                    # Start JVM with JavaFX module configuration:
                    jpype.startJVM(# JVM arguments come first (positional):
                                   "-Djava.awt.headless=false",  # Ensure GUI mode
                                   f"--module-path={module_path}",
                                   "--add-modules=javafx.controls", 
                                   # Suppress JavaFX warnings on newer Java versions:
                                   "--add-exports=javafx.graphics/com.sun.javafx.application=ALL-UNNAMED",
                                   # Keyword arguments come last:
                                   classpath=classpath)

                    self.jvm_started = True
                    self.ctx.logger.info("JVM started successfully with JavaFX modules")
                    return

                except Exception as e:
                    if attempt == retry_count - 1:
                        raise
                    self.ctx.logger.warning(f"JVM start attempt {attempt + 1} failed: {str(e)}, retrying...")
                    time.sleep(1)  # Brief delay before retry

        except Exception as e:
            error_msg = f"Failed to start JVM with JavaFX: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _launch_gui(self) -> None:
        """Launch JavaFX GUI application"""

        try:
            # Load the AppController class:
            self.ctx.logger.info("Loading AppController class...")
            AppController = jpype.JClass("com.malg_acta.gui_app.AppController")

            # Launch the JavaFX application in background thread:
            self.ctx.logger.info("Launching JavaFX application...")
            javafx_thread = threading.Thread(target=AppController.launchApp, daemon=True)
            javafx_thread.start()

            # Wait for GUI instance creation with timeout and retry logic:
            retry_count = getattr(self.ctx.config.input, 'retry_count', 3)
            max_wait_time = retry_count * 2  # 2 seconds per retry

            for attempt in range(max_wait_time):
                self.ctx.logger.info(f"Waiting for GUI instance creation... "
                                      "(attempt {attempt + 1}/{max_wait_time})")
                time.sleep(1)

                self.app_instance = AppController.getInstance()
                if self.app_instance is not None:
                    break

            if self.app_instance is None:
                error_msg = f"Failed to get GUI application instance after {max_wait_time} attempts"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.DeviceError(error_msg)

            # Wait for GUI to actually start running (fix race condition):
            self.ctx.logger.info("GUI instance created, waiting for startup...")
            for startup_attempt in range(5):  # 5 second timeout for startup
                time.sleep(1)
                try:
                    if self.app_instance.isRunning():
                        self.ctx.logger.info(f"GUI application started successfully, isRunning() = True")
                        return  # Success - GUI is fully running
                except Exception as e:
                    self.ctx.logger.warning(f"Error checking GUI running status: {str(e)}")
                    continue

            # GUI instance exists but not running - warn but don't fail
            self.ctx.logger.warning("GUI instance created but not running after 5 seconds")
            try:
                is_running = self.app_instance.isRunning()
                self.ctx.logger.info(f"Final GUI status check: isRunning() = {is_running}")
            except Exception as e:
                self.ctx.logger.warning(f"Could not check final GUI running status: {str(e)}")

        except Exception as e:
            error_msg = f"Failed to launch GUI: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _setup_callback(self) -> None:
        """Setup data submission callback with the Java application"""

        if not self.app_instance or self.callback_registered:
            return

        try:
            # Create Java Runnable from Python function:
            java_callback = jpype.JProxy("java.lang.Runnable", dict(run=self._data_submitted_callback))

            # Register callback with Java application:
            self.app_instance.setOnDataSubmittedCallback(java_callback)
            self.callback_registered = True

            self.ctx.logger.info("Data submission callback registered successfully")

        except Exception as e:
            error_msg = f"Failed to register callback: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.DeviceError(error_msg)


    def _data_submitted_callback(self) -> None:
        """Internal callback function called when user submits data in GUI"""

        try:
            self.ctx.logger.info("User submitted data in GUI - retrieving...")

            # Get JSON string from Java:
            java_string = self.app_instance.getData()
            json_string = str(java_string)

            # Parse JSON to dictionary:
            data_dict = json.loads(json_string)

            self.ctx.logger.info("Data retrieved successfully from GUI")
            self.log_to_gui("INFO", f"Data submitted: {data_dict.get('set_id', 'Unknown ID')}")

            # Put data in queue for processing:
            self.data_queue.put({'timestamp': datetime.now().isoformat(), 'data': data_dict})

        except Exception as e:
            error_msg = f"Error in data submission callback: {str(e)}"
            self.ctx.logger.error(error_msg)
            self.log_to_gui("ERROR", error_msg)


    def __enter__(self):
        """Context manager entry"""

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self.cleanup()

#%%