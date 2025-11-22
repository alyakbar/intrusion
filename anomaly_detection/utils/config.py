"""
Configuration management module for loading and accessing system configuration.
"""

import yaml
import os
from typing import Dict, Any


def load_config(config_path: str = 'configs/config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get nested configuration value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path (e.g., 'models.supervised.random_forest')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def update_config(config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
    """
    Update nested configuration value.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path
        value: New value
        
    Returns:
        Updated configuration dictionary
    """
    keys = key_path.split('.')
    current = config
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return config


def save_config(config: Dict[str, Any], config_path: str = 'configs/config.yaml') -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


class Config:
    """Configuration manager class."""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = load_config(config_path)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value."""
        return get_config_value(self.config, key_path, default)
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value."""
        self.config = update_config(self.config, key_path, value)
    
    def save(self) -> None:
        """Save configuration to file."""
        save_config(self.config, self.config_path)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = load_config(self.config_path)