"""
Malg-ACTA Entry Point
Run with: python main.py --config configs/app_config.yaml
"""

#%% Standard Dependencies:

import sys
import atexit
import argparse
from pathlib import Path
from typing import Tuple, Any

#%% Setup functions:

def load_dependencies(logger: Any) -> Tuple[Any, Any, Any]:
    """Import required modules"""

    try:
        # Import utility modules:
        from app_modules.utils.config_loader import load_config
        from app_modules.utils import custom_typing, custom_errors

        # TODO: import core modules when implemented

        logger.info("Successfully imported required modules")
        return (custom_typing, custom_errors, load_config)

    except Exception as e:
        logger.critical(f"Failed to import required modules: {str(e)}")
        sys.exit(1)

def parse_arguments(default_config_path: Path) -> Path:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description="Malg-ACTA - Automated Construction Materials Testing")
    parser.add_argument("--config", type=str, 
                        help=f"Path to configuration file (default: {default_config_path})")
    args = parser.parse_args()

    # Get config path from command line arguments or use default:
    config_path = Path(args.config) if args.config else default_config_path
    return config_path

#%% Main Application Function:

def main() -> None:
    """Initialize and run the Malg-ACTA application"""

    # Initialization constants:
    project_root = Path(__file__).parent
    init_error_logpath = project_root / "logs" / "init_error.log"
    config_error_logpath = project_root / "logs" / "config_error.log"
    default_config_path = project_root / "configs" / "app_config.yaml"

    # Initialize logger first so we can log any errors:
    try:
        from app_modules.utils.custom_logging import Logger

        # Create initial logger to capture startup errors:
        logger = Logger(logpath=init_error_logpath, console_enabled=False)

        # Register cleanup to ensure log files are properly closed:
        atexit.register(logger.close_handlers)

        # Log startup:
        logger.info("Malg-ACTA starting...")

    except Exception as e:
        # If logging setup fails, print to console and exit:
        print(f"CRITICAL ERROR: Failed to initialize logger: {str(e)}")
        sys.exit(1)

    # Load dependencies after logger is ready:
    custom_typing, custom_errors, load_config = load_dependencies(logger)

    # Create context:
    try:
        ctx = custom_typing.Context(typing=custom_typing, errors=custom_errors, logger=logger)

    except Exception as e:
        logger.critical(f"Failed to create context: {str(e)}")
        sys.exit(1)

    # Parse command line arguments:
    config_path = parse_arguments(default_config_path)

    try:
        # Rename log file to capture config loading errors:
        ctx.logger.rename_logfile(config_error_logpath)

        # Load and validate configuration:
        ctx.config = load_config(config_path, ctx)
        ctx.logger.info(f"Configuration file {config_path} loaded and validated")

        # Update logger with final configuration:
        ctx.logger.rename_logfile(ctx.config.logging.path)
        ctx.logger.set_console_enabled(ctx.config.logging.console_enabled)
        ctx.logger.info("Logger configured with final settings")
        ctx.logger.info_with_newline("Initialization complete")

        # Application is ready - this is where the main application logic will go:
        ctx.logger.info("Malg-ACTA system initialized successfully")

        # TODO: when core modules are implemented, initialize and run them here

    except custom_errors.ApplicationError as e:
        ctx.logger.exception(f"Malg-ACTA error during startup: {str(e)}")
        sys.exit(1)

    except Exception as e:
        ctx.logger.exception(f"Unexpected error during startup: {str(e)}")
        sys.exit(1)

#%% Entry point:

if __name__ == "__main__":
    main()

#%%