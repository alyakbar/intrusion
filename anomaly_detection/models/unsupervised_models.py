"""
Unsupervised machine learning models for anomaly detection.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans, DBSCAN
from sklearn.neighbors import LocalOutlierFactor
from typing import Dict, Any
import joblib
import os


class UnsupervisedModels:
    """Collection of unsupervised learning models."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize unsupervised models.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all unsupervised models."""
        # Isolation Forest
        if_config = self.config.get('isolation_forest', {})
        self.models['isolation_forest'] = IsolationForest(
            n_estimators=if_config.get('n_estimators', 100),
            contamination=if_config.get('contamination', 0.1),
            random_state=if_config.get('random_state', 42),
            n_jobs=-1
        )
        
        # K-Means
        kmeans_config = self.config.get('kmeans', {})
        self.models['kmeans'] = KMeans(
            n_clusters=kmeans_config.get('n_clusters', 5),
            random_state=kmeans_config.get('random_state', 42),
            n_init=10
        )
        
        # DBSCAN
        dbscan_config = self.config.get('dbscan', {})
        self.models['dbscan'] = DBSCAN(
            eps=dbscan_config.get('eps', 0.5),
            min_samples=dbscan_config.get('min_samples', 5),
            n_jobs=-1
        )
        
        # Local Outlier Factor
        self.models['lof'] = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.1,
            novelty=True,
            n_jobs=-1
        )
    
    def train(self, model_name: str, X_train: np.ndarray):
        """
        Train a specific unsupervised model.
        
        Args:
            model_name: Name of the model to train
            X_train: Training features
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        print(f"Training {model_name}...")
        self.models[model_name].fit(X_train)
        print(f"{model_name} training complete!")
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using a specific model.
        
        Args:
            model_name: Name of the model
            X: Feature array
            
        Returns:
            Predictions (1 for normal, -1 for anomaly)
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        predictions = self.models[model_name].predict(X)
        
        # Convert to binary: 1 for normal, 0 for anomaly
        if model_name in ['isolation_forest', 'lof']:
            # Isolation Forest and LOF return 1 for inliers, -1 for outliers
            predictions = np.where(predictions == 1, 0, 1)
        elif model_name == 'kmeans':
            # For K-Means, we need to define anomalies based on distance to centroid
            distances = self.models[model_name].transform(X)
            min_distances = np.min(distances, axis=1)
            threshold = np.percentile(min_distances, 90)
            predictions = np.where(min_distances > threshold, 1, 0)
        elif model_name == 'dbscan':
            # DBSCAN: -1 means noise (anomaly), others are clusters
            predictions = np.where(predictions == -1, 1, 0)
        
        return predictions
    
    def get_anomaly_scores(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores for samples.
        
        Args:
            model_name: Name of the model
            X: Feature array
            
        Returns:
            Anomaly scores
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        if model_name == 'isolation_forest':
            # Decision function returns anomaly scores
            scores = -self.models[model_name].decision_function(X)
        elif model_name == 'lof':
            # LOF score
            scores = -self.models[model_name].score_samples(X)
        elif model_name == 'kmeans':
            # Distance to nearest centroid
            distances = self.models[model_name].transform(X)
            scores = np.min(distances, axis=1)
        elif model_name == 'dbscan':
            # DBSCAN doesn't have a built-in scoring method
            # Use a simple heuristic based on cluster membership
            predictions = self.models[model_name].fit_predict(X)
            scores = np.where(predictions == -1, 1.0, 0.0)
        else:
            scores = np.zeros(len(X))
        
        # Normalize scores to [0, 1]
        if len(scores) > 0 and scores.max() != scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        return scores
    
    def get_model(self, model_name: str):
        """
        Get a specific model instance.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model instance
        """
        return self.models.get(model_name)
    
    def save_model(self, model_name: str, save_path: str):
        """
        Save a trained model to disk.
        
        Args:
            model_name: Name of the model
            save_path: Path to save the model
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(self.models[model_name], save_path)
        print(f"Model saved: {save_path}")
    
    def load_model(self, model_name: str, load_path: str):
        """
        Load a trained model from disk.
        
        Args:
            model_name: Name of the model
            load_path: Path to load the model from
        """
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        self.models[model_name] = joblib.load(load_path)
        print(f"Model loaded: {load_path}")