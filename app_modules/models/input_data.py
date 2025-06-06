"""Input data model"""

#%% Dependencies:

from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator

#%% Main Class:

class InputData(BaseModel):
    """
    Validates all user-provided information according to project requirements:
    - Protocol selection with validation;
    - Client and concrete class management;
    - Date validation with DD.MM.YYYY format;
    - Sampling location and project name;
    - Set identifier and sizing;
    - Output preferences validation.
    """

    # Protocol selection (radio button format):
    protocol: Literal["cube_compression_testing",
                      "cube_frost_testing", 
                      "beam_compression_testing",
                      "beam_flexural_testing"
                     ] = Field(..., description="Testing protocol selection")

    client: str = Field(..., description="Client/beneficiary name", min_length=1, max_length=200)
    concrete_class: str = Field(..., description="Concrete class specification", min_length=1, max_length=100)

    sampling_date: str = Field(..., description="Sampling date in DD.MM.YYYY format")
    testing_date: str = Field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y"), 
                              description="Testing date in DD.MM.YYYY format")  # defaults to current date

    sampling_location: str = Field(default="sampling location", description="Location where sampling occurred", 
                                   min_length=1, max_length=200)
    project_name: str = Field(default="project name", description="Project name/identifier", 
                              min_length=1, max_length=200)

    set_id: str = Field(..., description="Set identifier/indicative", min_length=1, max_length=100)
    set_size: int = Field(..., description="Number of specimens in the set", gt=0, le=100)

    should_print: bool = Field(..., description="Whether to print receipt immediately")
    output_format: List[Literal["PDF", "Excel"]] = Field(..., 
                                                         description="Selected output formats",
                                                         min_length=1)


    @field_validator('sampling_date', 'testing_date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date follows DD.MM.YYYY format"""

        if not v:
            raise ValueError("Date is required")

        try:
            # Parse the date to validate format:
            datetime.strptime(v, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Date must be in DD.MM.YYYY format")

        return v


    @field_validator('client', 'concrete_class', 'set_id', 'sampling_location', 'project_name')
    @classmethod
    def validate_string(cls, v: str) -> str:
        """Validate and clean string fields that cannot be empty"""

        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")

        return cleaned


    @field_validator('output_format')
    @classmethod
    def validate_output_format(cls, v: List[str]) -> List[str]:
        """Validate that at least one output format is selected"""

        if not v or len(v) == 0:
            raise ValueError("At least one output format must be selected")

        # Remove duplicates while preserving order:
        seen = set()
        unique_formats = []
        for format_type in v:
            if format_type not in seen:
                seen.add(format_type)
                unique_formats.append(format_type)

        return unique_formats


    def get_sample_age(self) -> int:
        """Calculate sample age in days as testing_date - sampling_date"""

        sampling_dt = datetime.strptime(self.sampling_date, "%d.%m.%Y")
        testing_dt = datetime.strptime(self.testing_date, "%d.%m.%Y")
        age_delta = testing_dt - sampling_dt
        return age_delta.days  # Age in whole days

#%%