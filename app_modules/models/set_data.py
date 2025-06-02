"""Set data model"""

#%% Dependencies:

from typing import List, Any
from pydantic import BaseModel, Field, field_validator

#%% Main Class:

class SetData(BaseModel):
    """Container for user input data and the corresponding specimens tested together"""

    # Input data containing user preferences and test parameters:
    input_data: Any = Field(..., description="User input data for this set")

    # Collection of specimens (size must match input_data.set_size):
    specimens: List[Any] = Field(default_factory=list, description="List of specimen measurements")


    @field_validator('specimens')
    @classmethod
    def validate_specimens_count(cls, v: List[Any], info) -> List[Any]:
        """Validate that specimens count matches input_data.set_size"""

        # Get input_data from the model being validated:
        input_data = info.data.get('input_data')

        if input_data and hasattr(input_data, 'set_size'):
            expected_count = input_data.set_size
            actual_count = len(v)

            if actual_count != expected_count:
                raise ValueError(f"Number of specimens ({actual_count}) must match set_size ({expected_count})")

        return v


    def add_specimen(self, specimen: Any) -> None:
        """Add a specimen to the set"""

        if len(self.specimens) >= self.input_data.set_size:
            raise ValueError(f"Cannot add more specimens: set is full ({self.input_data.set_size} maximum)")

        self.specimens.append(specimen)


    def is_complete(self) -> bool:
        """Check if the set has all required specimens"""

        return len(self.specimens) == self.input_data.set_size

#%%