"""State machine - controls application flow through states"""

#%% Dependencies:

from typing import Any

#%% State Machine Class:

class StateMachine:
    """Manages state transitions, data passing, and error handling"""

    def __init__(self, ctx: Any,            # Context object containing config, logger, errors, typing
                 idle_state: Any,           # IdleState instance
                 input_state: Any,          # InputState instance  
                 acquisition_state: Any,    # AcquisitionState instance
                 dissemination_state: Any,  # DisseminationState instance
                 error_state: Any):         # ErrorState instance

        self.ctx = ctx

        # State management:
        self.current_state_name = "idle_state"
        self.current_state = None
        self.state_data = None  # Data passed between states
        self.running = False

        # State registry:
        self._states = {"idle_state": idle_state,
                        "input_state": input_state,
                        "acquisition_state": acquisition_state,
                        "dissemination_state": dissemination_state,
                        "error_state": error_state}

        # Valid state transitions:
        self._valid_transitions = {"idle_state": ["input_state", "error_state"],
                                   "input_state": ["acquisition_state", "error_state", "idle_state"],
                                   "acquisition_state": ["dissemination_state", "error_state"],
                                   "dissemination_state": ["idle_state", "error_state"],
                                   "error_state": ["idle_state", "input_state"]}

        self.ctx.logger.info("StateMachine initialized")


    def start(self) -> None:
        """Start the state machine from idle state. Runs continuously until stopped or error"""

        try:
            self.running = True
            self.ctx.logger.info("Starting state machine")
            self.ctx.logger.info("Application ready for use", target="user")

            # Load initial state:
            self._load_state("idle_state")

            # Main state machine loop:
            while self.running:
                try:
                    # Execute current state:
                    next_state_name, next_state_data = self.current_state.execute(self.ctx)

                    # Check for stop condition:
                    if next_state_name == "stop":
                        self.ctx.logger.info("State machine stop requested")
                        break

                    # Transition to next state:
                    if next_state_name != self.current_state_name:
                        self._transition_to(next_state_name, next_state_data)

                except self.ctx.errors.ApplicationError as e:
                    # Handle application errors by transitioning to error state:
                    self.ctx.logger.error(f"Application error in {self.current_state_name}: {str(e)}")
                    self._transition_to("error_state", {"error": e, "source_state": self.current_state_name})

                except Exception as e:
                    # Handle unexpected errors:
                    self.ctx.logger.exception(f"Unexpected error in {self.current_state_name}: {str(e)}")
                    error_obj = self.ctx.errors.StateMachineError(f"Unexpected error: {str(e)}")
                    self._transition_to("error_state", {"error": error_obj, "source_state": self.current_state_name})

        except Exception as e:
            self.ctx.logger.exception(f"Critical error in state machine: {str(e)}")
            raise self.ctx.errors.StateMachineError(f"State machine failed: {str(e)}")

        finally:
            self._cleanup()


    def stop(self) -> None:
        """Stop the state machine gracefully"""

        self.running = False
        self.ctx.logger.info("State machine stop initiated")


    def force_transition(self, target_state: str,  # Name of target state
                         data: Any = None          # Optional data to pass to target state
                        ) -> None:
        """Force transition to specific state (for external control)"""

        self.ctx.logger.info(f"Forced transition to {target_state}")
        self._transition_to(target_state, data)


    def get_current_state(self) -> str:
        """Get current state name"""

        return self.current_state_name


    def get_valid_transitions(self) -> list[str]:
        """Get list of valid transitions from current state"""

        return self._valid_transitions.get(self.current_state_name, [])


    def _load_state(self, state_name: str) -> None:
        """Load state instance from injected state registry"""

        try:
            if state_name not in self._states:
                available_states = list(self._states.keys())
                error_msg = f"Unknown state '{state_name}'. Available: {available_states}"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.StateMachineError(error_msg)

            self.current_state = self._states[state_name]
            self.current_state_name = state_name
            self.ctx.logger.info(f"Loaded state: {state_name}")

        except Exception as e:
            error_msg = f"Failed to load state '{state_name}': {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.StateMachineError(error_msg)


    def _transition_to(self, target_state: str,  # Name of target state
                       data: Any = None          # Optional data to pass to target state
                      ) -> None:
        """Transition from current state to target state"""

        try:
            # Validate transition:
            if not self._is_valid_transition(target_state):
                error_msg = f"Invalid transition from {self.current_state_name} to {target_state}"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.StateMachineError(error_msg)

            # Exit current state:
            if self.current_state:
                self.current_state.exit(self.ctx)

            # Load and enter new state:
            previous_state = self.current_state_name
            self._load_state(target_state)
            self.state_data = data
            self.current_state.enter(self.ctx, data)

            self.ctx.logger.info(f"Transitioned from {previous_state} to {target_state}")

        except Exception as e:
            error_msg = f"State transition failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.StateMachineError(error_msg)


    def _is_valid_transition(self, target_state: str) -> bool:
        """Check if transition to target state is valid"""

        # Always allow transitions to error state:
        if target_state == "error_state":
            return True

        # Check configured valid transitions:
        valid_states = self._valid_transitions.get(self.current_state_name, [])
        if target_state not in valid_states:
            return False

        # Ask current state if transition is allowed:
        if self.current_state:
            return self.current_state.can_transition_to(self.ctx, target_state)

        return True


    def _cleanup(self) -> None:
        """Cleanup state machine resources"""

        try:
            self.ctx.logger.info("Cleaning up state machine...")

            # Exit current state:
            if self.current_state:
                self.current_state.exit(self.ctx)

            self.running = False
            self.ctx.logger.info("State machine cleanup completed")

        except Exception as e:
            self.ctx.logger.warning(f"Error during state machine cleanup: {str(e)}")


    def __enter__(self):
        """Context manager entry"""

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self._cleanup()

#%%