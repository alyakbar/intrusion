"""
Example usage of the Network Anomaly Detection System.
This script demonstrates how to use the system with synthetic data.
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

# Import system components
from anomaly_detection.utils.config import load_config
from anomaly_detection.data_processing.preprocessor import DataPreprocessor
from anomaly_detection.data_processing.feature_engineering import FeatureEngineer
from anomaly_detection.models.supervised_models import SupervisedModels
from anomaly_detection.models.unsupervised_models import UnsupervisedModels
from anomaly_detection.training.evaluator import ModelEvaluator
from anomaly_detection.visualization.plotter import Plotter


def generate_synthetic_data(n_samples=1000, n_features=20):
    """Generate synthetic network traffic data for demonstration."""
    print("Generating synthetic data...")
    
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        weights=[0.9, 0.1],  # Imbalanced: 90% normal, 10% anomaly
        random_state=42
    )
    
    # Create DataFrame with feature names
    feature_names = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['label'] = ['normal' if label == 0 else 'anomaly' for label in y]
    
    print(f"Generated {n_samples} samples with {n_features} features")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    return df


def demonstrate_preprocessing():
    """Demonstrate data preprocessing."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Data Preprocessing")
    print("="*60)
    
    # Generate data
    data = generate_synthetic_data(n_samples=500)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor(scaling_method='standard')
    
    # Preprocess data
    X, y, label_mapping = preprocessor.fit_transform(data, label_column='label')
    
    print(f"\nPreprocessed data shape: {X.shape}")
    print(f"Label mapping: {label_mapping}")
    print(f"Feature statistics:")
    print(f"  Mean: {X.mean():.4f}")
    print(f"  Std: {X.std():.4f}")
    
    return X, y, preprocessor


def demonstrate_supervised_models(X, y):
    """Demonstrate supervised learning models."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Supervised Models")
    print("="*60)
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Initialize models
    config = {
        'random_forest': {'n_estimators': 50, 'max_depth': 10, 'random_state': 42},
        'gradient_boosting': {'n_estimators': 50, 'learning_rate': 0.1, 'random_state': 42}
    }
    
    models = SupervisedModels(config)
    evaluator = ModelEvaluator()
    
    # Train and evaluate each model
    for model_name in ['random_forest', 'gradient_boosting']:
        print(f"\n--- Training {model_name} ---")
        
        # Train
        models.train(model_name, X_train, y_train)
        
        # Predict
        y_pred = models.predict(model_name, X_test)
        y_proba = models.predict_proba(model_name, X_test)
        
        # Evaluate
        metrics = evaluator.evaluate_model(y_test, y_pred, y_proba[:, 1], model_name)
        evaluator.print_evaluation(model_name)
    
    # Compare models
    print("\n--- Model Comparison ---")
    comparison = evaluator.compare_models()
    print(comparison)
    
    return models, evaluator


def demonstrate_unsupervised_models(X, y):
    """Demonstrate unsupervised learning models."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Unsupervised Models")
    print("="*60)
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Initialize models
    config = {
        'isolation_forest': {'n_estimators': 50, 'contamination': 0.1, 'random_state': 42},
        'kmeans': {'n_clusters': 2, 'random_state': 42}
    }
    
    models = UnsupervisedModels(config)
    evaluator = ModelEvaluator()
    
    # Train and evaluate each model
    for model_name in ['isolation_forest', 'kmeans']:
        print(f"\n--- Training {model_name} ---")
        
        # Train
        models.train(model_name, X_train)
        
        # Predict
        y_pred = models.predict(model_name, X_test)
        
        # Evaluate
        metrics = evaluator.evaluate_model(y_test, y_pred, model_name=model_name)
        evaluator.print_evaluation(model_name)
    
    return models, evaluator


def demonstrate_visualization(X, y, models, evaluator):
    """Demonstrate visualization capabilities."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Visualization")
    print("="*60)
    
    # Load config
    config = load_config('configs/config.yaml')
    plotter = Plotter(config)
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Get predictions from best model
    y_pred = models.predict('random_forest', X_test)
    y_proba = models.predict_proba('random_forest', X_test)[:, 1]
    
    # Plot confusion matrix
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, y_pred)
    plotter.plot_confusion_matrix(cm, title='Random Forest - Confusion Matrix')
    
    # Plot ROC curve
    plotter.plot_roc_curve(y_test, y_proba, title='Random Forest - ROC Curve')
    
    # Plot model comparison
    comparison_df = evaluator.compare_models()
    plotter.plot_model_comparison(comparison_df, metric='F1-Score')
    
    print("Visualization complete!")


def main():
    """Main demonstration function."""
    print("\n" + "#"*60)
    print("# Network Anomaly Detection System - Demonstration")
    print("#"*60)
    
    # 1. Preprocessing
    X, y, preprocessor = demonstrate_preprocessing()
    
    # 2. Supervised Models
    supervised_models, sup_evaluator = demonstrate_supervised_models(X, y)
    
    # 3. Unsupervised Models
    unsupervised_models, unsup_evaluator = demonstrate_unsupervised_models(X, y)
    
    # 4. Visualization
    try:
        demonstrate_visualization(X, y, supervised_models, sup_evaluator)
    except Exception as e:
        print(f"Visualization skipped: {str(e)}")
    
    print("\n" + "#"*60)
    print("# Demonstration Complete!")
    print("#"*60)
    print("\nTo use with real data:")
    print("1. Download NSL-KDD or CICIDS dataset")
    print("2. Place in data/raw/ directory")
    print("3. Run: python -m anomaly_detection.main --mode train")
    print("4. Run: python -m anomaly_detection.main --mode dashboard")


if __name__ == '__main__':
    main()
