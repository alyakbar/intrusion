"""
Tests for detection and inference modules.
"""

import pytest
import numpy as np
import pandas as pd
from anomaly_detection.inference.alert_manager import AlertManager
from anomaly_detection.training.evaluator import ModelEvaluator


def test_alert_manager_initialization():
    """Test alert manager initialization."""
    config = {
        'alerts': {
            'enabled': True,
            'severity_levels': {'high': 0.9, 'medium': 0.7, 'low': 0.5}
        }
    }
    
    manager = AlertManager(config)
    assert manager.enabled == True
    assert 'high' in manager.severity_levels


def test_create_alert():
    """Test alert creation."""
    config = {
        'alerts': {
            'enabled': True,
            'severity_levels': {'high': 0.9, 'medium': 0.7, 'low': 0.5},
            'notification_methods': ['console'],
            'alert_cooldown': 60
        }
    }
    
    manager = AlertManager(config)
    
    alert_data = {
        'severity': 'high',
        'anomaly_score': 0.95,
        'description': 'Test anomaly detected'
    }
    
    alert = manager.create_alert(alert_data)
    
    assert alert is not None
    assert alert['severity'] == 'high'
    assert 'id' in alert


def test_evaluator_metrics():
    """Test model evaluation metrics."""
    evaluator = ModelEvaluator()
    
    # Create test predictions
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.9, 0.4, 0.3, 0.8, 0.6, 0.85])
    
    metrics = evaluator.evaluate_model(y_true, y_pred, y_proba, 'test_model')
    
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1_score' in metrics
    assert 'roc_auc' in metrics
    assert 0 <= metrics['accuracy'] <= 1


def test_detection_rate_calculation():
    """Test detection rate calculation."""
    evaluator = ModelEvaluator()
    
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1])
    
    rates = evaluator.calculate_detection_rate(y_true, y_pred)
    
    assert 'detection_rate' in rates
    assert 'false_alarm_rate' in rates
    assert 0 <= rates['detection_rate'] <= 1
    assert 0 <= rates['false_alarm_rate'] <= 1


if __name__ == '__main__':
    pytest.main([__file__])