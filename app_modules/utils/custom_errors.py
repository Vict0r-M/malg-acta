"""Custom error classes"""

#%%

class ApplicationError(Exception):
    """Base exception for all application errors"""
    
    pass


class ConfigurationError(ApplicationError):
    """Error raised for configuration file issues and validation failures"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class DeviceError(ApplicationError):
    """Error raised for all device-related issues (connection, communication, reading)"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ProtocolError(ApplicationError):
    """Error raised for testing protocol execution issues"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class PluginError(ApplicationError):
    """Error raised for all plugin-related issues (loading, execution, configuration)"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Error raised when data validation fails"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class DataStorageError(ApplicationError):
    """Error raised for data storage and persistence issues"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class OutputError(ApplicationError):
    """Error raised when output/report generation fails"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class StateMachineError(ApplicationError):
    """Error raised for state machine transition and execution issues"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

#%%