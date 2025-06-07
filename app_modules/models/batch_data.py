"""Batch data model"""

#%% Dependencies:

from typing import List, Any
from pydantic import BaseModel, Field

#%% Main Class:

class BatchData(BaseModel):
    """Container for multiple sets tested in a session"""

    sets: List[Any] = Field(default_factory=list, description="List of specimen sets")


    @property
    def batch_size(self) -> int:
        """Get the current number of sets in the batch"""

        return len(self.sets)


    def add_set(self, ctx: Any, set_data: Any) -> None:
        """Add a set to the batch"""

        if set_data is None:
            raise ctx.errors.ValidationError("Cannot add None set to batch")

        self.sets.append(set_data)
        ctx.logger.info(f"Added set to batch. New batch size: {self.batch_size}")

#%%