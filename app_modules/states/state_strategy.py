"""State strategy protocol - interface for all state implementations"""

#%% Dependencies:

from typing import Any, Protocol, Tuple

#%% State Strategy Protocol:

class StateStrategy(Protocol):
    """Protocol defining what any state implementation must provide"""

    def enter(self, ctx: Any,   # Context object (config, logger, errors, typing)
              data: Any = None  # Optional data passed from previous state
             ) -> None:
        """Called when entering this state"""
        ...


    def execute(self, ctx: Any        # Context object
               ) -> Tuple[str, Any]:  # Tuple as (next_state_name, data_for_next_state)
        """Execute the main logic of this state"""
        ...


    def exit(self, ctx: Any) -> None:
        """Called when exiting this state (cleanup)"""
        ...


    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """Check if transition to target state is allowed"""
        ...

#%%