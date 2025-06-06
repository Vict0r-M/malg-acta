"""Scale data model"""

#%% Dependencies:

from typing import ClassVar, Any
from pydantic import BaseModel, Field, field_validator

#%% Main Class:

class ScaleData(BaseModel):
    """Data model for scale measurements from specimen weighing"""

    # Allowed units:
    ALLOWED_MASS_UNITS: ClassVar[set] = {"kg", "g", "mg", "t", "lb", "oz"}

    # Measurement field:
    mass: float = Field(..., description="Mass of the specimen (assumed in kilograms unless specified otherwise)", ge=0.0)

    # Optional formatting configuration:
    mass_decimals: int = Field(default=1, ge=0, le=6)
    mass_unit: str = Field(default="kg")


    @field_validator('mass_unit')
    @classmethod
    def validate_mass_unit(cls, v: str) -> str:
        """Validate mass unit is in allowed list"""

        if v not in cls.ALLOWED_MASS_UNITS:
            raise ValueError(f"Mass unit must be one of: {', '.join(sorted(cls.ALLOWED_MASS_UNITS))}")
        return v


    def get_formatted_mass(self) -> str:
        """Get mass formatted with specified decimals and unit"""

        return f"{self.mass:.{self.mass_decimals}f} {self.mass_unit}"


    def set_mass_format(self, ctx: Any, decimals: int = None, unit: str = None) -> None:
        """Update mass formatting configuration and convert units if needed"""

        if decimals is not None:
            self.mass_decimals = decimals

        if unit is not None:
            # Validate unit first:
            if unit not in self.ALLOWED_MASS_UNITS:
                raise ctx.errors.ValidationError(f"Mass unit must be one of: {', '.join(sorted(self.ALLOWED_MASS_UNITS))}")
            
            # Define conversion factors relative to base SI unit (kg):
            mass_conversions = {"kg": 1.0,        # Kilogram
                                "g": 1000.0,      # Gram
                                "mg": 1000000.0,  # Miligram
                                "t": 0.001,       # Metric ton
                                "lb": 2.20462,    # Pounds
                                "oz": 35.274}     # Ounces

            current_factor = mass_conversions[self.mass_unit]
            new_factor = mass_conversions[unit]

            # Convert value - first to base unit (kg), then to target unit:
            old_mass = self.mass
            old_unit = self.mass_unit
            self.mass = self.mass / current_factor * new_factor
            self.mass_unit = unit

            ctx.logger.info(f"Converted mass from {old_mass} {old_unit} to {self.mass} {unit}")

#%%