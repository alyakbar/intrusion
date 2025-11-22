"""
Logging utilities for the anomaly detection system.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str,
    log_dir: str = 'logs',
    log_file: str = 'anomaly_detection.log',
    level: str = 'INFO',
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        log_file: Log file name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        format_string: Custom format string
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # File handler with rotation
    log_path = os.path.join(log_dir, log_file)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_model_performance(logger: logging.Logger, model_name: str, metrics: dict) -> None:
    """
    Log model performance metrics.
    
    Args:
        logger: Logger instance
        model_name: Name of the model
        metrics: Dictionary of performance metrics
    """
    logger.info(f"Model Performance - {model_name}")
    logger.info("=" * 50)
    for metric_name, metric_value in metrics.items():
        if isinstance(metric_value, float):
            logger.info(f"{metric_name}: {metric_value:.4f}")
        else:
            logger.info(f"{metric_name}: {metric_value}")
    logger.info("=" * 50)


def log_detection_event(logger: logging.Logger, event_data: dict) -> None:
    """
    Log an anomaly detection event.
    
    Args:
        logger: Logger instance
        event_data: Dictionary containing event information
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    severity = event_data.get('severity', 'UNKNOWN')
    score = event_data.get('anomaly_score', 0.0)
    description = event_data.get('description', 'No description')
    
    logger.warning(
        f"[{timestamp}] ANOMALY DETECTED - "
        f"Severity: {severity} | "
        f"Score: {score:.4f} | "
        f"Description: {description}"
    )


def log_training_progress(
    logger: logging.Logger,
    epoch: int,
    total_epochs: int,
    loss: float,
    metrics: dict
) -> None:
    """
    Log training progress.
    
    Args:
        logger: Logger instance
        epoch: Current epoch
        total_epochs: Total number of epochs
        loss: Current loss value
        metrics: Dictionary of training metrics
    """
    metrics_str = " | ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
    logger.info(
        f"Epoch [{epoch}/{total_epochs}] - "
        f"Loss: {loss:.4f} | {metrics_str}"
    )


class LoggerFactory:
    """Factory class for creating loggers."""
    
    _loggers = {}
    
    @classmethod
    def get_logger(
        cls,
        name: str,
        log_dir: str = 'logs',
        level: str = 'INFO'
    ) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
            level: Logging level
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = setup_logger(
                name=name,
                log_dir=log_dir,
                level=level
            )
        return cls._loggers[name]