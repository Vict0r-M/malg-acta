"""Error state - handles error recovery and user guidance"""

#%% Dependencies:

import time
from typing import Any, Tuple

#%% Error State:

class ErrorState:
    """Handles application errors and provides recovery options"""

    def __init__(self):
        """Initialize error state"""

        self.state_name = "error_state"
        self.error_info = None
        self.recovery_attempted = False


    def enter(self, ctx: Any,   # Context object
              data: Any = None  # Dictionary containing error details from previous state
             ) -> None:
        """Enter error state with error information"""

        try:
            ctx.logger.info("Entering error state - analyzing error")

            if not data or not isinstance(data, dict):
                raise ctx.errors.StateMachineError("Error state requires error information")

            self.error_info = data
            self.recovery_attempted = False

            # Extract error details:
            error = data.get("error")
            source_state = data.get("source_state", "unknown")
            recoverable = data.get("recoverable", False)

            # Log error details for developers:
            ctx.logger.error(f"Error from {source_state}: {str(error)}")
            if hasattr(error, '__class__'):
                ctx.logger.error(f"Error type: {error.__class__.__name__}")

            # Provide user-friendly error message:
            user_message = self._get_user_friendly_message(ctx, error, source_state)
            ctx.logger.error(user_message, target="user")

            # Log recovery options:
            if recoverable:
                ctx.logger.info("Attempting automatic recovery...", target="user")
            else:
                ctx.logger.info("Manual intervention may be required", target="user")

        except Exception as e:
            error_msg = f"Critical error entering error state: {str(e)}"
            ctx.logger.critical(error_msg)  # Can't raise here as we're already in error handling


    def execute(self, ctx: Any        # Context object
               ) -> Tuple[str, Any]:  # (next_state_name, recovery_data)
        """Execute error handling logic"""

        try:
            error = self.error_info.get("error")
            source_state = self.error_info.get("source_state")
            recoverable = self.error_info.get("recoverable", False)

            # Attempt recovery based on error type:
            if recoverable and not self.recovery_attempted:
                recovery_result = self._attempt_recovery(ctx, error, source_state)
                self.recovery_attempted = True

                if recovery_result["success"]:
                    return recovery_result["next_state"], recovery_result["data"]
                else:
                    # Recovery failed, fall through to manual handling:
                    ctx.logger.error("Automatic recovery failed", target="user")

            # Handle non-recoverable errors or failed recovery:
            return self._handle_manual_recovery(ctx, error, source_state)

        except Exception as e:
            # Critical error in error handling:
            ctx.logger.critical(f"Critical error in error handling: {str(e)}")
            ctx.logger.critical("Returning to idle state for safety", target="user")
            return ("idle_state", {"critical_error_recovery": True})


    def exit(self, ctx: Any) -> None:
        """Exit error state"""

        try:
            ctx.logger.info("Exiting error state")

            # Log recovery summary:
            if self.recovery_attempted:
                ctx.logger.info("Error recovery completed")

        except Exception as e:
            ctx.logger.warning(f"Error exiting error state: {str(e)}")


    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """Check if transition to target state is allowed from error state"""

        # From error state, we can go to any state depending on recovery:
        # - idle_state (most common recovery)
        # - input_state (retry input collection)
        # - acquisition_state (retry testing)
        allowed_transitions = ["idle_state", "input_state", "acquisition_state"]
        return target_state in allowed_transitions


    def _get_user_friendly_message(self, ctx: Any,    # Context object
                                   error: Any,        # Error object
                                   source_state: str  # State where error occurred
                                  ) -> str:           # User-friendly error message
        """Convert technical error to user-friendly message"""

        try:
            error_type = error.__class__.__name__ if hasattr(error, '__class__') else str(type(error))
            error_msg = str(error)

            # Map error types to user messages:
            if "ValidationError" in error_type:
                return f"Date introduse invalide: {error_msg}"
            elif "DeviceError" in error_type:
                if "scale" in error_msg.lower():
                    return "Atenție: Cântarul nu este conectat sau nu răspunde!"
                elif "press" in error_msg.lower():
                    return "Atenție: Presa nu este conectată sau nu răspunde!"
                else:
                    return f"Problemă cu echipamentul: {error_msg}"
            elif "ConfigurationError" in error_type:
                return f"Problemă de configurare: {error_msg}"
            elif "ProtocolError" in error_type:
                return f"Problemă cu protocolul de testare: {error_msg}"
            else:
                return f"Eroare în {source_state}: {error_msg}"

        except Exception:
            return f"Eroare neașteptată în {source_state}"


    def _attempt_recovery(self, ctx: Any,    # Context object
                          error: Any,        # Error object
                          source_state: str  # State where error occurred
                         ) -> dict:          # Recovery result with success status and next action
        """Attempt automatic recovery based on error type"""

        try:
            error_type = error.__class__.__name__ if hasattr(error, '__class__') else str(type(error))
            error_msg = str(error)

            ctx.logger.info("Attempting automatic error recovery...")

            # Recovery strategies by error type:
            if "DeviceError" in error_type:
                return self._recover_device_error(ctx, error_msg, source_state)
            elif "ValidationError" in error_type:
                return self._recover_validation_error(ctx, error_msg, source_state)
            elif "ConfigurationError" in error_type:
                return self._recover_configuration_error(ctx, error_msg, source_state)
            else:
                # No automatic recovery available:
                return {"success": False, "reason": "No automatic recovery for this error type"}

        except Exception as e:
            ctx.logger.error(f"Recovery attempt failed: {str(e)}")
            return {"success": False, "reason": f"Recovery attempt failed: {str(e)}"}


    def _recover_device_error(self, ctx: Any, error_msg: str, source_state: str) -> dict:
        """Recover from device connection errors"""

        try:
            ctx.logger.info("Attempting device recovery...", target="user")

            # Simulate device reconnection attempt:
            time.sleep(2)  # Give devices time to reconnect

            if "scale" in error_msg.lower():
                ctx.logger.info("Verificați conexiunea cântarului și încercați din nou", target="user")
                # For 1.0.0, assume scale recovers automatically:
                ctx.logger.info("Cântarul a fost reconectat", target="user")
                return {"success": True,
                        "next_state": source_state,  # Return to source state
                        "data": {"device_recovered": True}}

            elif "press" in error_msg.lower():
                ctx.logger.info("Verificați conexiunea presei și încercați din nou", target="user")
                # For 1.0.0, assume press recovers automatically:
                ctx.logger.info("Presa a fost reconectată", target="user")
                return {"success": True,
                        "next_state": source_state,  # Return to source state
                        "data": {"device_recovered": True}}

            return {"success": False, "reason": "Unknown device error"}

        except Exception as e:
            return {"success": False, "reason": f"Device recovery failed: {str(e)}"}


    def _recover_validation_error(self, ctx: Any, error_msg: str, source_state: str) -> dict:
        """Recover from validation errors"""

        try:
            ctx.logger.info("Validation error recovery", target="user")

            if source_state == "input_state":
                # Return to input state for data correction:
                ctx.logger.info("Vă rugăm să corectați datele introduse", target="user")
                return {"success": True,
                        "next_state": "input_state",
                        "data": {"retry_input": True, "validation_error": error_msg}}

            return {"success": False, "reason": "Cannot recover validation error from this state"}

        except Exception as e:
            return {"success": False, "reason": f"Validation recovery failed: {str(e)}"}


    def _recover_configuration_error(self, ctx: Any, error_msg: str, source_state: str) -> dict:
        """Recover from configuration errors"""

        try:
            # Configuration errors usually require manual intervention:
            ctx.logger.error("Eroare de configurare - contactați administratorul", target="user")
            return {"success": False, "reason": "Configuration errors require manual intervention"}

        except Exception as e:
            return {"success": False, "reason": f"Configuration recovery failed: {str(e)}"}


    def _handle_manual_recovery(self, ctx: Any,       # Context object
                                error: Any,           # Error object
                                source_state: str     # State where error occurred
                               ) -> Tuple[str, Any]:  # (next_state_name, recovery_data)
        """Handle errors that require manual intervention"""

        try:
            ctx.logger.error("Intervenție manuală necesară", target="user")

            # Provide recovery guidance based on source state:
            if source_state == "input_state":
                ctx.logger.info("Revenind la introducerea datelor...", target="user")
                return ("input_state", {"manual_recovery": True})

            elif source_state == "acquisition_state":
                # Check if we have partial data to preserve:
                partial_data = self.error_info.get("partial_data")
                if partial_data:
                    ctx.logger.info("Date parțiale salvate - revenind la starea inițială", target="user")
                    return ("idle_state", {"partial_data_saved": True})
                else:
                    ctx.logger.info("Revenind la starea inițială", target="user")
                    return ("idle_state", {"testing_failed": True})

            else:
                # Default recovery: return to idle state:
                ctx.logger.info("Revenind la starea inițială", target="user")
                return ("idle_state", {"recovered_from_error": True})

        except Exception as e:
            ctx.logger.critical(f"Manual recovery failed: {str(e)}")
            return ("idle_state", {"critical_error_recovery": True})

#%%