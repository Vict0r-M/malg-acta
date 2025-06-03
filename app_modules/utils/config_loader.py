"""Configuration loading and validation for Malg-ACTA"""

#%% Dependencies:

import yaml
from box import Box
from pathlib import Path
from typing import Any, Dict, Union

#%% Helper Functions:

def _convert_path_to_absolute(path_str: str) -> Path:
    """Convert any path string to absolute path"""

    path = Path(path_str)

    # Case 1 - System absolute paths:
    if path.is_absolute():
        return path

    # Case 2 - Project-relative paths:
    project_root = Path(__file__).parent.parent.parent
    return (project_root / path).resolve()

def _convert_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert path strings to Path objects in a dictionary"""

    converted = {}

    for key, value in config.items():
        if isinstance(value, dict):
            # Recursively process nested dictionaries:
            converted[key] = _convert_paths(value)
        elif isinstance(value, str) and key.endswith(('path', 'dir', 'file')):
            # Convert string paths to Path objects:
            converted[key] = _convert_path_to_absolute(value)
        else:
            converted[key] = value

    return converted

def _validate_paths(config: Box, ctx: Any) -> None:
    """Validate all paths in config recursively"""

    for key, value in config.items():
        if isinstance(value, Path):
            try:
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

def _validate_data_paths(config: Box, ctx: Any) -> None:
    """Validate data paths configuration"""

    if 'data_paths' not in config:
        error_msg = "Missing required section: data_paths"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    required_data_paths = [
        'demo_data', 'clients_file', 'concrete_classes_file', 
        'registry_file', 'input_exchange', 'output_exchange'
    ]

    for path_name in required_data_paths:
        if path_name not in config.data_paths:
            error_msg = f"data_paths.{path_name} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

def _validate_output_paths(config: Box, ctx: Any) -> None:
    """Validate output paths configuration"""

    if 'output_paths' not in config:
        error_msg = "Missing required section: output_paths"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    required_output_paths = ['reports_dir', 'excel_dir', 'pdf_dir']

    for path_name in required_output_paths:
        if path_name not in config.output_paths:
            error_msg = f"output_paths.{path_name} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

def _validate_protocols(config: Box, ctx: Any) -> None:
    """Validate protocols configuration"""

    if 'protocols' not in config:
        error_msg = "Missing required section: protocols"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    required_protocols = [
        'cube_compression_testing', 'cube_frost_testing',
        'beam_compression_testing', 'beam_flexural_testing'
    ]

    for protocol_name in required_protocols:
        if protocol_name not in config.protocols:
            error_msg = f"protocols.{protocol_name} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        protocol_config = config.protocols[protocol_name]

        # Validate required protocol fields:
        if 'requires_scale' not in protocol_config:
            error_msg = f"protocols.{protocol_name}.requires_scale must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        if 'requires_press' not in protocol_config:
            error_msg = f"protocols.{protocol_name}.requires_press must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        if not isinstance(protocol_config.requires_scale, bool):
            error_msg = f"protocols.{protocol_name}.requires_scale must be boolean"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

        if not isinstance(protocol_config.requires_press, bool):
            error_msg = f"protocols.{protocol_name}.requires_press must be boolean"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

def _validate_java_integration(config: Box, ctx: Any) -> None:
    """Validate Java integration configuration"""

    if 'java_integration' not in config:
        error_msg = "Missing required section: java_integration"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    required_java_fields = ['gui_jar_path', 'cli_class', 'gui_class']

    for field_name in required_java_fields:
        if field_name not in config.java_integration:
            error_msg = f"java_integration.{field_name} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

def _validate_output_generation(config: Box, ctx: Any) -> None:
    """Validate output generation configuration"""

    if 'output_generation' not in config:
        error_msg = "Missing required section: output_generation"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

    required_output_fields = ['pdf_script', 'excel_script']

    for field_name in required_output_fields:
        if field_name not in config.output_generation:
            error_msg = f"output_generation.{field_name} must be specified"
            ctx.logger.error(error_msg)
            raise ctx.errors.ConfigurationError(error_msg)

def _validate_config(config: Box, ctx: Any) -> None:
    """Validate configuration parameters"""

    # First validate all paths:
    _validate_paths(config, ctx)

    # Validate required sections:
    _validate_logging(config, ctx)
    _validate_data_paths(config, ctx)
    _validate_output_paths(config, ctx)
    _validate_protocols(config, ctx)
    _validate_java_integration(config, ctx)
    _validate_output_generation(config, ctx)

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

        # Replace escaped backslashes for cross-platform compatibility:
        yaml_text = yaml_text.replace('\\\\', '/')
        yaml_text = yaml_text.replace('\\', '/')

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

    except ctx.errors.MalgActaError:
        raise
    except Exception as e:
        error_msg = f"Failed to load configuration: {str(e)}"
        ctx.logger.error(error_msg)
        raise ctx.errors.ConfigurationError(error_msg)

#%%