"""
Malg-ACTA Entry Point
Materials Testing Automation System
"""

#%% Standard Dependencies:

import sys
import atexit
import argparse
from pathlib import Path
from typing import Tuple, Any

#%% Setup Functions:

def load_dependencies(logger: Any) -> Tuple[Any, Any, Any, Any, Any, Any, Any]:
    """Import required modules"""
    
    try:
        # Utils:
        from app_modules.utils.config_loader import load_config
        from app_modules.utils import custom_typing, custom_errors
        
        # Core components:
        from app_modules.core.state_machine import StateMachine
        from app_modules.bridges.java_bridge import JavaBridge
        from app_modules.data_storage.data_managers import ClientsManager, ConcreteClassesManager, RegistryManager
        
        logger.info("Successfully imported required modules")
        return (custom_typing, custom_errors, load_config, StateMachine, 
                JavaBridge, ClientsManager, ConcreteClassesManager)
        
    except Exception as e:
        logger.critical(f"Failed to import required modules: {str(e)}")
        sys.exit(1)

def parse_arguments(default_config_path: Path) -> Tuple[Path, str]:
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(description="Malg-ACTA Materials Testing System")
    parser.add_argument("--config", type=str,
                       help=f"Path to configuration file (default: {default_config_path})")
    parser.add_argument("--input", type=str, choices=["cli", "gui"], default="cli",
                       help="Input method: cli or gui (default: cli)")
    args = parser.parse_args()
    
    # Get config path from command line arguments or use default:
    config_path = Path(args.config) if args.config else default_config_path
    return config_path, args.input

#%% Orchestrator:

def main() -> None:
    """Initialize and run the Malg-ACTA system"""
    
    # Initialization constants:
    project_root = Path(__file__).parent
    init_error_logpath = project_root / "logs" / "init_error.log"
    config_error_logpath = project_root / "logs" / "config_error.log"
    default_config_path = project_root / "configs" / "app_config.yaml"
    
    # Initialize logger first:
    try:
        from app_modules.utils.custom_logging import Logger
        
        # Create initial logger to capture startup errors:
        logger = Logger(logpath=init_error_logpath, console_enabled=True)
        
        # Register cleanup:
        atexit.register(logger.close_handlers)
        
        # Log startup:
        logger.info("Malg-ACTA Materials Testing System starting")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize logger: {str(e)}")
        sys.exit(1)
    
    # Load dependencies:
    custom_typing, custom_errors, load_config, StateMachine, JavaBridge, ClientsManager, ConcreteClassesManager = load_dependencies(logger)
    
    # Create context:
    try:
        ctx = custom_typing.Context(
            typing=custom_typing, 
            errors=custom_errors, 
            logger=logger,
            config=None
        )
        
    except Exception as e:
        logger.critical(f"Failed to create context: {str(e)}")
        sys.exit(1)
    
    # Parse arguments:
    config_path, input_method = parse_arguments(default_config_path)
    
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
        ctx.logger.info("Initialization complete")
        
        # Initialize data managers:
        clients_manager = ClientsManager(ctx)
        concrete_manager = ConcreteClassesManager(ctx)
        
        # Create Java bridge:
        java_bridge = JavaBridge(ctx)
        
        # Create and run state machine:
        state_machine = StateMachine(ctx, java_bridge)
        
        # Run demo workflow:
        ctx.logger.info(f"Starting demo workflow with {input_method} input method")
        success = state_machine.run_demo_workflow(input_method)
        
        if success:
            ctx.logger.info("Demo workflow completed successfully!")
            print("\n=== Demo Workflow Completed Successfully! ===")
            print("Check the data/reports directory for generated files.")
        else:
            ctx.logger.error("Demo workflow failed")
            print("\n=== Demo Workflow Failed ===")
            print("Check the logs for error details.")
            sys.exit(1)
            
    except custom_errors.MalgActaError as e:
        ctx.logger.exception(f"Error during processing: {str(e)}")
        sys.exit(1)
        
    except Exception as e:
        ctx.logger.exception(f"Unexpected error during processing: {str(e)}")
        sys.exit(1)

#%% Entry Point:

if __name__ == "__main__":
    main()

#%%