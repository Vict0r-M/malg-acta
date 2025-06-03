"""Custom typing definitions for Malg-ACTA"""

#%% Dependencies:

from dataclasses import dataclass
from typing import Any, Literal, List, Dict, Union
from pathlib import Path

#%% Context Object:

@dataclass
class Context:
    """Shared context passed through constructors for dependency injection"""

    typing: Any         # Will contain the custom typing module 
    errors: Any         # Will contain the custom_errors module
    logger: Any         # Will contain the logger instance
    config: Any = None  # Will contain the loaded config (Box object)

#%% Protocol Types:

ProtocolType = Literal[
    "cube_compression_testing",
    "cube_frost_testing", 
    "beam_compression_testing",
    "beam_flexural_testing"
]

#%% Device and Serial Types:

DeviceConnectionState = Literal["connected", "disconnected", "error", "unknown"]

SerialPortConfig = Dict[str, Union[str, int, bool]]
# Example: {
#     "port": "/dev/ttyACM0",
#     "baudrate": 9600,
#     "timeout": 1.0,
#     "bytesize": 8,
#     "parity": "N",
#     "stopbits": 1
# }

DeviceReadingData = Dict[str, Union[float, str, bool]]
# Example: {
#     "value": 2.5,
#     "unit": "kg", 
#     "stable": True,
#     "raw_data": "ST,GS,+  2.500kg",
#     "timestamp": "2025-01-15 10:30:45"
# }

#%% File and Path Types:

ConfigPath = Union[str, Path]
DataFilePath = Union[str, Path]
ReportFilePath = Union[str, Path]
LogFilePath = Union[str, Path]

# Specific file types:
JSONFilePath = Union[str, Path]
YAMLFilePath = Union[str, Path]
CSVFilePath = Union[str, Path]
ExcelFilePath = Union[str, Path]
PDFFilePath = Union[str, Path]

#%% Testing Workflow Types:

WorkflowState = Literal[
    "idle",
    "input", 
    "validation",
    "testing",
    "acquisition",
    "processing",
    "output",
    "complete",
    "error"
]

TestingPhase = Literal[
    "scale_measurement",
    "press_measurement", 
    "calculations",
    "validation",
    "completed"
]

#%% Input Validation Types:

InputFieldType = Literal[
    "protocol",
    "client",
    "concrete_class", 
    "sampling_date",
    "testing_date",
    "sampling_location",
    "project_name",
    "set_id",
    "set_size",
    "should_print",
    "output_format"
]

ValidationErrorInfo = Dict[str, Union[str, List[str]]]
# Example: {
#     "field": "sampling_date",
#     "errors": ["Date must be in DD.MM.YYYY format"],
#     "value": "invalid_date"
# }

OutputFormatType = Literal["PDF", "Excel", "Word"]

#%% Data Structure Types:

SpecimenMeasurements = Dict[str, Union[float, str, bool, None]]
# Example: {
#     "mass": 2.5,
#     "mass_unit": "kg",
#     "load": 15000.0,
#     "strength": 25.5,
#     "has_scale_data": True,
#     "has_press_data": True
# }

SetStatistics = Dict[str, Union[float, int, str]]
# Example: {
#     "specimen_count": 3,
#     "average_mass": 2.45,
#     "average_strength": 24.8,
#     "min_strength": 23.1,
#     "max_strength": 26.2
# }

BatchSummary = Dict[str, Union[int, float, str, List[str]]]
# Example: {
#     "total_sets": 2,
#     "total_specimens": 6,
#     "protocols_used": ["cube_compression_testing"],
#     "completion_rate": 100.0
# }

#%% Plugin and Component Types:

PluginType = Literal["input", "acquisition", "output"]
PluginState = Literal["loaded", "initialized", "active", "error", "disabled"]

ComponentConfig = Dict[str, Any]
# Generic configuration for any component

PluginInfo = Dict[str, Union[str, bool, PluginState]]
# Example: {
#     "name": "scale_plugin",
#     "type": "acquisition", 
#     "enabled": True,
#     "state": "active",
#     "version": "1.0.0"
# }

#%% Bridge and Communication Types:

JavaBridgeMessage = Dict[str, Any]
# Example: {
#     "type": "input_data",
#     "timestamp": "2025-01-15T10:30:45",
#     "data": {...}
# }

BridgeConnectionState = Literal["connected", "disconnected", "timeout", "error"]

CommunicationProtocol = Literal["json_file", "socket", "pipe", "rest_api"]

#%% Error and Exception Types:

ErrorSeverity = Literal["info", "warning", "error", "critical"]

ErrorContext = Dict[str, Union[str, int, float, bool, None]]
# Example: {
#     "component": "scale_plugin",
#     "operation": "read_measurement",
#     "attempt": 3,
#     "timeout": 5.0
# }

#%% Configuration Types:

LoggingConfig = Dict[str, Union[str, bool, Path]]
# Example: {
#     "path": Path("logs/malg_acta.log"),
#     "console_enabled": True,
#     "level": "INFO"
# }

ProtocolConfig = Dict[str, Union[bool, int, float, Dict[str, Union[int, float]]]]
# Example: {
#     "requires_scale": True,
#     "requires_press": True,
#     "specimen_dimensions": {"x": 150, "y": 150, "z": 150},
#     "compression_area": 22500
# }

DeviceConfig = Dict[str, Union[str, int, float, bool]]
# Example: {
#     "device_type": "scale",
#     "port": "/dev/ttyACM1", 
#     "baudrate": 9600,
#     "timeout": 1.0,
#     "auto_detect": True
# }

#%% Unit and Measurement Types:

MassUnit = Literal["kg", "g", "mg", "t", "lb", "oz"]
ForceUnit = Literal["N", "kN", "MN", "lbf"]
StrengthUnit = Literal["N/mm²", "MPa", "Pa", "kPa", "GPa", "psi"]
TimeUnit = Literal["s", "ms", "min", "h"]

MeasurementPrecision = Dict[str, int]
# Example: {
#     "mass_decimals": 3,
#     "load_decimals": 0, 
#     "strength_decimals": 2
# }

#%% Registry and Persistence Types:

RegistryEntry = Dict[str, Union[str, int, float]]
# Example: {
#     "timestamp": "15.01.2025 10:30",
#     "client": "AGREMIN SRL",
#     "set_id": "ABC123",
#     "protocol": "cube_compression_testing",
#     "specimen_count": 3,
#     "sample_age_days": 28
# }

PersistentListType = Literal["clients", "concrete_classes"]

DataStorageOperation = Literal["load", "save", "add", "remove", "update"]

#%%