"""
Supervised machine learning models for anomaly detection.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from typing import Dict, Any, Optional
import joblib
import os


class SupervisedModels:
    """Collection of supervised learning models."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize supervised models.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all supervised models."""
        # Random Forest
        rf_config = self.config.get('random_forest', {})
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=rf_config.get('n_estimators', 100),
            max_depth=rf_config.get('max_depth', 20),
            random_state=rf_config.get('random_state', 42),
            n_jobs=-1
        )
        
        # Gradient Boosting
        gb_config = self.config.get('gradient_boosting', {})
        self.models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=gb_config.get('n_estimators', 100),
            learning_rate=gb_config.get('learning_rate', 0.1),
            max_depth=gb_config.get('max_depth', 5),
            random_state=gb_config.get('random_state', 42)
        )
        
        # Support Vector Machine
        svm_config = self.config.get('svm', {})
        self.models['svm'] = SVC(
            kernel=svm_config.get('kernel', 'rbf'),
            C=svm_config.get('C', 1.0),
            gamma=svm_config.get('gamma', 'scale'),
            probability=True,
            random_state=svm_config.get('random_state', 42)
        )
        
        # Logistic Regression
        self.models['logistic_regression'] = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )
        
        # Decision Tree
        self.models['decision_tree'] = DecisionTreeClassifier(
            max_depth=20,
            random_state=42
        )
    
    def train(self, model_name: str, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train a specific model.
        
        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training labels
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        print(f"Training {model_name}...")
        self.models[model_name].fit(X_train, y_train)
        print(f"{model_name} training complete!")
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using a specific model.
        
        Args:
            model_name: Name of the model
            X: Feature array
            
        Returns:
            Predictions
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        return self.models[model_name].predict(X)
    
    def predict_proba(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            model_name: Name of the model
            X: Feature array
            
        Returns:
            Probability predictions
        """
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        return self.models[model_name].predict_proba(X)
    
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
    
    def get_feature_importance(self, model_name: str) -> Optional[np.ndarray]:
        """
        Get feature importance for tree-based models.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Feature importance array or None
        """
        model = self.models.get(model_name)
        if hasattr(model, 'feature_importances_'):
            return model.feature_importances_
        return None