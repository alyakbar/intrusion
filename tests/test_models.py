"""
Tests for model modules.
"""

import pytest
import numpy as np
from anomaly_detection.models.supervised_models import SupervisedModels
from anomaly_detection.models.unsupervised_models import UnsupervisedModels


def test_supervised_models_initialization():
    """Test supervised models initialization."""
    config = {
        'random_forest': {'n_estimators': 10, 'max_depth': 5},
        'svm': {'kernel': 'rbf', 'C': 1.0}
    }
    
    models = SupervisedModels(config)
    assert 'random_forest' in models.models
    assert 'svm' in models.models


def test_supervised_model_training():
    """Test supervised model training."""
    config = {
        'random_forest': {'n_estimators': 10, 'max_depth': 5}
    }
    
    models = SupervisedModels(config)
    
    # Create simple training data
    X_train = np.random.rand(100, 10)
    y_train = np.random.randint(0, 2, 100)
    
    models.train('random_forest', X_train, y_train)
    
    # Test prediction
    X_test = np.random.rand(10, 10)
    predictions = models.predict('random_forest', X_test)
    
    assert len(predictions) == 10
    assert all(p in [0, 1] for p in predictions)


def test_unsupervised_models_initialization():
    """Test unsupervised models initialization."""
    config = {
        'isolation_forest': {'n_estimators': 10, 'contamination': 0.1},
        'kmeans': {'n_clusters': 3}
    }
    
    models = UnsupervisedModels(config)
    assert 'isolation_forest' in models.models
    assert 'kmeans' in models.models


def test_unsupervised_model_training():
    """Test unsupervised model training."""
    config = {
        'isolation_forest': {'n_estimators': 10, 'contamination': 0.1}
    }
    
    models = UnsupervisedModels(config)
    
    # Create simple training data
    X_train = np.random.rand(100, 10)
    
    models.train('isolation_forest', X_train)
    
    # Test prediction
    X_test = np.random.rand(10, 10)
    predictions = models.predict('isolation_forest', X_test)
    
    assert len(predictions) == 10
    assert all(p in [0, 1] for p in predictions)


if __name__ == '__main__':
    pytest.main([__file__])