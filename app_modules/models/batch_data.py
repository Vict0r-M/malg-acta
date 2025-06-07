"""Batch data model"""

#%% Dependencies:

from typing import List, Any
from pydantic import BaseModel, Field, field_validator

#%% Main Class:

class BatchData(BaseModel):
    """Container for multiple sets tested in a session"""

    sets: List[Any] = Field(default_factory=list, description="List of specimen sets")
    batch_size: int = Field(..., description="Number of sets in this batch", gt=0)

    @field_validator('sets')
    @classmethod
    def validate_sets_count(cls, v: List[Any], info) -> List[Any]:
        """Validate that sets count matches batch_size"""

        # Get batch_size from the model being validated:
        batch_size = info.data.get('batch_size')

        if batch_size is not None:
            actual_count = len(v)

            if actual_count != batch_size:
                raise ValueError(f"Number of sets ({actual_count}) must match batch_size ({batch_size})")

        return v


    def add_set(self, set_data: Any) -> None:
        """Add a set to the batch"""

        if len(self.sets) >= self.batch_size:
            raise ValueError(f"Cannot add more sets: batch is full ({self.batch_size} maximum)")

        self.sets.append(set_data)


    def is_complete(self) -> bool:
        """Check if the batch has all required sets"""

        return len(self.sets) == self.batch_size

#%%