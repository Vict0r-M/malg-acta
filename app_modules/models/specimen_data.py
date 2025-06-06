"""Specimen data model"""

#%% Dependencies:

from typing import Optional, Any
from pydantic import BaseModel, Field

#%% Main Class:

class SpecimenData(BaseModel):
    """Data model for individual specimens: container for scale and press measurements"""

    # Measurement data (protocol-dependent):
    scale_data: Optional[Any] = Field(default=None, description="Scale measurement data")
    press_data: Optional[Any] = Field(default=None, description="Press measurement data")

#%%