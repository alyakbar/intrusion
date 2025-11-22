"""
Data loading module for NSL-KDD and CICIDS datasets.
"""

import pandas as pd
import numpy as np
import os
from typing import Tuple, Optional, List
from sklearn.model_selection import train_test_split


class DataLoader:
    """Data loader for network anomaly detection datasets."""
    
    def __init__(self, data_path: str = 'data/raw'):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to raw data directory
        """
        self.data_path = data_path
        self.nsl_kdd_columns = self._get_nsl_kdd_columns()
    
    def _get_nsl_kdd_columns(self) -> List[str]:
        """Get column names for NSL-KDD dataset."""
        return [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins',
            'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
            'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
            'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
            'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
            'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
            'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
        ]
    
    def load_nsl_kdd(
        self,
        train_file: str = 'KDDTrain+.txt',
        test_file: str = 'KDDTest+.txt'
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load NSL-KDD dataset.
        
        Args:
            train_file: Training data file name
            test_file: Test data file name
            
        Returns:
            Tuple of (train_data, test_data)
        """
        train_path = os.path.join(self.data_path, 'nsl-kdd', train_file)
        test_path = os.path.join(self.data_path, 'nsl-kdd', test_file)
        
        if not os.path.exists(train_path):
            raise FileNotFoundError(f"Training file not found: {train_path}")
        if not os.path.exists(test_path):
            raise FileNotFoundError(f"Test file not found: {test_path}")
        
        train_data = pd.read_csv(train_path, header=None, names=self.nsl_kdd_columns)
        test_data = pd.read_csv(test_path, header=None, names=self.nsl_kdd_columns)
        
        return train_data, test_data
    
    def load_cicids(
        self,
        file_pattern: str = '*.csv'
    ) -> pd.DataFrame:
        """
        Load CICIDS dataset.
        
        Args:
            file_pattern: File pattern to match CSV files
            
        Returns:
            Combined dataframe
        """
        cicids_path = os.path.join(self.data_path, 'cicids')
        
        if not os.path.exists(cicids_path):
            raise FileNotFoundError(f"CICIDS directory not found: {cicids_path}")
        
        csv_files = [f for f in os.listdir(cicids_path) if f.endswith('.csv')]
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in: {cicids_path}")
        
        dataframes = []
        for csv_file in csv_files:
            file_path = os.path.join(cicids_path, csv_file)
            df = pd.read_csv(file_path)
            dataframes.append(df)
        
        combined_data = pd.concat(dataframes, ignore_index=True)
        return combined_data
    
    def load_custom_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load custom CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dataframe
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return pd.read_csv(file_path)
    
    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        random_state: int = 42
    ) -> Tuple[np.ndarray, ...]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            X: Feature array
            y: Label array
            test_size: Proportion of test set
            validation_size: Proportion of validation set
            random_state: Random seed
            
        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: separate validation set from training set
        val_size_adjusted = validation_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted,
            random_state=random_state, stratify=y_temp
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def save_processed_data(
        self,
        data: pd.DataFrame,
        filename: str,
        output_path: str = 'data/processed'
    ) -> None:
        """
        Save processed data to file.
        
        Args:
            data: Dataframe to save
            filename: Output filename
            output_path: Output directory path
        """
        os.makedirs(output_path, exist_ok=True)
        file_path = os.path.join(output_path, filename)
        data.to_csv(file_path, index=False)
        print(f"Data saved to: {file_path}")