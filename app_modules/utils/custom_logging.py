"""Logging formatting and management"""

#%% Dependencies:

import os
import sys
import shutil
import logging
import traceback
from pathlib import Path
from typing import Any, Optional, Dict

#%% Custom Exception Handler:

class FileExceptionHandler:
    def __init__(self, logpath: Path) -> None:
        """Custom sys.excepthook to redirect all uncaught exceptions to log file"""

        self.logpath = logpath
        self._original_excepthook = sys.excepthook


    def __call__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        """Handle uncaught exception by writing to log file"""

        try:
            # Format exception information:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_message = ''.join(tb_lines)

            # Write to log file:
            with open(self.logpath, 'a', encoding='utf-8', errors='replace') as f:
                f.write(f"UNCAUGHT EXCEPTION: {error_message}\n")

        except Exception:
            # If logging fails, fall back to original excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)

#%% Main Logging Manager:

class Logger:
    def __init__(self, logpath: Path = Path("logs/init_error.log"), 
                 console_enabled: bool = False) -> None:
        """Manages logging setup with file renaming capability"""

        # Set initial properties:
        self._path = logpath
        self._console_enabled = console_enabled
        self._file_handlers: Dict[str, logging.FileHandler] = {}
        self._error_handler: Optional[FileExceptionHandler] = None
        self._logger: Optional[logging.Logger] = None

        # User messaging setup:
        self.user_message_handler = None

        # Setup initial logging:
        self._first_setup = True
        self._setup_logger()


    def _setup_logger(self) -> None:
        """Internal method to set up the logger with current settings"""

        # Ensure log directory exists:
        self._path.parent.mkdir(parents=True, exist_ok=True)

        # Create or get the logger:
        if self._logger is None:
            self._logger = logging.getLogger('malg_acta')
            self._logger.setLevel(logging.INFO)
            self._logger.propagate = False  # Prevent logs from propagating to the root logger

        # Close and remove any existing handlers:
        for handler in self._logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
            self._logger.removeHandler(handler)

        # Create formatter for detailed output:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                                      datefmt='%d.%m.%Y %H:%M:%S')

        mode = 'w' if self._first_setup else 'a'
        self._first_setup = False

        # Add file handler and clear it's contents if it already exists:
        file_handler = logging.FileHandler(self._path, encoding='utf-8', errors='replace', mode=mode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self._logger.addHandler(file_handler)

        # Add console handler if enabled:
        if self._console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            self._logger.addHandler(console_handler)

        # Install error handler if not already installed:
        if self._error_handler is None:
            self._error_handler = FileExceptionHandler(self._path)
            sys.excepthook = self._error_handler
        else:
            self._error_handler.logpath = self._path


    def rename_logfile(self, logpath: Path) -> None:
        """Change the log file by creating a new file, copying content, and removing old file"""

        if logpath == self._path:
            return  # No change needed

        # Make sure all pending log messages are written and handlers are closed:
        for handler in self._logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
                self._logger.removeHandler(handler)  # Accumulate console handlers

        # Copy content from old to new if old file exists:
        copy_error = None
        deletion_error = None
        if self._path.exists():
            # Ensure directory exists for new log file:
            logpath.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(self._path, 'r', encoding='utf-8', errors='replace') as src:
                    with open(logpath, 'w', encoding='utf-8', errors='replace') as dst:
                        shutil.copyfileobj(src, dst)
            except Exception as e:
                # Store error for later logging (can't log now as handlers are closed):
                copy_error = str(e)

            # Remove old log file:
            try:
                os.remove(self._path)
            except Exception as e:
                deletion_error = str(e)

        # Update log file path:
        self._path = logpath

        # Update error handler:
        if self._error_handler:
            self._error_handler.logpath = logpath

        # Reconfigure logger:
        self._setup_logger()

        if copy_error:
            # Critical error - log to new file and exit:
            self.critical(f"Failed to copy log file: {copy_error}")
            sys.exit(1)
        else:
            # Log error deleting the old file as warning:
            if deletion_error:
                self.warning(f"Failed to delete old log file: {deletion_error}")


    def set_console_enabled(self, console_enabled: bool) -> None:
        """Enable or disable console output"""

        if console_enabled == self._console_enabled:
            return  # No change needed

        self._console_enabled = console_enabled

        # Reconfigure logger:
        self._setup_logger()

        # Log the change:
        self.info(f"Console output {'enabled' if console_enabled else 'disabled'}")


    def _log_with_target(self, level: str, message: str, target: str) -> None:
        """Route log message based on target"""

        if target in ["dev", "both"]:
            log_method = getattr(self._logger, level)
            log_method(message, stacklevel=3)

        if target in ["user", "both"] and self.user_message_handler is not None:
            try:
                self.user_message_handler(level.upper(), message)
            except Exception as e:
                # If user messaging fails, log to dev channel:
                self._logger.warning(f"User message failed: {str(e)}")


    # Convenience methods to log messages:
    def info(self, message: str, target: str = "dev") -> None:
        """Log an info message with optional target routing"""

        self._log_with_target("info", message, target)


    def info_with_newline(self, message: str) -> None:
        """Log an info message with a newline before it (dev-only)"""

        # Add a blank record first:
        if self._logger and hasattr(self._logger, 'handlers'):
            for handler in self._logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.stream.write('\n')
                    handler.flush()

        # Log actual message:
        self._logger.info(message, stacklevel=2)


    def warning(self, message: str, target: str = "dev") -> None:
        """Log a warning message with optional target routing"""

        self._log_with_target("warning", message, target)


    def error(self, message: str, target: str = "dev") -> None:
        """Log an error message with optional target routing"""

        self._log_with_target("error", message, target)


    def critical(self, message: str, target: str = "dev") -> None:
        """Log a critical message with optional target routing"""

        self._log_with_target("critical", message, target)


    def exception(self, message: str, target: str = "dev") -> None:
        """Log an exception message with traceback"""

        if target == "dev":
            # For dev-only, use built-in exception logging with automatic traceback:
            self._logger.exception(message, stacklevel=2)
        else:
            # For user or both targets, manually format traceback and use _log_with_target:
            full_message = f"{message}\n{traceback.format_exc()}"
            self._log_with_target("error", full_message, target)


    def close_handlers(self) -> None:
        """Close all handlers properly"""

        if self._logger:
            for handler in self._logger.handlers:
                try:
                    handler.close()
                except:
                    pass

#%%