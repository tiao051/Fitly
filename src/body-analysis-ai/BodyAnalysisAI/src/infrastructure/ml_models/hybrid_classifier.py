"""
Infrastructure - Hybrid Classifier Implementation
SVM-based hybrid feature classification for body type prediction
"""

import numpy as np
import joblib
import logging
from typing import Optional, Tuple, Dict
import os

from ...domain.entities import HybridFeatures, BodyType, BodyRatios, ModelLoadError
from ...domain.interfaces import IHybridClassifier

logger = logging.getLogger(__name__)


class SVMHybridClassifier(IHybridClassifier):
    """SVM-based hybrid feature classifier implementation"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load trained SVM model and scaler"""
        if self.model_path and os.path.exists(self.model_path):
            try:
                logger.info(f"Loading SVM model from: {self.model_path}")
                model_data = joblib.load(self.model_path)
                self.model = model_data['classifier']
                self.scaler = model_data['scaler']
                self.is_trained = True
                logger.info("SVM model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load SVM model: {str(e)}")
                self._create_dummy_model()
        else:
            logger.info("No model path provided, creating dummy model for development")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create dummy model for development/testing"""
        try:
            from sklearn.svm import SVC
            from sklearn.preprocessing import StandardScaler
            
            self.model = SVC(probability=True, random_state=42)
            self.scaler = StandardScaler()
            self.is_trained = False
            logger.info("Dummy SVM model created for development")
        except ImportError:
            logger.error("Scikit-learn not available, SVM classifier disabled")
            self.model = None
            self.scaler = None
    
    def create_hybrid_features(
        self, 
        dl_features: np.ndarray, 
        traditional_features: dict
    ) -> HybridFeatures:
        """Combine deep learning and traditional features"""
        try:
            # Extract body ratios from traditional features
            body_ratios = BodyRatios(
                shoulder_to_hip_ratio=traditional_features.get('shoulder_to_hip_ratio', 1.0),
                waist_to_hip_ratio=traditional_features.get('waist_to_hip_ratio', 0.8),
                shoulder_to_waist_ratio=traditional_features.get('shoulder_to_waist_ratio', 1.25),
                torso_aspect_ratio=traditional_features.get('torso_aspect_ratio', 1.0)
            )
            
            return HybridFeatures(
                dl_features=dl_features,
                body_ratios=body_ratios
            )
            
        except Exception as e:
            logger.error(f"Failed to create hybrid features: {str(e)}")
            raise ValueError(f"Invalid feature combination: {str(e)}")
    
    def classify_body_type(self, features: HybridFeatures) -> BodyType:
        """Classify body type from hybrid features"""
        try:
            if not self.is_trained or self.model is None:
                # Use rule-based classification as fallback
                return self._rule_based_classify(features.body_ratios)
            
            # Prepare feature vector
            feature_vector = features.to_combined_vector().reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_vector)
            
            # Predict body type
            prediction = self.model.predict(scaled_features)[0]
            
            # Convert numeric prediction to BodyType enum
            body_type = self._convert_prediction_to_body_type(prediction)
            
            logger.debug(f"SVM classified body type: {body_type}")
            return body_type
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}, falling back to rule-based")
            return self._rule_based_classify(features.body_ratios)
    
    def get_classification_confidence(self, features: HybridFeatures) -> float:
        """Get confidence score for classification"""
        try:
            if not self.is_trained or self.model is None:
                return 0.75  # Default confidence for rule-based classification
            
            # Prepare feature vector
            feature_vector = features.to_combined_vector().reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_vector)
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(scaled_features)[0]
            confidence = float(max(probabilities))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.5  # Low confidence on error
    
    def _rule_based_classify(self, ratios: BodyRatios) -> BodyType:
        """Rule-based body type classification using traditional ratios"""
        shoulder_hip = ratios.shoulder_to_hip_ratio
        waist_hip = ratios.waist_to_hip_ratio
        shoulder_waist = ratios.shoulder_to_waist_ratio
        
        # Classification rules based on body proportion research
        if shoulder_hip > 1.1 and waist_hip < 0.8:
            # Broad shoulders, narrow waist and hips
            return BodyType.INVERTED_TRIANGLE
        elif shoulder_hip < 0.9 and waist_hip < 0.8:
            # Narrow shoulders, wider hips
            return BodyType.PEAR
        elif waist_hip > 0.85:
            # Wider waist relative to hips
            return BodyType.APPLE
        elif 0.9 <= shoulder_hip <= 1.1 and waist_hip < 0.75:
            # Balanced shoulders and hips, narrow waist
            return BodyType.HOURGLASS
        else:
            # Similar measurements throughout
            return BodyType.RECTANGLE
    
    def _convert_prediction_to_body_type(self, prediction) -> BodyType:
        """Convert numeric prediction to BodyType enum"""
        # Mapping depends on how the model was trained
        # This is a placeholder - should match training labels
        type_mapping = {
            0: BodyType.APPLE,
            1: BodyType.HOURGLASS,
            2: BodyType.INVERTED_TRIANGLE,
            3: BodyType.PEAR,
            4: BodyType.RECTANGLE
        }
        
        if isinstance(prediction, (int, np.integer)):
            return type_mapping.get(prediction, BodyType.RECTANGLE)
        elif isinstance(prediction, str):
            try:
                return BodyType(prediction.upper())
            except ValueError:
                return BodyType.RECTANGLE
        else:
            return BodyType.RECTANGLE
    
    def is_model_loaded(self) -> bool:
        """Check if the classification model is loaded"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the classification model"""
        return {
            'model_type': 'SVM',
            'is_trained': self.is_trained,
            'is_loaded': self.is_model_loaded(),
            'model_path': self.model_path,
            'fallback_method': 'rule_based_classification'
        }
    
    def save_model(self, save_path: str, model_metadata: Optional[Dict] = None):
        """Save trained model to disk"""
        if self.model is None or self.scaler is None:
            raise ModelLoadError("No model to save")
        
        try:
            model_data = {
                'classifier': self.model,
                'scaler': self.scaler,
                'metadata': model_metadata or {}
            }
            joblib.dump(model_data, save_path)
            logger.info(f"Model saved to: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise ModelLoadError(f"Model saving failed: {str(e)}")
