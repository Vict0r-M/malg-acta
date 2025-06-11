"""Configuration loading and validation + path management for malg-acta"""

#%% Dependencies:

import yaml
from box import Box
from pathlib import Path
from typing import Any, Dict, Union

#%% load_config() Helper Functions:

def _convert_path_to_absolute(path_str: str) -> Path:
    """_convert_paths() helper: convert any path string to absolute path"""

    path = Path(path_str)

    # Case 1 - System absolute paths (e.g. "/home/user/data" or "C:\\Users\\data"):
    if path.is_absolute():
        return path

    # Case 2 - Project-relative paths (e.g. "data/reports" and including ./ and ../ paths):
    project_root = Path(__file__).parent.parent.parent
    return (project_root / path).resolve()


def _convert_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert path strings to Path objects in a dictionary"""

    converted = {}  # e.g., starts empty, will contain {"data_dir": Path("/abs/path")}

    for key, value in config.items():
        if isinstance(value, dict):
            # Recursively process nested dictionaries:
            converted[key] = _convert_paths(value)
        elif isinstance(value, str) and key.endswith(('path', 'dir')):
            # Convert string paths to Path objects (e.g., "data/" -> "/home/user/malg-acta/data/"):
            converted[key] = _convert_path_to_absolute(value)
        else:
            converted[key] = value  # Keep non-path values unchanged

    return converted


def _validate_paths(config: Box, ctx: Any) -> None:
    """Validate all paths in config recursively and create directories as needed"""

    for key, value in config.items():
        if isinstance(value, Path):
            try:
                # Create parent directories for file paths, or the directory itself for dir paths:
                if key.endswith('dir'):
                    value.mkdir(parents=True, exist_ok=True)
                else:
                    value.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                error_msg = f"Permission denied creating directory for path: {str(value)}"
                ctx.logger.error(error_msg)
                raise ctx.errors.ConfigurationError(error_msg)
        elif isinstance(value, dict):
            _validate_paths(value, ctx)


def _validate_logging(config: Box, ctx: Any) -> None:
    """Validate logging configuration section"""

    if 'logging' not in config:
        error_msg = "Missing required section: logging"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if 'path' not in config.logging:
        error_msg = "logging.path must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(config.logging.path, Path):
        error_msg = "logging.path must be a valid path"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if 'console_enabled' not in config.logging:
        error_msg = "logging.console_enabled must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(config.logging.console_enabled, bool):
        error_msg = "logging.console_enabled must be a boolean value (true/false)"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def _validate_data_storage(config: Box, ctx: Any) -> None:
    """Validate data storage configuration section"""

    if 'data_storage' not in config:
        error_msg = "Missing required section: data_storage"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    data_config = config.data_storage

    # Validate required directories:
    required_dirs = ['data_dir', 'receipts_dir']
    for dir_key in required_dirs:
        if dir_key not in data_config:
            error_msg = f"data_storage.{dir_key} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        if not isinstance(data_config[dir_key], Path):
            error_msg = f"data_storage.{dir_key} must be a valid path"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

    # Validate required file paths:
    required_files = ['clients_path', 'concrete_classes_path', 'registry_path']
    for file_key in required_files:
        if file_key not in data_config:
            error_msg = f"data_storage.{file_key} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        if not isinstance(data_config[file_key], Path):
            error_msg = f"data_storage.{file_key} must be a valid path"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)


def _validate_device_config(device_config: Dict[str, Any], device_name: str, ctx: Any) -> None:
    """Validate individual device configuration"""

    if 'port' not in device_config:
        error_msg = f"devices.{device_name}.port must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(device_config['port'], str):
        error_msg = f"devices.{device_name}.port must be a string"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if 'baudrate' not in device_config:
        error_msg = f"devices.{device_name}.baudrate must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(device_config['baudrate'], int) or device_config['baudrate'] <= 0:
        error_msg = f"devices.{device_name}.baudrate must be a positive integer"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if 'timeout' not in device_config:
        error_msg = f"devices.{device_name}.timeout must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(device_config['timeout'], (int, float)) or device_config['timeout'] <= 0:
        error_msg = f"devices.{device_name}.timeout must be a positive number"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    # Validate retry_count for devices if present:
    if 'retry_count' in device_config:
        if not isinstance(device_config['retry_count'], int) or device_config['retry_count'] <= 0:
            error_msg = f"devices.{device_name}.retry_count must be a positive integer"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)


def _validate_devices(config: Box, ctx: Any) -> None:
    """Validate devices configuration section"""

    if 'devices' not in config:
        error_msg = "Missing required section: devices"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    devices_config = config.devices

    # Validate required devices:
    required_devices = ['scale', 'press']
    for device_name in required_devices:
        if device_name not in devices_config:
            error_msg = f"devices.{device_name} configuration must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        _validate_device_config(devices_config[device_name], device_name, ctx)


def _validate_plugins(config: Box, ctx: Any) -> None:
    """Validate plugins configuration section"""

    if 'plugins' not in config:
        error_msg = "Missing required section: plugins"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    plugins_config = config.plugins

    if 'config_path' not in plugins_config:
        error_msg = "plugins.config_path must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    if not isinstance(plugins_config['config_path'], Path):
        error_msg = "plugins.config_path must be a valid path"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def _validate_input_method(config: Box, ctx: Any) -> None:
    """Validate input method configuration"""

    if 'input' not in config:
        error_msg = "Missing required section: input"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    input_config = config.input

    if 'method' not in input_config:
        error_msg = "input.method must be specified"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    allowed_methods = ['gui', 'cli']
    if input_config.method not in allowed_methods:
        error_msg = f"input.method must be one of: {', '.join(allowed_methods)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    # Validate retry_count for input if present:
    if 'retry_count' in input_config:
        if not isinstance(input_config.retry_count, int) or input_config.retry_count <= 0:
            error_msg = "input.retry_count must be a positive integer"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)
    else:
        # Set default retry_count if not specified:
        input_config.retry_count = 3
        ctx.logger.info("input.retry_count not specified, using default value: 3")


def _validate_input_logging_combination(config: Box, ctx: Any) -> None:
    """Validate input method and logging combination to prevent console conflicts"""
    
    input_method = config.input.method
    console_enabled = config.logging.console_enabled
    
    # Case 4: CLI input + console logging = conflict:
    if input_method == "cli" and console_enabled:
        error_msg = "Cannot use console logging (console_enabled=true) with CLI input method"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)


def _validate_config(config: Box, ctx: Any) -> None:
    """Validate configuration parameters"""

    # First validate all paths and create directories:
    _validate_paths(config, ctx)

    # Validate required sections:
    _validate_logging(config, ctx)
    _validate_data_storage(config, ctx)
    _validate_devices(config, ctx)
    _validate_plugins(config, ctx)

    # Validate input method configuration:
    _validate_input_method(config, ctx)
    
    # Validate input/logging combination to prevent conflicts:
    _validate_input_logging_combination(config, ctx)

#%% Main Configuration Loading Function:

def load_config(config_path: Union[str, Path], ctx: Any) -> Box:
    """Load and validate configuration from YAML file"""

    try:
        # Ensure we have a Path object:
        config_path = Path(config_path)
        if not config_path.exists():
            error_msg = f"Configuration file not found: {str(config_path)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        # Read YAML file as raw text:
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_text = f.read()

        # Replace escaped backslashes for Windows compatibility:
        yaml_text = yaml_text.replace('\\\\', '/')  # Double backslash case
        yaml_text = yaml_text.replace('\\', '/')    # Single backslash case

        # Parse the modified YAML:
        try:
            raw_config = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in {config_path}: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        # Convert paths:
        processed_config = _convert_paths(raw_config)
        config = Box(processed_config)

        _validate_config(config, ctx)
        return config

    except ctx.errors.ApplicationError:
        raise
    except Exception as e:
        error_msg = f"Failed to load configuration: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

#%%