"""
Feature engineering module for creating and selecting features.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_selection import (
    SelectKBest, f_classif, mutual_info_classif, RFE
)
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple, Optional, List


class FeatureEngineer:
    """Feature engineering for network anomaly detection."""
    
    def __init__(self, n_features: int = 20):
        """
        Initialize feature engineer.
        
        Args:
            n_features: Number of features to select
        """
        self.n_features = n_features
        self.selector = None
        self.pca = None
        self.selected_features = None
        self.feature_importance = None
    
    def create_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create statistical features from existing features.
        
        Args:
            data: Input dataframe
            
        Returns:
            Dataframe with additional statistical features
        """
        data_enriched = data.copy()
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        # Create aggregated features
        if len(numeric_cols) > 0:
            data_enriched['mean_value'] = data[numeric_cols].mean(axis=1)
            data_enriched['std_value'] = data[numeric_cols].std(axis=1)
            data_enriched['max_value'] = data[numeric_cols].max(axis=1)
            data_enriched['min_value'] = data[numeric_cols].min(axis=1)
            data_enriched['median_value'] = data[numeric_cols].median(axis=1)
        
        return data_enriched
    
    def create_ratio_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create ratio-based features.
        
        Args:
            data: Input dataframe
            
        Returns:
            Dataframe with ratio features
        """
        data_enriched = data.copy()
        
        # Example ratio features for network traffic
        if 'src_bytes' in data.columns and 'dst_bytes' in data.columns:
            data_enriched['byte_ratio'] = np.where(
                data['dst_bytes'] != 0,
                data['src_bytes'] / (data['dst_bytes'] + 1e-10),
                0
            )
        
        if 'count' in data.columns and 'srv_count' in data.columns:
            data_enriched['srv_count_ratio'] = np.where(
                data['count'] != 0,
                data['srv_count'] / (data['count'] + 1e-10),
                0
            )
        
        return data_enriched
    
    def select_features_kbest(
        self,
        X: np.ndarray,
        y: np.ndarray,
        score_func=f_classif
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select top K features using univariate statistical tests.
        
        Args:
            X: Feature array
            y: Target array
            score_func: Scoring function
            
        Returns:
            Tuple of (selected features, feature scores)
        """
        self.selector = SelectKBest(score_func=score_func, k=self.n_features)
        X_selected = self.selector.fit_transform(X, y)
        
        feature_scores = self.selector.scores_
        selected_indices = self.selector.get_support(indices=True)
        self.selected_features = selected_indices
        
        return X_selected, feature_scores
    
    def select_features_mutual_info(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select features using mutual information.
        
        Args:
            X: Feature array
            y: Target array
            
        Returns:
            Tuple of (selected features, feature scores)
        """
        return self.select_features_kbest(X, y, score_func=mutual_info_classif)
    
    def select_features_rfe(
        self,
        X: np.ndarray,
        y: np.ndarray,
        estimator=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select features using Recursive Feature Elimination.
        
        Args:
            X: Feature array
            y: Target array
            estimator: Estimator for RFE (default: RandomForest)
            
        Returns:
            Tuple of (selected features, feature ranking)
        """
        if estimator is None:
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
        
        self.selector = RFE(estimator=estimator, n_features_to_select=self.n_features)
        X_selected = self.selector.fit_transform(X, y)
        
        feature_ranking = self.selector.ranking_
        selected_indices = self.selector.get_support(indices=True)
        self.selected_features = selected_indices
        
        return X_selected, feature_ranking
    
    def get_feature_importance(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate feature importance using Random Forest.
        
        Args:
            X: Feature array
            y: Target array
            feature_names: List of feature names
            
        Returns:
            Dataframe with feature importance scores
        """
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        importance_scores = rf.feature_importances_
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance_scores
        }).sort_values('importance', ascending=False)
        
        self.feature_importance = importance_df
        return importance_df
    
    def apply_pca(
        self,
        X: np.ndarray,
        n_components: Optional[int] = None,
        variance_threshold: float = 0.95
    ) -> Tuple[np.ndarray, float]:
        """
        Apply Principal Component Analysis for dimensionality reduction.
        
        Args:
            X: Feature array
            n_components: Number of components (if None, use variance_threshold)
            variance_threshold: Cumulative variance threshold
            
        Returns:
            Tuple of (transformed features, explained variance ratio)
        """
        if n_components is None:
            self.pca = PCA(n_components=variance_threshold, svd_solver='full')
        else:
            self.pca = PCA(n_components=n_components)
        
        X_pca = self.pca.fit_transform(X)
        explained_variance = np.sum(self.pca.explained_variance_ratio_)
        
        print(f"PCA: {X_pca.shape[1]} components explain {explained_variance:.2%} variance")
        
        return X_pca, explained_variance
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform new data using fitted feature selector.
        
        Args:
            X: Feature array
            
        Returns:
            Transformed feature array
        """
        if self.selector is not None:
            return self.selector.transform(X)
        elif self.pca is not None:
            return self.pca.transform(X)
        else:
            return X
    
    def create_interaction_features(
        self,
        data: pd.DataFrame,
        feature_pairs: List[Tuple[str, str]]
    ) -> pd.DataFrame:
        """
        Create interaction features from feature pairs.
        
        Args:
            data: Input dataframe
            feature_pairs: List of feature pairs for interaction
            
        Returns:
            Dataframe with interaction features
        """
        data_enriched = data.copy()
        
        for feat1, feat2 in feature_pairs:
            if feat1 in data.columns and feat2 in data.columns:
                # Multiplication interaction
                data_enriched[f'{feat1}_x_{feat2}'] = data[feat1] * data[feat2]
                
                # Division interaction (with small epsilon to avoid division by zero)
                data_enriched[f'{feat1}_div_{feat2}'] = data[feat1] / (data[feat2] + 1e-10)
        
        return data_enriched
    
    def create_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features if timestamp is available.
        
        Args:
            data: Input dataframe
            
        Returns:
            Dataframe with temporal features
        """
        data_enriched = data.copy()
        
        if 'timestamp' in data.columns:
            data_enriched['timestamp'] = pd.to_datetime(data['timestamp'])
            data_enriched['hour'] = data_enriched['timestamp'].dt.hour
            data_enriched['day_of_week'] = data_enriched['timestamp'].dt.dayofweek
            data_enriched['is_weekend'] = data_enriched['day_of_week'].isin([5, 6]).astype(int)
        
        return data_enriched