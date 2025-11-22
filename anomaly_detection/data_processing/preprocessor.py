"""
Data preprocessing module for cleaning and transforming network traffic data.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Optional, List


class DataPreprocessor:
    """Preprocessor for network anomaly detection data."""
    
    def __init__(self, scaling_method: str = 'standard'):
        """
        Initialize preprocessor.
        
        Args:
            scaling_method: Scaling method ('standard', 'minmax', 'robust')
        """
        self.scaling_method = scaling_method
        self.scaler = self._get_scaler()
        self.label_encoders = {}
        self.feature_names = None
        self.fitted = False
    
    def _get_scaler(self):
        """Get scaler based on scaling method."""
        if self.scaling_method == 'standard':
            return StandardScaler()
        elif self.scaling_method == 'minmax':
            return MinMaxScaler()
        elif self.scaling_method == 'robust':
            return RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method: {self.scaling_method}")
    
    def handle_missing_values(
        self,
        data: pd.DataFrame,
        strategy: str = 'mean'
    ) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            data: Input dataframe
            strategy: Imputation strategy ('mean', 'median', 'most_frequent')
            
        Returns:
            Dataframe with imputed values
        """
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        # Impute numeric columns
        if len(numeric_cols) > 0:
            numeric_imputer = SimpleImputer(strategy=strategy)
            data[numeric_cols] = numeric_imputer.fit_transform(data[numeric_cols])
        
        # Impute categorical columns
        if len(categorical_cols) > 0:
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            data[categorical_cols] = categorical_imputer.fit_transform(data[categorical_cols])
        
        return data
    
    def encode_categorical_features(
        self,
        data: pd.DataFrame,
        categorical_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Encode categorical features using label encoding.
        
        Args:
            data: Input dataframe
            categorical_columns: List of categorical column names
            
        Returns:
            Dataframe with encoded features
        """
        if categorical_columns is None:
            categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
        
        data_encoded = data.copy()
        
        for col in categorical_columns:
            if col in data_encoded.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    data_encoded[col] = self.label_encoders[col].fit_transform(
                        data_encoded[col].astype(str)
                    )
                else:
                    data_encoded[col] = self.label_encoders[col].transform(
                        data_encoded[col].astype(str)
                    )
        
        return data_encoded
    
    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows.
        
        Args:
            data: Input dataframe
            
        Returns:
            Dataframe without duplicates
        """
        initial_shape = data.shape
        data_cleaned = data.drop_duplicates()
        removed = initial_shape[0] - data_cleaned.shape[0]
        print(f"Removed {removed} duplicate rows")
        return data_cleaned
    
    def remove_outliers(
        self,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from numeric columns.
        
        Args:
            data: Input dataframe
            columns: Columns to check for outliers
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Dataframe without outliers
        """
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        data_cleaned = data.copy()
        
        if method == 'iqr':
            for col in columns:
                if col in data_cleaned.columns:
                    Q1 = data_cleaned[col].quantile(0.25)
                    Q3 = data_cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    data_cleaned = data_cleaned[
                        (data_cleaned[col] >= lower_bound) &
                        (data_cleaned[col] <= upper_bound)
                    ]
        
        elif method == 'zscore':
            from scipy import stats
            for col in columns:
                if col in data_cleaned.columns:
                    z_scores = np.abs(stats.zscore(data_cleaned[col]))
                    data_cleaned = data_cleaned[z_scores < threshold]
        
        removed = len(data) - len(data_cleaned)
        print(f"Removed {removed} outlier rows")
        return data_cleaned
    
    def scale_features(
        self,
        X: np.ndarray,
        fit: bool = True
    ) -> np.ndarray:
        """
        Scale features using the specified scaling method.
        
        Args:
            X: Feature array
            fit: Whether to fit the scaler
            
        Returns:
            Scaled feature array
        """
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            self.fitted = True
        else:
            if not self.fitted:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def prepare_labels(
        self,
        labels: pd.Series,
        binary: bool = True
    ) -> Tuple[np.ndarray, dict]:
        """
        Prepare labels for training.
        
        Args:
            labels: Label series
            binary: Whether to convert to binary classification
            
        Returns:
            Tuple of (encoded_labels, label_mapping)
        """
        if binary:
            # Convert to binary: normal (0) vs anomaly (1)
            y = np.where(labels.str.lower() == 'normal', 0, 1)
            label_mapping = {0: 'normal', 1: 'anomaly'}
        else:
            # Multi-class classification
            le = LabelEncoder()
            y = le.fit_transform(labels)
            label_mapping = {i: label for i, label in enumerate(le.classes_)}
        
        return y, label_mapping
    
    def fit_transform(
        self,
        data: pd.DataFrame,
        label_column: str = 'label',
        binary_classification: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Complete preprocessing pipeline: fit and transform.
        
        Args:
            data: Input dataframe
            label_column: Name of label column
            binary_classification: Whether to use binary classification
            
        Returns:
            Tuple of (X_scaled, y, label_mapping)
        """
        # Separate features and labels
        y_raw = data[label_column]
        X_raw = data.drop(columns=[label_column])
        
        # Store feature names
        self.feature_names = X_raw.columns.tolist()
        
        # Handle missing values
        X_processed = self.handle_missing_values(X_raw)
        
        # Encode categorical features
        X_encoded = self.encode_categorical_features(X_processed)
        
        # Scale features
        X_scaled = self.scale_features(X_encoded.values, fit=True)
        
        # Prepare labels
        y, label_mapping = self.prepare_labels(y_raw, binary=binary_classification)
        
        return X_scaled, y, label_mapping
    
    def transform(
        self,
        data: pd.DataFrame,
        label_column: Optional[str] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Transform new data using fitted preprocessor.
        
        Args:
            data: Input dataframe
            label_column: Name of label column (optional)
            
        Returns:
            Tuple of (X_scaled, y) or just X_scaled if no labels
        """
        if not self.fitted:
            raise ValueError("Preprocessor not fitted. Call fit_transform first.")
        
        if label_column:
            y_raw = data[label_column]
            X_raw = data.drop(columns=[label_column])
        else:
            X_raw = data
            y_raw = None
        
        # Handle missing values
        X_processed = self.handle_missing_values(X_raw)
        
        # Encode categorical features
        X_encoded = self.encode_categorical_features(X_processed)
        
        # Scale features
        X_scaled = self.scale_features(X_encoded.values, fit=False)
        
        if y_raw is not None:
            y, _ = self.prepare_labels(y_raw)
            return X_scaled, y
        else:
            return X_scaled, None