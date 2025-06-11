"""Custom type definitions"""

#%% Dependencies:

from dataclasses import dataclass
from typing import Any, List, Optional, Literal

#%% Data Model Types:

@dataclass
class ScaleDataType:
    """Scale measurement data type"""

    mass: float
    mass_decimals: int = 1
    mass_unit: str = "kg"


@dataclass
class PressDataType:
    """Press measurement data type"""

    load: float
    strength: float
    load_decimals: int = 0
    strength_decimals: int = 2
    load_unit: str = "N"
    strength_unit: str = "N/mm²"


@dataclass
class SpecimenDataType:
    """Individual specimen measurements type"""

    scale_data: Optional[ScaleDataType] = None
    press_data: Optional[PressDataType] = None


@dataclass
class InputDataType:
    """User input data type"""

    protocol: Literal["cube_compression_testing", "cube_frost_testing", 
                      "beam_compression_testing", "beam_flexural_testing"]
    client: str
    concrete_class: str
    sampling_date: str
    testing_date: str
    set_id: str
    set_size: int
    should_print: bool
    output_format: List[Literal["PDF", "Excel"]]
    project_title: str = "project_title"
    element: str = "element"


@dataclass
class SetDataType:
    """Test set data type"""

    input_data: InputDataType
    specimens: List[SpecimenDataType]


@dataclass
class BatchDataType:
    """Batch data type containing multiple sets"""

    sets: List[SetDataType]

#%% Context:

@dataclass
class Context:
    """Shared context passed through constructors for dependency injection"""

    typing: Any         # Custom typing module for type definitions
    errors: Any         # Custom_errors module for exception handling  
    logger: Any         # Configured logger instance for system logging
    config: Any = None  # Loaded configuration

#%%