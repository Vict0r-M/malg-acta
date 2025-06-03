"""Custom error classes for Malg-ACTA"""

#%%

class MalgActaError(Exception):
    """Base exception for all Malg-ACTA errors"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

#%% Configuration Errors:

class ConfigurationError(MalgActaError):
    """Error raised for configuration issues"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

class ConfigFileNotFoundError(ConfigurationError):
    """Error raised when configuration file is not found"""

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        message = f"Configuration file not found: {config_path}"
        super().__init__(message)

class InvalidConfigValueError(ConfigurationError):
    """Error raised for invalid configuration values"""

    def __init__(self, config_key: str, value: str, reason: str) -> None:
        self.config_key = config_key
        self.value = value
        self.reason = reason
        message = f"Invalid config value for '{config_key}': {value} ({reason})"
        super().__init__(message)

#%% Device Communication Errors:

class DeviceConnectionError(MalgActaError):
    """Error raised when device connection fails"""

    def __init__(self, device_type: str, port: str, reason: str = "") -> None:
        self.device_type = device_type
        self.port = port
        self.reason = reason
        message = f"Failed to connect to {device_type} on port {port}"
        if reason:
            message += f": {reason}"
        super().__init__(message)

class DeviceReadingError(MalgActaError):
    """Error raised when device reading fails or is unstable"""

    def __init__(self, device_type: str, reading_type: str, reason: str) -> None:
        self.device_type = device_type
        self.reading_type = reading_type
        self.reason = reason
        message = f"Failed to get stable {reading_type} from {device_type}: {reason}"
        super().__init__(message)

class SerialCommunicationError(MalgActaError):
    """Error raised for serial port communication issues"""

    def __init__(self, port: str, operation: str, reason: str) -> None:
        self.port = port
        self.operation = operation
        self.reason = reason
        message = f"Serial communication error on {port} during {operation}: {reason}"
        super().__init__(message)

class DeviceTimeoutError(MalgActaError):
    """Error raised when device operation times out"""

    def __init__(self, device_type: str, operation: str, timeout_seconds: float) -> None:
        self.device_type = device_type
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        message = f"{device_type} {operation} timed out after {timeout_seconds}s"
        super().__init__(message)

#%% Data Validation Errors:

class DataValidationError(MalgActaError):
    """Error raised for Pydantic validation failures"""

    def __init__(self, model_name: str, field_name: str, value: str, reason: str) -> None:
        self.model_name = model_name
        self.field_name = field_name
        self.value = value
        self.reason = reason
        message = f"Validation error in {model_name}.{field_name}: {reason} (value: {value})"
        super().__init__(message)

class ProtocolMismatchError(MalgActaError):
    """Error raised when protocol doesn't match specimen requirements"""

    def __init__(self, expected_protocol: str, actual_protocol: str) -> None:
        self.expected_protocol = expected_protocol
        self.actual_protocol = actual_protocol
        message = f"Protocol mismatch: expected {expected_protocol}, got {actual_protocol}"
        super().__init__(message)

class SpecimenOrderError(MalgActaError):
    """Error raised for incorrect specimen sequencing"""

    def __init__(self, expected_sequence: str, actual_sequence: str) -> None:
        self.expected_sequence = expected_sequence
        self.actual_sequence = actual_sequence
        message = f"Specimen order error: expected {expected_sequence}, got {actual_sequence}"
        super().__init__(message)

class InvalidMeasurementError(MalgActaError):
    """Error raised for invalid measurement values"""

    def __init__(self, measurement_type: str, value: float, limits: str) -> None:
        self.measurement_type = measurement_type
        self.value = value
        self.limits = limits
        message = f"Invalid {measurement_type} measurement: {value} (limits: {limits})"
        super().__init__(message)

#%% Workflow Management Errors:

class StateTransitionError(MalgActaError):
    """Error raised for invalid state changes"""

    def __init__(self, current_state: str, requested_state: str, reason: str) -> None:
        self.current_state = current_state
        self.requested_state = requested_state
        self.reason = reason
        message = f"Cannot transition from {current_state} to {requested_state}: {reason}"
        super().__init__(message)

class PluginLoadError(MalgActaError):
    """Error raised when plugin loading/registration fails"""

    def __init__(self, plugin_name: str, plugin_type: str, reason: str) -> None:
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.reason = reason
        message = f"Failed to load {plugin_type} plugin '{plugin_name}': {reason}"
        super().__init__(message)

class WorkflowError(MalgActaError):
    """Error raised for general workflow issues"""

    def __init__(self, workflow_phase: str, operation: str, reason: str) -> None:
        self.workflow_phase = workflow_phase
        self.operation = operation
        self.reason = reason
        message = f"Workflow error in {workflow_phase} during {operation}: {reason}"
        super().__init__(message)

class IncompleteSetError(MalgActaError):
    """Error raised when attempting to process incomplete specimen set"""

    def __init__(self, expected_count: int, actual_count: int, set_id: str) -> None:
        self.expected_count = expected_count
        self.actual_count = actual_count
        self.set_id = set_id
        message = f"Incomplete set {set_id}: expected {expected_count} specimens, got {actual_count}"
        super().__init__(message)

#%% File and Storage Errors:

class DataStorageError(MalgActaError):
    """Error raised for JSON file read/write issues"""

    def __init__(self, file_path: str, operation: str, reason: str) -> None:
        self.file_path = file_path
        self.operation = operation
        self.reason = reason
        message = f"Data storage error during {operation} on {file_path}: {reason}"
        super().__init__(message)

class ReportGenerationError(MalgActaError):
    """Error raised when PDF/Excel/Word creation fails"""

    def __init__(self, report_type: str, output_path: str, reason: str) -> None:
        self.report_type = report_type
        self.output_path = output_path
        self.reason = reason
        message = f"Failed to generate {report_type} report at {output_path}: {reason}"
        super().__init__(message)

class FilePermissionError(MalgActaError):
    """Error raised for file permission issues"""

    def __init__(self, file_path: str, operation: str) -> None:
        self.file_path = file_path
        self.operation = operation
        message = f"Permission denied for {operation} on {file_path}"
        super().__init__(message)

class InvalidFileFormatError(MalgActaError):
    """Error raised for invalid file formats"""

    def __init__(self, file_path: str, expected_format: str, actual_format: str) -> None:
        self.file_path = file_path
        self.expected_format = expected_format
        self.actual_format = actual_format
        message = f"Invalid file format for {file_path}: expected {expected_format}, got {actual_format}"
        super().__init__(message)

#%% Bridge and Communication Errors:

class JavaBridgeError(MalgActaError):
    """Error raised for Java bridge communication issues"""

    def __init__(self, operation: str, reason: str) -> None:
        self.operation = operation
        self.reason = reason
        message = f"Java bridge error during {operation}: {reason}"
        super().__init__(message)

class InputDataNotFoundError(MalgActaError):
    """Error raised when input data file is not found"""

    def __init__(self, input_file: str, timeout_seconds: float) -> None:
        self.input_file = input_file
        self.timeout_seconds = timeout_seconds
        message = f"Input data file not found: {input_file} (waited {timeout_seconds}s)"
        super().__init__(message)

class OutputGenerationTimeoutError(MalgActaError):
    """Error raised when output generation times out"""

    def __init__(self, output_type: str, timeout_seconds: float) -> None:
        self.output_type = output_type
        self.timeout_seconds = timeout_seconds
        message = f"{output_type} generation timed out after {timeout_seconds}s"
        super().__init__(message)

class ComponentCommunicationError(MalgActaError):
    """Error raised for inter-component communication failures"""

    def __init__(self, source_component: str, target_component: str, message_type: str, reason: str) -> None:
        self.source_component = source_component
        self.target_component = target_component
        self.message_type = message_type
        self.reason = reason
        message = f"Communication error from {source_component} to {target_component} ({message_type}): {reason}"
        super().__init__(message)

#%% Protocol and Testing Errors:

class ProtocolNotFoundError(MalgActaError):
    """Error raised when requested protocol is not available"""

    def __init__(self, protocol_name: str, available_protocols: list) -> None:
        self.protocol_name = protocol_name
        self.available_protocols = available_protocols
        message = f"Protocol '{protocol_name}' not found. Available: {', '.join(available_protocols)}"
        super().__init__(message)

class InsufficientMeasurementsError(MalgActaError):
    """Error raised when specimen lacks required measurements for protocol"""

    def __init__(self, protocol: str, specimen_id: str, missing_measurements: list) -> None:
        self.protocol = protocol
        self.specimen_id = specimen_id
        self.missing_measurements = missing_measurements
        message = f"Specimen {specimen_id} missing required measurements for {protocol}: {', '.join(missing_measurements)}"
        super().__init__(message)

class CalculationError(MalgActaError):
    """Error raised when calculations fail"""

    def __init__(self, calculation_type: str, input_values: dict, reason: str) -> None:
        self.calculation_type = calculation_type
        self.input_values = input_values
        self.reason = reason
        message = f"Calculation error for {calculation_type}: {reason} (inputs: {input_values})"
        super().__init__(message)

#%%