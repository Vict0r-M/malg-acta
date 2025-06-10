"""
Malg-ACTA Entry Point
Run with: python main.py --config configs/app_config.yaml
"""

#%% Standard Dependencies:

import sys
import yaml
import atexit
import argparse
from box import Box
from pathlib import Path
from typing import Tuple, Any

#%% Setup functions:

def load_dependencies(logger: Any) -> Tuple[Any, Any, Any, Any]:
    """Import required modules"""

    try:
        # Import utility modules:
        from app_modules.utils.config_loader import load_config
        from app_modules.utils import custom_typing, custom_errors

        # Import core modules:
        from app_modules.core.plugin_manager import PluginManager
        from app_modules.core.state_machine import StateMachine

        logger.info("Successfully imported required modules")
        return (custom_typing, custom_errors, load_config, PluginManager, StateMachine)

    except Exception as e:
        logger.critical(f"Failed to import required modules: {str(e)}")
        sys.exit(1)


def load_state_modules(logger: Any) -> Tuple[Any, Any, Any, Any, Any]:
    """Import all state modules directly"""

    try:
        # Import all state implementations:
        from app_modules.states.idle_state import IdleState
        from app_modules.states.input_state import InputState
        from app_modules.states.acquisition_state import AcquisitionState
        from app_modules.states.dissemination_state import DisseminationState
        from app_modules.states.error_state import ErrorState

        logger.info("Successfully imported all state modules")
        return (IdleState, InputState, AcquisitionState, DisseminationState, ErrorState)

    except Exception as e:
        logger.critical(f"Failed to import state modules: {str(e)}")
        sys.exit(1)


def load_data_models(logger: Any) -> Tuple[Any]:
    """Import data model modules"""

    try:
        # Import data models:
        from app_modules.models.input_data import InputData

        logger.info("Successfully imported data models")
        return (InputData,)

    except Exception as e:
        logger.critical(f"Failed to import data models: {str(e)}")
        sys.exit(1)


def load_interface_modules(logger: Any) -> Tuple[Any]:
    """Import interface modules"""

    try:
        # Import interface modules:
        from app_modules.input.input_interface import InputInterface

        logger.info("Successfully imported interface modules")
        return (InputInterface,)

    except Exception as e:
        logger.critical(f"Failed to import interface modules: {str(e)}")
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


def initialize_plugin_manager(ctx: Any, PluginManager: type) -> Any:
    """Initialize plugin manager with plugin configuration"""

    try:
        ctx.logger.info("Initializing plugin manager...")

        # Load plugin configuration:
        plugin_config_path = ctx.config.plugins.config_path

        with open(plugin_config_path, 'r', encoding='utf-8') as f:
            plugin_config_raw = yaml.safe_load(f)

        plugin_config = Box(plugin_config_raw)

        # Create plugin manager:
        plugin_manager = PluginManager(ctx, plugin_config)

        ctx.logger.info("Plugin manager initialized successfully")
        return plugin_manager

    except Exception as e:
        error_msg = f"Failed to initialize plugin manager: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def initialize_input_interface(ctx: Any, plugin_manager: Any, input_data_class: type, InputInterface: type) -> Any:
    """Initialize input interface with proper plugin strategy"""

    try:
        ctx.logger.info("Initializing input interface...")

        # Create input interface with dependency injection:
        input_interface = InputInterface(ctx, input_data_class, plugin_manager)

        ctx.logger.info("Input interface initialized successfully")
        return input_interface

    except Exception as e:
        error_msg = f"Failed to initialize input interface: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def create_state_instances(ctx: Any, 
                           input_interface: Any, 
                           IdleState: type, 
                           InputState: type, 
                           AcquisitionState: type,
                           DisseminationState: type, 
                           ErrorState: type) -> Tuple[Any, Any, Any, Any, Any]:
    """Create all state instances with proper dependency injection"""

    try:
        ctx.logger.info("Creating state instances...")

        # Create state instances with dependency injection:
        idle_state = IdleState()
        input_state = InputState(input_interface)
        acquisition_state = AcquisitionState()  # Mock implementation needs no dependencies
        dissemination_state = DisseminationState()  # Mock implementation needs no dependencies
        error_state = ErrorState()

        # Set input interface reference in states that need session management:
        idle_state.set_input_interface(input_interface)
        dissemination_state.set_input_interface(input_interface)

        ctx.logger.info("All state instances created successfully")
        return (idle_state, input_state, acquisition_state, dissemination_state, error_state)

    except Exception as e:
        error_msg = f"Failed to create state instances: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def initialize_state_machine(ctx: Any, 
                             idle_state: Any, 
                             input_state: Any, 
                             acquisition_state: Any,
                             dissemination_state: Any, 
                             error_state: Any,
                             StateMachine: type) -> Any:
    """Initialize state machine with all state instances"""

    try:
        ctx.logger.info("Initializing state machine...")

        # Create state machine with injected states:
        state_machine = StateMachine(ctx=ctx,
                                     idle_state=idle_state,
                                     input_state=input_state,
                                     acquisition_state=acquisition_state,
                                     dissemination_state=dissemination_state,
                                     error_state=error_state)

        ctx.logger.info("State machine initialized successfully")
        return state_machine

    except Exception as e:
        error_msg = f"Failed to initialize state machine: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.StateMachineError(error_msg)

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
    custom_typing, custom_errors, load_config, PluginManager, StateMachine = load_dependencies(logger)

    # Load state modules:
    IdleState, InputState, AcquisitionState, DisseminationState, ErrorState = load_state_modules(logger)

    # Load data models:
    InputData, = load_data_models(logger)

    # Load interface modules:
    InputInterface, = load_interface_modules(logger)

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

        # Initialize core components:
        ctx.logger.info("Malg-ACTA system initialization starting...")

        # Initialize plugin manager:
        plugin_manager = initialize_plugin_manager(ctx, PluginManager)

        # Initialize input interface:
        input_interface = initialize_input_interface(ctx, plugin_manager, InputData, InputInterface)

        # Create all state instances:
        idle_state, input_state, acquisition_state, dissemination_state, error_state = create_state_instances(
            ctx, input_interface, IdleState, InputState, AcquisitionState, DisseminationState, ErrorState)

        # Initialize state machine:
        state_machine = initialize_state_machine(
            ctx, idle_state, input_state, acquisition_state, dissemination_state, error_state, StateMachine)

        ctx.logger.info("Malg-ACTA system initialized successfully")
        ctx.logger.info_with_newline("Starting application...")

        # Start the main application:
        run_application(ctx, state_machine, input_interface)

    except custom_errors.ApplicationError as e:
        ctx.logger.exception(f"Malg-ACTA error during startup: {str(e)}")
        sys.exit(1)

    except Exception as e:
        ctx.logger.exception(f"Unexpected error during startup: {str(e)}")
        sys.exit(1)


def run_application(ctx: Any, state_machine: Any, input_interface: Any) -> None:
    """Run the main application with proper resource management"""

    try:
        ctx.logger.info("Starting Malg-ACTA application...")
        ctx.logger.info("=== MALG-ACTA v1.0.0 ===", target="user")
        ctx.logger.info("Sistem automatizat pentru testarea materialelor de construcție", target="user")
        ctx.logger.info("Application ready", target="user")

        # Use context managers for proper cleanup:
        with state_machine, input_interface:
            # Start the state machine (this blocks until application exit):
            state_machine.start()

        ctx.logger.info("Application shutdown completed successfully")

    except KeyboardInterrupt:
        ctx.logger.info("Application interrupted by user (Ctrl+C)")
        ctx.logger.info("Shutting down gracefully...")

    except ctx.custom_errors.ApplicationError as e:
        ctx.logger.exception(f"Application error: {str(e)}")
        ctx.logger.error("Application terminated due to error", target="user")

    except Exception as e:
        ctx.logger.exception(f"Unexpected application error: {str(e)}")
        ctx.logger.error("Application terminated unexpectedly", target="user")

    finally:
        ctx.logger.info("Malg-ACTA application shutdown")

#%% Entry point:

if __name__ == "__main__":
    main()

#%%