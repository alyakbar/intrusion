"""
Model training module with comprehensive training pipeline.
"""

import numpy as np
from typing import Dict, Any, List, Optional
import os
from ..models.supervised_models import SupervisedModels
from ..models.unsupervised_models import UnsupervisedModels
from ..models.neural_networks import AutoEncoder, LSTMDetector, DNNClassifier
from ..utils.logger import LoggerFactory


class ModelTrainer:
    """Unified trainer for all model types."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize model trainer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = LoggerFactory.get_logger('ModelTrainer')
        
        # Initialize model collections
        supervised_config = config.get('models', {}).get('supervised', {})
        unsupervised_config = config.get('models', {}).get('unsupervised', {})
        
        self.supervised_models = SupervisedModels(supervised_config)
        self.unsupervised_models = UnsupervisedModels(unsupervised_config)
        self.neural_models = {}
        
        self.save_dir = config.get('model_storage', {}).get('save_dir', 'saved_models')
    
    def train_supervised_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray
    ):
        """
        Train a supervised model.
        
        Args:
            model_name: Name of the model
            X_train: Training features
            y_train: Training labels
        """
        self.logger.info(f"Training supervised model: {model_name}")
        self.supervised_models.train(model_name, X_train, y_train)
        
        # Save model
        save_path = os.path.join(self.save_dir, 'supervised', f'{model_name}.joblib')
        self.supervised_models.save_model(model_name, save_path)
        self.logger.info(f"Model saved: {save_path}")
    
    def train_unsupervised_model(
        self,
        model_name: str,
        X_train: np.ndarray
    ):
        """
        Train an unsupervised model.
        
        Args:
            model_name: Name of the model
            X_train: Training features
        """
        self.logger.info(f"Training unsupervised model: {model_name}")
        self.unsupervised_models.train(model_name, X_train)
        
        # Save model
        save_path = os.path.join(self.save_dir, 'unsupervised', f'{model_name}.joblib')
        self.unsupervised_models.save_model(model_name, save_path)
        self.logger.info(f"Model saved: {save_path}")
    
    def train_autoencoder(
        self,
        X_train: np.ndarray,
        X_val: np.ndarray
    ):
        """
        Train autoencoder model.
        
        Args:
            X_train: Training features
            X_val: Validation features
        """
        self.logger.info("Training Autoencoder")
        
        ae_config = self.config.get('models', {}).get('neural_networks', {}).get('autoencoder', {})
        autoencoder = AutoEncoder(input_dim=X_train.shape[1], config=ae_config)
        
        save_path = os.path.join(self.save_dir, 'neural_networks', 'autoencoder.h5')
        autoencoder.train(X_train, X_val, save_path)
        
        self.neural_models['autoencoder'] = autoencoder
        self.logger.info(f"Autoencoder saved: {save_path}")
    
    def train_dnn(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ):
        """
        Train DNN classifier.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        self.logger.info("Training DNN Classifier")
        
        dnn_config = self.config.get('models', {}).get('neural_networks', {}).get('dnn', {})
        dnn = DNNClassifier(input_dim=X_train.shape[1], config=dnn_config)
        
        save_path = os.path.join(self.save_dir, 'neural_networks', 'dnn.h5')
        dnn.train(X_train, y_train, X_val, y_val, save_path)
        
        self.neural_models['dnn'] = dnn
        self.logger.info(f"DNN saved: {save_path}")
    
    def train_all_supervised(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ):
        """
        Train all supervised models.
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        model_names = ['random_forest', 'gradient_boosting', 'svm', 
                      'logistic_regression', 'decision_tree']
        
        for model_name in model_names:
            try:
                self.train_supervised_model(model_name, X_train, y_train)
            except Exception as e:
                self.logger.error(f"Error training {model_name}: {str(e)}")
    
    def train_all_unsupervised(
        self,
        X_train: np.ndarray
    ):
        """
        Train all unsupervised models.
        
        Args:
            X_train: Training features
        """
        model_names = ['isolation_forest', 'kmeans', 'dbscan', 'lof']
        
        for model_name in model_names:
            try:
                self.train_unsupervised_model(model_name, X_train)
            except Exception as e:
                self.logger.error(f"Error training {model_name}: {str(e)}")
    
    def train_all_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ):
        """
        Train all models (supervised, unsupervised, and neural networks).
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        self.logger.info("Starting training for all models...")
        
        # Train supervised models
        self.logger.info("Training supervised models...")
        self.train_all_supervised(X_train, y_train)
        
        # Train unsupervised models
        self.logger.info("Training unsupervised models...")
        self.train_all_unsupervised(X_train)
        
        # Train neural networks
        self.logger.info("Training neural networks...")
        try:
            self.train_autoencoder(X_train, X_val)
        except Exception as e:
            self.logger.error(f"Error training autoencoder: {str(e)}")
        
        try:
            self.train_dnn(X_train, y_train, X_val, y_val)
        except Exception as e:
            self.logger.error(f"Error training DNN: {str(e)}")
        
        self.logger.info("All model training complete!")
    
    def load_models(self):
        """Load all saved models."""
        self.logger.info("Loading saved models...")
        
        # Load supervised models
        supervised_dir = os.path.join(self.save_dir, 'supervised')
        if os.path.exists(supervised_dir):
            for model_file in os.listdir(supervised_dir):
                if model_file.endswith('.joblib'):
                    model_name = model_file.replace('.joblib', '')
                    model_path = os.path.join(supervised_dir, model_file)
                    try:
                        self.supervised_models.load_model(model_name, model_path)
                    except Exception as e:
                        self.logger.error(f"Error loading {model_name}: {str(e)}")
        
        # Load unsupervised models
        unsupervised_dir = os.path.join(self.save_dir, 'unsupervised')
        if os.path.exists(unsupervised_dir):
            for model_file in os.listdir(unsupervised_dir):
                if model_file.endswith('.joblib'):
                    model_name = model_file.replace('.joblib', '')
                    model_path = os.path.join(unsupervised_dir, model_file)
                    try:
                        self.unsupervised_models.load_model(model_name, model_path)
                    except Exception as e:
                        self.logger.error(f"Error loading {model_name}: {str(e)}")
        
        self.logger.info("Model loading complete!")