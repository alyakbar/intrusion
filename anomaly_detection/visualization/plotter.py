"""
Plotting and visualization module for analysis and results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc, confusion_matrix
from typing import Dict, Any, List, Optional
import os


class Plotter:
    """Visualization tools for anomaly detection results."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize plotter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        viz_config = config.get('visualization', {}).get('plots', {})
        self.save_plots = viz_config.get('save_plots', True)
        self.plot_format = viz_config.get('plot_format', 'png')
        self.dpi = viz_config.get('dpi', 300)
        
        # Set style
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        title: str = 'Confusion Matrix',
        save_path: Optional[str] = None
    ):
        """
        Plot confusion matrix.
        
        Args:
            cm: Confusion matrix
            title: Plot title
            save_path: Path to save plot
        """
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Normal', 'Anomaly'],
            yticklabels=['Normal', 'Anomaly']
        )
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        title: str = 'ROC Curve',
        save_path: Optional[str] = None
    ):
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities
            title: Plot title
            save_path: Path to save plot
        """
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_feature_importance(
        self,
        importance_scores: np.ndarray,
        feature_names: List[str],
        top_n: int = 20,
        title: str = 'Feature Importance',
        save_path: Optional[str] = None
    ):
        """
        Plot feature importance.
        
        Args:
            importance_scores: Feature importance scores
            feature_names: Names of features
            top_n: Number of top features to show
            title: Plot title
            save_path: Path to save plot
        """
        indices = np.argsort(importance_scores)[-top_n:]
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(top_n), importance_scores[indices])
        plt.yticks(range(top_n), [feature_names[i] for i in indices])
        plt.xlabel('Importance Score')
        plt.title(title)
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_model_comparison(
        self,
        comparison_df: pd.DataFrame,
        metric: str = 'F1-Score',
        title: str = 'Model Comparison',
        save_path: Optional[str] = None
    ):
        """
        Plot model comparison.
        
        Args:
            comparison_df: DataFrame with model comparison
            metric: Metric to plot
            title: Plot title
            save_path: Path to save plot
        """
        plt.figure(figsize=(12, 6))
        
        if metric in comparison_df.columns:
            comparison_df = comparison_df.sort_values(metric)
            plt.barh(comparison_df['Model'], comparison_df[metric])
            plt.xlabel(metric)
            plt.ylabel('Model')
            plt.title(title)
            plt.xlim([0, 1])
            
            # Add value labels
            for i, v in enumerate(comparison_df[metric]):
                plt.text(v + 0.01, i, f'{v:.4f}', va='center')
        
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_training_history(
        self,
        history: Dict[str, List[float]],
        title: str = 'Training History',
        save_path: Optional[str] = None
    ):
        """
        Plot training history for neural networks.
        
        Args:
            history: Training history dictionary
            title: Plot title
            save_path: Path to save plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot loss
        if 'loss' in history:
            axes[0].plot(history['loss'], label='Training Loss')
            if 'val_loss' in history:
                axes[0].plot(history['val_loss'], label='Validation Loss')
            axes[0].set_xlabel('Epoch')
            axes[0].set_ylabel('Loss')
            axes[0].set_title('Model Loss')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # Plot accuracy or other metric
        metric_key = None
        for key in ['accuracy', 'acc']:
            if key in history:
                metric_key = key
                break
        
        if metric_key:
            axes[1].plot(history[metric_key], label='Training Accuracy')
            val_key = f'val_{metric_key}'
            if val_key in history:
                axes[1].plot(history[val_key], label='Validation Accuracy')
            axes[1].set_xlabel('Epoch')
            axes[1].set_ylabel('Accuracy')
            axes[1].set_title('Model Accuracy')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_anomaly_distribution(
        self,
        anomaly_scores: np.ndarray,
        labels: np.ndarray,
        title: str = 'Anomaly Score Distribution',
        save_path: Optional[str] = None
    ):
        """
        Plot distribution of anomaly scores.
        
        Args:
            anomaly_scores: Anomaly scores
            labels: True labels
            title: Plot title
            save_path: Path to save plot
        """
        plt.figure(figsize=(10, 6))
        
        normal_scores = anomaly_scores[labels == 0]
        anomaly_scores_filtered = anomaly_scores[labels == 1]
        
        plt.hist(normal_scores, bins=50, alpha=0.5, label='Normal', color='blue')
        plt.hist(anomaly_scores_filtered, bins=50, alpha=0.5, label='Anomaly', color='red')
        
        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()
    
    def plot_detection_timeline(
        self,
        detections: List[Dict[str, Any]],
        title: str = 'Detection Timeline',
        save_path: Optional[str] = None
    ):
        """
        Plot timeline of detections.
        
        Args:
            detections: List of detection results
            title: Plot title
            save_path: Path to save plot
        """
        if not detections:
            print("No detections to plot")
            return
        
        timestamps = [d['timestamp'] for d in detections]
        anomaly_scores = [d.get('anomaly_score', 0) for d in detections]
        is_anomaly = [d.get('is_anomaly', False) for d in detections]
        
        plt.figure(figsize=(14, 6))
        colors = ['red' if a else 'blue' for a in is_anomaly]
        plt.scatter(timestamps, anomaly_scores, c=colors, alpha=0.6)
        plt.xlabel('Time')
        plt.ylabel('Anomaly Score')
        plt.title(title)
        plt.axhline(y=0.5, color='orange', linestyle='--', label='Threshold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path and self.save_plots:
            plt.savefig(save_path, dpi=self.dpi, format=self.plot_format)
        plt.show()
        plt.close()