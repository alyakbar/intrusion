"""
Model evaluation module with comprehensive metrics.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from typing import Dict, Any, Tuple
import pandas as pd


class ModelEvaluator:
    """Evaluator for model performance metrics."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.results = {}
    
    def evaluate_model(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray = None,
        model_name: str = 'model'
    ) -> Dict[str, Any]:
        """
        Evaluate model performance with multiple metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (optional)
            model_name: Name of the model
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, average='binary', zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, average='binary', zero_division=0)
        metrics['f1_score'] = f1_score(y_true, y_pred, average='binary', zero_division=0)
        
        # ROC-AUC if probabilities are provided
        if y_proba is not None:
            try:
                if len(y_proba.shape) > 1 and y_proba.shape[1] > 1:
                    y_proba = y_proba[:, 1]
                metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            except:
                metrics['roc_auc'] = None
        else:
            metrics['roc_auc'] = None
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm
        
        # Additional metrics from confusion matrix
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['true_positive'] = int(tp)
            metrics['true_negative'] = int(tn)
            metrics['false_positive'] = int(fp)
            metrics['false_negative'] = int(fn)
            
            # Specificity
            metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            # False Positive Rate
            metrics['fpr'] = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            # False Negative Rate
            metrics['fnr'] = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        # Store results
        self.results[model_name] = metrics
        
        return metrics
    
    def print_evaluation(self, model_name: str):
        """
        Print evaluation metrics for a model.
        
        Args:
            model_name: Name of the model
        """
        if model_name not in self.results:
            print(f"No evaluation results for {model_name}")
            return
        
        metrics = self.results[model_name]
        
        print(f"\n{'='*60}")
        print(f"Model Evaluation: {model_name}")
        print(f"{'='*60}")
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1-Score:  {metrics['f1_score']:.4f}")
        
        if metrics['roc_auc'] is not None:
            print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        
        if 'specificity' in metrics:
            print(f"Specificity: {metrics['specificity']:.4f}")
        
        print(f"\nConfusion Matrix:")
        print(metrics['confusion_matrix'])
        
        if 'true_positive' in metrics:
            print(f"\nTP: {metrics['true_positive']}, TN: {metrics['true_negative']}")
            print(f"FP: {metrics['false_positive']}, FN: {metrics['false_negative']}")
        
        print(f"{'='*60}\n")
    
    def get_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        target_names: list = None
    ) -> str:
        """
        Get detailed classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            target_names: Names of target classes
            
        Returns:
            Classification report string
        """
        if target_names is None:
            target_names = ['Normal', 'Anomaly']
        
        return classification_report(y_true, y_pred, target_names=target_names)
    
    def compare_models(self) -> pd.DataFrame:
        """
        Compare all evaluated models.
        
        Returns:
            Dataframe with comparison metrics
        """
        if not self.results:
            print("No models to compare")
            return pd.DataFrame()
        
        comparison_data = []
        
        for model_name, metrics in self.results.items():
            row = {
                'Model': model_name,
                'Accuracy': metrics['accuracy'],
                'Precision': metrics['precision'],
                'Recall': metrics['recall'],
                'F1-Score': metrics['f1_score']
            }
            
            if metrics['roc_auc'] is not None:
                row['ROC-AUC'] = metrics['roc_auc']
            
            if 'specificity' in metrics:
                row['Specificity'] = metrics['specificity']
            
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('F1-Score', ascending=False)
        
        return df
    
    def get_best_model(self, metric: str = 'f1_score') -> Tuple[str, float]:
        """
        Get the best performing model based on a metric.
        
        Args:
            metric: Metric to use for comparison
            
        Returns:
            Tuple of (model_name, metric_value)
        """
        if not self.results:
            return None, None
        
        best_model = None
        best_score = -1
        
        for model_name, metrics in self.results.items():
            score = metrics.get(metric, 0)
            if score > best_score:
                best_score = score
                best_model = model_name
        
        return best_model, best_score
    
    def calculate_detection_rate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate detection rates for anomalies.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Dictionary with detection rates
        """
        # True Positive Rate (Detection Rate for anomalies)
        anomaly_mask = y_true == 1
        detected_anomalies = np.sum((y_true == 1) & (y_pred == 1))
        total_anomalies = np.sum(anomaly_mask)
        
        detection_rate = detected_anomalies / total_anomalies if total_anomalies > 0 else 0
        
        # False Alarm Rate
        normal_mask = y_true == 0
        false_alarms = np.sum((y_true == 0) & (y_pred == 1))
        total_normal = np.sum(normal_mask)
        
        false_alarm_rate = false_alarms / total_normal if total_normal > 0 else 0
        
        return {
            'detection_rate': detection_rate,
            'false_alarm_rate': false_alarm_rate,
            'detected_anomalies': int(detected_anomalies),
            'total_anomalies': int(total_anomalies),
            'false_alarms': int(false_alarms),
            'total_normal': int(total_normal)
        }