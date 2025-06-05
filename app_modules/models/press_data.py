"""Press data model for materials testing"""

#%% Dependencies:

from typing import ClassVar
from pydantic import BaseModel, Field, field_validator

#%% Main Class:

class PressData(BaseModel):
    """Data model for press measurements"""

    # Allowed units - annotated as ClassVar
    ALLOWED_LOAD_UNITS: ClassVar[set] = {"N", "kN", "MN"}
    ALLOWED_STRENGTH_UNITS: ClassVar[set] = {"N/mm²", "MPa", "Pa", "kPa", "GPa"}

    # Measurement fields:
    load: float = Field(..., description="Maximum force reached (assumed in Newtons unless specified otherwise)", ge=0.0)
    strength: float = Field(..., description="Calculated peak strength (assumed in N/mm² unless specified otherwise)", ge=0.0)

    # Optional formatting configuration:
    load_decimals: int = Field(default=0, ge=0, le=6)
    strength_decimals: int = Field(default=2, ge=0, le=6)
    load_unit: str = Field(default="N")
    strength_unit: str = Field(default="N/mm²")  # Not SI, but practical standard

    @field_validator('load_unit')
    @classmethod
    def validate_load_unit(cls, v: str) -> str:
        """Validate load unit is in allowed list"""

        if v not in cls.ALLOWED_LOAD_UNITS:
            raise ValueError(f"Load unit must be one of: {', '.join(sorted(cls.ALLOWED_LOAD_UNITS))}")
        return v


    @field_validator('strength_unit')
    @classmethod
    def validate_strength_unit(cls, v: str) -> str:
        """Validate strength unit is in allowed list"""

        if v not in cls.ALLOWED_STRENGTH_UNITS:
            raise ValueError(f"Strength unit must be one of: {', '.join(sorted(cls.ALLOWED_STRENGTH_UNITS))}")
        return v


    def get_formatted_load(self) -> str:
        """Get peak load formatted with specified decimals and unit"""

        return f"{self.load:.{self.load_decimals}f} {self.load_unit}"


    def get_formatted_strength(self) -> str:
        """Get peak strength formatted with specified decimals and unit"""

        return f"{self.strength:.{self.strength_decimals}f} {self.strength_unit}"


    def set_load_format(self, decimals: int = None, unit: str = None) -> None:
        """Update load formatting configuration and convert units if needed"""

        if decimals is not None:
            self.load_decimals = decimals

        if unit is not None:
            # Validate unit first:
            if unit not in self.ALLOWED_LOAD_UNITS:
                raise ValueError(f"Load unit must be one of: {', '.join(sorted(self.ALLOWED_LOAD_UNITS))}")

            # Define conversion factors relative to base SI unit (N):
            load_conversions = {"N": 1.0,        # Newton
                                "kN": 0.001,     # kilo Newton
                                "MN": 0.000001}  # mega Newton

            current_factor = load_conversions[self.load_unit]
            new_factor = load_conversions[unit]

            # Convert value - first to base unit (N), then to target unit:
            self.load = self.load / current_factor * new_factor
            self.load_unit = unit


    def set_strength_format(self, decimals: int = None, unit: str = None) -> None:
        """Update strength formatting configuration and convert units if needed"""

        if decimals is not None:
            self.strength_decimals = decimals

        if unit is not None:
            # Validate unit first:
            if unit not in self.ALLOWED_STRENGTH_UNITS:
                raise ValueError(f"Strength unit must be one of: {', '.join(sorted(self.ALLOWED_STRENGTH_UNITS))}")

            # Define conversion factors relative to base SI unit (N/mm²):
            strength_conversions = {"N/mm²": 1.0,     # Not SI, but practical stadard
                                    "MPa": 1.0,       # 1 N/mm² = 1 MPa
                                    "Pa": 1000000.0,  # 1 N/mm² = 1,000,000 Pa
                                    "kPa": 1000.0,    # 1 N/mm² = 1,000 kPa
                                    "GPa": 0.001}     # 1 N/mm² = 0.001 GPa

            current_factor = strength_conversions[self.strength_unit]
            new_factor = strength_conversions[unit]

            # Convert value - first to base unit (N/mm²), then to target unit:
            self.strength = self.strength / current_factor * new_factor
            self.strength_unit = unit

#%%