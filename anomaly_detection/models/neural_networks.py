"""
Neural network models for anomaly detection using TensorFlow/Keras.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from typing import Dict, Any, Tuple
import os


class AutoEncoder:
    """Autoencoder for unsupervised anomaly detection."""
    
    def __init__(self, input_dim: int, config: Dict[str, Any]):
        """
        Initialize autoencoder.
        
        Args:
            input_dim: Input dimension
            config: Configuration dictionary
        """
        self.input_dim = input_dim
        self.config = config
        self.model = None
        self.encoder = None
        self.decoder = None
        self.history = None
        self._build_model()
    
    def _build_model(self):
        """Build autoencoder model."""
        encoding_dim = self.config.get('encoding_dim', 32)
        
        # Encoder
        encoder_input = layers.Input(shape=(self.input_dim,))
        encoded = layers.Dense(128, activation='relu')(encoder_input)
        encoded = layers.Dropout(0.2)(encoded)
        encoded = layers.Dense(64, activation='relu')(encoded)
        encoded = layers.Dense(encoding_dim, activation='relu')(encoded)
        
        self.encoder = models.Model(encoder_input, encoded)
        
        # Decoder
        decoder_input = layers.Input(shape=(encoding_dim,))
        decoded = layers.Dense(64, activation='relu')(decoder_input)
        decoded = layers.Dense(128, activation='relu')(decoded)
        decoded = layers.Dropout(0.2)(decoded)
        decoded = layers.Dense(self.input_dim, activation='sigmoid')(decoded)
        
        self.decoder = models.Model(decoder_input, decoded)
        
        # Autoencoder
        autoencoder_input = layers.Input(shape=(self.input_dim,))
        encoded_output = self.encoder(autoencoder_input)
        decoded_output = self.decoder(encoded_output)
        
        self.model = models.Model(autoencoder_input, decoded_output)
        
        # Compile
        learning_rate = self.config.get('learning_rate', 0.001)
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='mse',
            metrics=['mae']
        )
    
    def train(self, X_train: np.ndarray, X_val: np.ndarray, save_path: str = None):
        """
        Train the autoencoder.
        
        Args:
            X_train: Training data
            X_val: Validation data
            save_path: Path to save best model
        """
        epochs = self.config.get('epochs', 50)
        batch_size = self.config.get('batch_size', 128)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        ]
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            callbacks.append(
                ModelCheckpoint(save_path, save_best_only=True, monitor='val_loss')
            )
        
        self.history = self.model.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, X_val),
            callbacks=callbacks,
            verbose=1
        )
        
        print("Autoencoder training complete!")
    
    def get_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate reconstruction error.
        
        Args:
            X: Input data
            
        Returns:
            Reconstruction errors
        """
        reconstructions = self.model.predict(X, verbose=0)
        mse = np.mean(np.power(X - reconstructions, 2), axis=1)
        return mse
    
    def predict(self, X: np.ndarray, threshold: float = None) -> np.ndarray:
        """
        Predict anomalies based on reconstruction error.
        
        Args:
            X: Input data
            threshold: Error threshold (if None, use 95th percentile)
            
        Returns:
            Binary predictions (0: normal, 1: anomaly)
        """
        errors = self.get_reconstruction_error(X)
        
        if threshold is None:
            threshold = np.percentile(errors, 95)
        
        predictions = np.where(errors > threshold, 1, 0)
        return predictions
    
    def save(self, save_path: str):
        """Save model."""
        self.model.save(save_path)
    
    def load(self, load_path: str):
        """Load model."""
        self.model = keras.models.load_model(load_path)


class LSTMDetector:
    """LSTM model for sequence-based anomaly detection."""
    
    def __init__(self, input_shape: Tuple[int, int], config: Dict[str, Any]):
        """
        Initialize LSTM detector.
        
        Args:
            input_shape: (timesteps, features)
            config: Configuration dictionary
        """
        self.input_shape = input_shape
        self.config = config
        self.model = None
        self.history = None
        self._build_model()
    
    def _build_model(self):
        """Build LSTM model."""
        units = self.config.get('units', 64)
        dropout = self.config.get('dropout', 0.2)
        
        model = models.Sequential([
            layers.LSTM(units, return_sequences=True, input_shape=self.input_shape),
            layers.Dropout(dropout),
            layers.LSTM(units // 2, return_sequences=False),
            layers.Dropout(dropout),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        learning_rate = self.config.get('learning_rate', 0.001)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray, save_path: str = None):
        """
        Train LSTM model.
        
        Args:
            X_train: Training sequences
            y_train: Training labels
            X_val: Validation sequences
            y_val: Validation labels
            save_path: Path to save best model
        """
        epochs = self.config.get('epochs', 50)
        batch_size = self.config.get('batch_size', 128)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        ]
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            callbacks.append(
                ModelCheckpoint(save_path, save_best_only=True, monitor='val_accuracy')
            )
        
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        print("LSTM training complete!")
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Make predictions."""
        probabilities = self.model.predict(X, verbose=0)
        predictions = (probabilities > threshold).astype(int).flatten()
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities."""
        return self.model.predict(X, verbose=0)
    
    def save(self, save_path: str):
        """Save model."""
        self.model.save(save_path)
    
    def load(self, load_path: str):
        """Load model."""
        self.model = keras.models.load_model(load_path)


class DNNClassifier:
    """Deep Neural Network for supervised classification."""
    
    def __init__(self, input_dim: int, config: Dict[str, Any]):
        """
        Initialize DNN classifier.
        
        Args:
            input_dim: Input dimension
            config: Configuration dictionary
        """
        self.input_dim = input_dim
        self.config = config
        self.model = None
        self.history = None
        self._build_model()
    
    def _build_model(self):
        """Build DNN model."""
        hidden_layers = self.config.get('hidden_layers', [128, 64, 32])
        dropout = self.config.get('dropout', 0.3)
        
        model = models.Sequential()
        model.add(layers.Input(shape=(self.input_dim,)))
        
        for units in hidden_layers:
            model.add(layers.Dense(units, activation='relu'))
            model.add(layers.Dropout(dropout))
            model.add(layers.BatchNormalization())
        
        model.add(layers.Dense(1, activation='sigmoid'))
        
        learning_rate = self.config.get('learning_rate', 0.001)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall', tf.keras.metrics.AUC()]
        )
        
        self.model = model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray, save_path: str = None):
        """
        Train DNN model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            save_path: Path to save best model
        """
        epochs = self.config.get('epochs', 50)
        batch_size = self.config.get('batch_size', 128)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        ]
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            callbacks.append(
                ModelCheckpoint(save_path, save_best_only=True, monitor='val_accuracy')
            )
        
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        print("DNN training complete!")
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Make predictions."""
        probabilities = self.model.predict(X, verbose=0)
        predictions = (probabilities > threshold).astype(int).flatten()
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities."""
        return self.model.predict(X, verbose=0)
    
    def save(self, save_path: str):
        """Save model."""
        self.model.save(save_path)
    
    def load(self, load_path: str):
        """Load model."""
        self.model = keras.models.load_model(load_path)