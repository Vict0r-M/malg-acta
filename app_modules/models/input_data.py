"""Input data model"""

#%% Dependencies:

from datetime import datetime
from typing import List, Literal, Any
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
                              description="Testing date in DD.MM.YYYY format")  # Defaults to current date

    project_title: str = Field(default="project title", description="Project description/name", 
                               min_length=1, max_length=200)
    element: str = Field(default="element", description="Specific componentof interest", 
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


    @field_validator('client', 'concrete_class', 'set_id', 'project_title', 'element')
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


    def get_sample_age(self, ctx: Any) -> int:
        """Calculate sample age in days as testing_date - sampling_date"""

        try:
            sampling_dt = datetime.strptime(self.sampling_date, "%d.%m.%Y")
            testing_dt = datetime.strptime(self.testing_date, "%d.%m.%Y")
            age_delta = testing_dt - sampling_dt
            age_days = age_delta.days

            ctx.logger.info(f"Calculated sample age: {age_days} days (from {self.sampling_date} to {self.testing_date})")
            return age_days

        except ValueError as e:
            raise ctx.errors.ValidationError(f"Failed to calculate sample age: {str(e)}")

#%%