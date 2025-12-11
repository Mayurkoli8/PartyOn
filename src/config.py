"""
Configuration management for the Audio Streamer server.

Handles loading, validating, and providing default configuration values.
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional


@dataclass
class ServerConfig:
    """Server configuration with sensible defaults."""
    
    http_port: int = 5000
    ws_port: int = 8765
    sample_rate: int = 44100
    channels: int = 2
    block_size: int = 1024
    log_level: str = "INFO"
    max_reconnect_attempts: int = 10
    client_timeout_seconds: int = 30


def load_config(path: str = "config.json") -> ServerConfig:
    """
    Load configuration from JSON file, creating template if missing.
    
    Args:
        path: Path to the configuration file.
        
    Returns:
        ServerConfig instance with loaded or default values.
    """
    config_path = Path(path)
    
    if not config_path.exists():
        # Create template config file with defaults
        default_config = ServerConfig()
        config_path.write_text(
            json.dumps(asdict(default_config), indent=4),
            encoding='utf-8'
        )
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = ServerConfig(**{
            k: v for k, v in data.items() 
            if k in ServerConfig.__dataclass_fields__
        })
        return validate_config(config)
        
    except json.JSONDecodeError as e:
        logging.warning(f"Invalid JSON in config file: {e}. Using defaults.")
        return ServerConfig()
    except Exception as e:
        logging.warning(f"Error loading config: {e}. Using defaults.")
        return ServerConfig()


def validate_config(config: ServerConfig) -> ServerConfig:
    """
    Validate configuration values, replacing invalid with defaults.
    
    Args:
        config: ServerConfig instance to validate.
        
    Returns:
        ServerConfig with validated values.
    """
    defaults = ServerConfig()
    
    # Validate sample_rate
    valid_sample_rates = [22050, 44100, 48000]
    if config.sample_rate not in valid_sample_rates:
        logging.warning(
            f"Invalid sample_rate {config.sample_rate}. "
            f"Using default {defaults.sample_rate}."
        )
        config.sample_rate = defaults.sample_rate
    
    # Validate buffer_size (block_size)
    if not (512 <= config.block_size <= 4096):
        logging.warning(
            f"Invalid block_size {config.block_size}. "
            f"Using default {defaults.block_size}."
        )
        config.block_size = defaults.block_size
    
    # Validate log_level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if config.log_level.upper() not in valid_levels:
        logging.warning(
            f"Invalid log_level {config.log_level}. "
            f"Using default {defaults.log_level}."
        )
        config.log_level = defaults.log_level
    else:
        config.log_level = config.log_level.upper()
    
    # Validate ports
    if not (1 <= config.http_port <= 65535):
        config.http_port = defaults.http_port
    
    if not (1 <= config.ws_port <= 65535):
        config.ws_port = defaults.ws_port
    
    return config
