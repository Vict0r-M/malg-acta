"""Idle state - waiting for user interaction"""

#%% Dependencies:

import time
from typing import Any, Tuple

#%% Idle State:

class IdleState:
    """
    Idle state: waits for user to start testing workflow
    This is the default state when application starts or after testing completes
    """

    def __init__(self, input_interface: Any = None):
        """Initialize idle state with optional input interface reference"""
        self.state_name = "idle_state"
        self.waiting_for_input = False
        self.input_interface = input_interface
        self._queued_data = None  # Store GUI data that was submitted

    def set_input_interface(self, input_interface: Any) -> None:
        """Set input interface reference after construction"""
        self.input_interface = input_interface

    def enter(self, ctx: Any, data: Any = None) -> None:
        """
        Enter idle state - system is ready for user interaction
        Args:
            ctx: Context object
            data: Optional data from previous state (usually None for idle)
        """
        try:
            ctx.logger.info("Entering idle state - system ready")
            
            # Handle data from previous state:
            if data:
                # If coming from dissemination state, testing completed successfully:
                if isinstance(data, dict) and data.get("testing_completed"):
                    ctx.logger.info("Testing cycle completed successfully", target="user")
                    ctx.logger.info("Ready for next testing cycle", target="user")
                # If coming from error state, show recovery message:
                elif isinstance(data, dict) and data.get("recovered_from_error"):
                    ctx.logger.info("System recovered from error", target="user")
                    ctx.logger.info("Ready to resume operations", target="user")

            # Reset waiting flag:
            self.waiting_for_input = True
            
            # Log readiness:
            ctx.logger.info("System is idle and ready for testing", target="user")

        except Exception as e:
            error_msg = f"Error entering idle state: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.StateMachineError(error_msg)

    def execute(self, ctx: Any) -> Tuple[str, Any]:
        """
        Execute idle state logic - wait for user to trigger input collection
        Args:
            ctx: Context object
        Returns:
            Tuple: (next_state_name, data_for_next_state)
        """
        try:
            # For persistent session model, we check if input interface
            # has work to do rather than blocking indefinitely
            
            while self.waiting_for_input:
                try:
                    # Check for user input trigger (this depends on input method):
                    trigger_result = self._check_for_user_trigger(ctx)
                    
                    if trigger_result == "start_testing":
                        ctx.logger.info("User initiated testing workflow")
                        self.waiting_for_input = False
                        # Pass any queued data to input state
                        data_to_pass = getattr(self, '_queued_data', None)
                        self._queued_data = None  # Clear queued data
                        return ("input_state", data_to_pass)
                    elif trigger_result == "exit_application":
                        # User wants to exit (GUI closed or CLI exit choice)
                        ctx.logger.info("User requested application exit")
                        self.waiting_for_input = False
                        return ("stop", None)
                    # If trigger_result == "wait", continue waiting
                    
                    # Brief sleep to prevent busy waiting:
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully:
                    ctx.logger.info("User requested application shutdown")
                    return ("stop", None)
                    
                except Exception as e:
                    # Handle errors by transitioning to error state:
                    error_obj = ctx.errors.StateMachineError(f"Error in idle state: {str(e)}")
                    return ("error_state", {"error": error_obj, "source_state": "idle_state"})

            # If we exit the loop without user trigger, something went wrong:
            return ("error_state", {
                "error": ctx.errors.StateMachineError("Idle state exited unexpectedly"),
                "source_state": "idle_state"
            })

        except Exception as e:
            error_msg = f"Critical error in idle state execution: {str(e)}"
            ctx.logger.error(error_msg)
            error_obj = ctx.errors.StateMachineError(error_msg)
            return ("error_state", {"error": error_obj, "source_state": "idle_state"})

    def exit(self, ctx: Any) -> None:
        """
        Exit idle state
        Args:
            ctx: Context object
        """
        try:
            ctx.logger.info("Exiting idle state")
            self.waiting_for_input = False

        except Exception as e:
            ctx.logger.warning(f"Error exiting idle state: {str(e)}")

    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """
        Check if transition to target state is allowed from idle
        Args:
            ctx: Context object
            target_state: Name of target state
        Returns:
            bool: True if transition is allowed
        """
        # From idle, we can go to input_state or error_state:
        allowed_transitions = ["input_state", "error_state"]
        return target_state in allowed_transitions

    def _check_for_user_trigger(self, ctx: Any) -> str:
        """
        Check if user has triggered the start of testing workflow or wants to exit
        Args:
            ctx: Context object
        Returns:
            str: "start_testing", "exit_application", or "wait"
        """
        try:
            # Get input method from config:
            input_method = ctx.config.input.method
            
            if input_method == "gui":
                # For GUI: Check if GUI is still running and if data was submitted
                if self.input_interface and hasattr(self.input_interface, 'strategy'):
                    strategy = self.input_interface.strategy
                    if hasattr(strategy, 'app_instance') and strategy.app_instance:
                        try:
                            is_running = strategy.app_instance.isRunning()
                            if not is_running:
                                ctx.logger.info("GUI was closed by user")
                                return "exit_application"  # User closed GUI - exit application
                        except Exception:
                            # If we can't check GUI status, assume it's still running
                            pass
                    
                    # Check if user has submitted data (check the queue):
                    if hasattr(strategy, 'data_queue') and not strategy.data_queue.empty():
                        # Get the submitted data from queue
                        try:
                            submitted_data = strategy.data_queue.get_nowait()
                            # Store the data to pass to input state
                            self._queued_data = submitted_data
                            return "start_testing"  # User submitted data, start testing
                        except:
                            pass  # Queue empty, continue waiting
                
                # GUI is running but no data submitted yet, keep waiting
                return "wait"
                
            elif input_method == "cli":
                # For CLI: Check if CLI session is still active
                if self.input_interface and hasattr(self.input_interface, 'strategy'):
                    strategy = self.input_interface.strategy
                    if hasattr(strategy, 'is_session_active'):
                        is_active = strategy.is_session_active()
                        if not is_active:
                            ctx.logger.info("User chose to exit application")
                            return "exit_application"  # User chose to exit
                # CLI session is active, ready for input
                return "start_testing"
                
            else:
                ctx.logger.warning(f"Unknown input method: {input_method}")
                return "exit_application"
                
        except Exception as e:
            ctx.logger.warning(f"Error checking user trigger: {str(e)}")
            return "wait"  # Default to wait on error

#%%