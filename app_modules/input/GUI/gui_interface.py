import jpype
import jpype.imports
from jpype.types import *
import os
import time
import threading
import queue
from datetime import datetime
import json


class PythonGUIInterface:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.app_instance = None
        self.callback_registered = False


    def data_submitted_callback(self):
        """Callback function called when submit button is pressed"""
        try:
            print("\nSubmit button pressed - retrieving data...")

            # Get JSON string from Java
            java_string = self.app_instance.getData()

            # Convert Java String to Python string
            json_string = str(java_string)

            # Parse JSON to dictionary
            data_dict = json.loads(json_string)

            print(data_dict)
            print(f"NEW DATA SUBMITTED: {data_dict}")

            # Put data in queue for other parts of the program to process
            # self.data_queue.put({
            #     'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            #     'data': data
            # })

        except Exception as e:
            print(f"Error in callback: {e}")
            import traceback
            traceback.print_exc()

    def setup_callback(self):
        """Set up the callback with the Java application"""
        if self.app_instance and not self.callback_registered:
            try:
                # Create a Java Runnable from our Python function
                java_callback = jpype.JProxy("java.lang.Runnable", dict(run=self.data_submitted_callback))

                # Register the callback with the Java application
                self.app_instance.setOnDataSubmittedCallback(java_callback)
                self.callback_registered = True
                print("Callback registered successfully!")

            except Exception as e:
                print(f"Failed to register callback: {e}")

    def log_with_timestamp(self, level, message, timestamp=None):
        """
        Log a message with custom timestamp

        Args:
            message (str): The message to log
            level (str): Log level
            timestamp (str): ISO format timestamp (optional, uses current time if None)
        """

        try:
            if self.app_instance:
                if timestamp is None:
                    #timestamp = time.strftime('%H:%M:%S')
                    timestamp = datetime.now().isoformat()

                self.app_instance.logMessage(level, message, timestamp)
                print(f"Logged to GUI [{level}]: {message}")
            else:
                print(f"Cannot log to GUI - no app instance. Message: [{level}] {message}")
        except Exception as e:
            print(f"Failed to log to GUI: {e}")
            print(f"Original message: [{level}] {message}")

    def test_logging(self):
        """Test method to demonstrate all logging levels"""

        print("Testing GUI logging...")

        self.log_with_timestamp("INFO", "This is an INFO message")

        self.log_with_timestamp("WARNING", "This is a WARNING message")

        self.log_with_timestamp("ERROR", "This is an ERROR message")

    def run_interactive_mode(self):
        while True:
            try:
                if not self.app_instance.isRunning():
                    print("GUI application has been closed by user")
                    break

            except KeyboardInterrupt:
                print("\nReturning to command mode...")
                continue
            except EOFError:
                print("\nInput stream closed, shutting down...")
                break


def main():
    interface = PythonGUIInterface()

    # Start JVM with the JAR
    try:
        jpype.startJVM(classpath=[
            'gui-app/target/classes',
            'gui-app/target/dependency/*'
        ])
        print("JVM started successfully")
    except Exception as e:
        print(f"Failed to start JVM: {e}")
        return

    try:
        # Load the controllable JavaFX application
        print("Loading AppController class...")
        AppController = jpype.JClass("com.malg_acta.gui_app.AppController")
        print("AppController class loaded successfully")

        # Launch the JavaFX application in background thread
        print("Launching JavaFX application...")
        javafx_thread = threading.Thread(target=AppController.launchApp, daemon=True)
        javafx_thread.start()
        print("JavaFX application thread started!")

        # Wait for the GUI to initialize
        print("Waiting for GUI to initialize...")
        time.sleep(5)

        # Get the application instance
        app_instance = AppController.getInstance()
        retry_count = 0
        while app_instance is None and retry_count < 10:
            print(f"Waiting for application instance... (attempt {retry_count + 1})")
            time.sleep(2)
            app_instance = AppController.getInstance()
            retry_count += 1

        if app_instance is None:
            print("Failed to get application instance after multiple attempts")
            return

        print("Got application instance - GUI should be visible now!")

        # Set up the interface
        interface.app_instance = app_instance
        interface.test_logging()

        interface.setup_callback()

        interface.run_interactive_mode()

    except jpype.JException as je:
        print(f"Java exception occurred: {je}")
        if hasattr(je, 'stacktrace'):
            print(f"Java stack trace: {je.stacktrace()}")
    except Exception as e:
        print(f"Python exception occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            print("JVM shutdown completed")

if __name__ == "__main__":
    main()