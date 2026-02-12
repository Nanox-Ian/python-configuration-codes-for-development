import os
import json
import logging
import traceback
from typing import Dict, Any
from pydantic import BaseModel, ValidationError

# Set up logging with DEBUG level for complete trace
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigSchema(BaseModel):
    """Pydantic model for configuration validation."""
    app_name: str
    environment: str
    debug: bool
    db_url: str

def load_config(file_path: str, env_override: bool = True) -> ConfigSchema:
    """Load and validate configuration from a JSON file and environment variables.
    
    Args:
        file_path (str): Path to the configuration file (JSON format).
        env_override (bool): Whether to override config values with environment variables.

        Returns:
        ConfigSchema: Validated configuration object.

        Raises:
        ValueError: If the configuration data is invalid or missing required fields.
    """
    logger.info(f"Loading config from {file_path}...")  # Debugging line
    
    config = _load_config_from_file(file_path)
    
    if config is None:
        logger.error(f"Config loaded as None from {file_path}. Exiting.")
        raise ValueError("Config is None. Please check the file content.")

    if env_override:
        logger.info("Applying environment variable overrides...")  # Debugging line
        config = _apply_environment_overrides(config)

    try:
        logger.info(f"Validating config: {config}")  # Debugging line
        return ConfigSchema(**config)
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}", exc_info=True)
        raise ValueError("Invalid configuration data")

def _load_config_from_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file.
    
    Args:
        file_path (str): Path to the configuration file.

    Returns:
        Dict[str, Any]: Parsed JSON data.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            if not config:
                logger.error(f"Config file {file_path} is empty.")
                return None
            return config
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {file_path}", exc_info=True)
        raise e
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from the configuration file: {file_path}", exc_info=True)
        raise e
    except ValueError as e:
        logger.error(f"Failed to load config: {e}", exc_info=True)
        raise e

def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override configuration values with environment variables if they exist.
    
    Args:
        config (Dict[str, Any]): Original configuration dictionary.

    Returns:
        Dict[str, Any]: Updated configuration dictionary with environment overrides.
    """
    logger.debug(f"Applying environment overrides to config: {config}")
    for key in config.keys():
        env_value = os.getenv(key.upper())
        if env_value is not None:
            config[key] = env_value
            logger.info(f"Overriding '{key}' with environment variable.")

    return config

if __name__ == "__main__":
    # Example usage
    try:
        config = load_config('config.json')
        logger.info(f"Configuration loaded successfully: {config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
