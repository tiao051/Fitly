"""
Domain Entity - Deep Learning Features
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .body_ratios import BodyRatios


@dataclass
class DLEmbeddings:
    """Deep learning embeddings from pretrained backbone"""
    embeddings: np.ndarray
    model_name: str
    embedding_dimension: int
    
    def get_features(self) -> np.ndarray:
        """Get embedding features as numpy array"""
        return self.embeddings
    
    def validate_embeddings(self) -> bool:
        """Validate embedding dimensions and values"""
        if self.embeddings.shape[0] != self.embedding_dimension:
            return False
        
        # Check for NaN or infinite values
        if np.any(np.isnan(self.embeddings)) or np.any(np.isinf(self.embeddings)):
            return False
            
        return True
    
    def normalize_embeddings(self) -> np.ndarray:
        """Normalize embeddings to unit vector"""
        norm = np.linalg.norm(self.embeddings)
        if norm == 0:
            return self.embeddings
        return self.embeddings / norm


@dataclass
class HybridFeatures:
    """Combined features from DL embeddings and pose ratios"""
    dl_embeddings: DLEmbeddings
    body_ratios: 'BodyRatios'  # Forward reference
    
    def to_combined_vector(self) -> np.ndarray:
        """Combine both feature types into single vector"""
        dl_features = self.dl_embeddings.get_features()
        ratio_features = self.body_ratios.to_feature_vector()
        return np.concatenate([dl_features, ratio_features])
    
    def validate_features(self) -> bool:
        """Validate both feature components"""
        return (self.dl_embeddings.validate_embeddings() and 
                self.body_ratios.validate_ratios())
