"""
Tests for data processing modules.
"""

import pytest
import numpy as np
import pandas as pd
from anomaly_detection.data_processing.preprocessor import DataPreprocessor
from anomaly_detection.data_processing.feature_engineering import FeatureEngineer


def test_preprocessor_initialization():
    """Test preprocessor initialization."""
    preprocessor = DataPreprocessor(scaling_method='standard')
    assert preprocessor.scaling_method == 'standard'
    assert preprocessor.fitted == False


def test_handle_missing_values():
    """Test missing value handling."""
    preprocessor = DataPreprocessor()
    
    # Create test data with missing values
    data = pd.DataFrame({
        'feature1': [1, 2, np.nan, 4],
        'feature2': [5, np.nan, 7, 8],
        'label': ['normal', 'normal', 'anomaly', 'normal']
    })
    
    cleaned_data = preprocessor.handle_missing_values(data)
    assert cleaned_data.isnull().sum().sum() == 0


def test_remove_duplicates():
    """Test duplicate removal."""
    preprocessor = DataPreprocessor()
    
    data = pd.DataFrame({
        'feature1': [1, 2, 1, 4],
        'feature2': [5, 6, 5, 8],
        'label': ['normal', 'normal', 'normal', 'anomaly']
    })
    
    cleaned_data = preprocessor.remove_duplicates(data)
    assert len(cleaned_data) <= len(data)


def test_feature_engineer_initialization():
    """Test feature engineer initialization."""
    engineer = FeatureEngineer(n_features=10)
    assert engineer.n_features == 10


def test_create_statistical_features():
    """Test statistical feature creation."""
    engineer = FeatureEngineer()
    
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [5, 6, 7, 8]
    })
    
    enriched = engineer.create_statistical_features(data)
    assert 'mean_value' in enriched.columns
    assert 'std_value' in enriched.columns


if __name__ == '__main__':
    pytest.main([__file__])