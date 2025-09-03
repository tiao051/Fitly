"""
Infrastructure - File-Based Analysis Repository
Persistent file storage implementation for analysis results
"""

import json
import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from ...domain.entities import BodyAnalysisResult, BodyType, PoseKeypoints, BodyRatios, HybridFeatures
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class FileBasedAnalysisRepository(IAnalysisRepository):
    """File-based repository implementation for persistent storage"""
    
    def __init__(self, data_directory: str = "./data"):
        self.data_directory = data_directory
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create data directory structure if it doesn't exist"""
        directories = [
            self.data_directory,
            f"{self.data_directory}/analyses",
            f"{self.data_directory}/users",
            f"{self.data_directory}/metadata"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"Data directory structure ensured: {self.data_directory}")
    
    async def save_analysis(self, result: BodyAnalysisResult) -> str:
        """Save analysis result to file and return unique identifier"""
        analysis_id = str(uuid.uuid4())
        
        # Add metadata
        result.processing_metadata["analysis_id"] = analysis_id
        result.processing_metadata["created_at"] = datetime.utcnow().isoformat()
        result.processing_metadata["updated_at"] = datetime.utcnow().isoformat()
        result.processing_metadata["storage_type"] = "file_based"
        
        try:
            # Serialize and save analysis result
            result_data = self._serialize_result(result)
            result_file = f"{self.data_directory}/analyses/{analysis_id}.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # Update user history if user_id is available
            user_id = result.processing_metadata.get("user_id")
            if user_id:
                await self._update_user_history(user_id, analysis_id)
            
            logger.info(f"Saved analysis {analysis_id} to file storage")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Failed to save analysis to file: {str(e)}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[BodyAnalysisResult]:
        """Retrieve analysis result from file"""
        result_file = f"{self.data_directory}/analyses/{analysis_id}.json"
        
        try:
            if not os.path.exists(result_file):
                logger.warning(f"Analysis file not found: {analysis_id}")
                return None
            
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            result = self._deserialize_result(result_data)
            logger.debug(f"Retrieved analysis {analysis_id} from file storage")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load analysis {analysis_id}: {str(e)}")
            return None
    
    async def get_user_analyses(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[BodyAnalysisResult]:
        """Get analysis history for a user"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            if not os.path.exists(user_file):
                logger.info(f"No history file found for user {user_id}")
                return []
            
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            analysis_ids = user_data.get("analysis_ids", [])
            
            # Apply pagination (most recent first)
            total_count = len(analysis_ids)
            start_idx = max(0, total_count - offset - limit)
            end_idx = total_count - offset
            paginated_ids = analysis_ids[start_idx:end_idx]
            paginated_ids.reverse()  # Most recent first
            
            # Load analysis results
            results = []
            for analysis_id in paginated_ids:
                analysis = await self.get_analysis(analysis_id)
                if analysis:
                    results.append(analysis)
            
            logger.debug(f"Retrieved {len(results)} analyses for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to load user history for {user_id}: {str(e)}")
            return []
    
    async def get_analyses_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[BodyAnalysisResult]:
        """Get analyses within a date range"""
        # Get all user analyses (with a reasonable limit)
        all_analyses = await self.get_user_analyses(user_id, limit=1000)
        
        filtered_analyses = []
        for analysis in all_analyses:
            created_at_str = analysis.processing_metadata.get("created_at")
            if created_at_str:
                try:
                    # Handle both ISO format with and without timezone
                    if created_at_str.endswith('Z'):
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    else:
                        created_at = datetime.fromisoformat(created_at_str)
                    
                    if start_date <= created_at <= end_date:
                        filtered_analyses.append(analysis)
                except ValueError as e:
                    logger.warning(f"Invalid date format in analysis metadata: {created_at_str}, error: {e}")
        
        logger.debug(f"Retrieved {len(filtered_analyses)} analyses for user {user_id} in date range")
        return filtered_analyses
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis result"""
        result_file = f"{self.data_directory}/analyses/{analysis_id}.json"
        
        try:
            # Get analysis to find user_id for cleanup
            analysis = await self.get_analysis(analysis_id)
            if not analysis:
                logger.warning(f"Analysis {analysis_id} not found for deletion")
                return False
            
            # Remove analysis file
            if os.path.exists(result_file):
                os.remove(result_file)
            
            # Remove from user history
            user_id = analysis.processing_metadata.get("user_id")
            if user_id:
                await self._remove_from_user_history(user_id, analysis_id)
            
            logger.info(f"Deleted analysis {analysis_id} from file storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {str(e)}")
            return False
    
    async def get_analysis_count(self, user_id: str) -> int:
        """Get total number of analyses for a user"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            if not os.path.exists(user_file):
                return 0
            
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            count = len(user_data.get("analysis_ids", []))
            logger.debug(f"User {user_id} has {count} analyses")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get analysis count for user {user_id}: {str(e)}")
            return 0
    
    async def _update_user_history(self, user_id: str, analysis_id: str):
        """Update user's analysis history"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            # Load existing data or create new
            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
            else:
                user_data = {
                    "user_id": user_id,
                    "analysis_ids": [],
                    "created_at": datetime.utcnow().isoformat()
                }
            
            # Add new analysis
            if analysis_id not in user_data["analysis_ids"]:
                user_data["analysis_ids"].append(analysis_id)
                user_data["last_updated"] = datetime.utcnow().isoformat()
                user_data["total_analyses"] = len(user_data["analysis_ids"])
            
            # Save updated data
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to update user history for {user_id}: {str(e)}")
    
    async def _remove_from_user_history(self, user_id: str, analysis_id: str):
        """Remove analysis from user's history"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            if not os.path.exists(user_file):
                return
            
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Remove analysis ID
            if analysis_id in user_data.get("analysis_ids", []):
                user_data["analysis_ids"].remove(analysis_id)
                user_data["last_updated"] = datetime.utcnow().isoformat()
                user_data["total_analyses"] = len(user_data["analysis_ids"])
                
                # Save updated data
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Failed to remove analysis from user history: {str(e)}")
    
    def _serialize_result(self, result: BodyAnalysisResult) -> Dict[str, Any]:
        """Convert BodyAnalysisResult to JSON-serializable format"""
        return {
            "body_type": result.body_type.value,
            "confidence_score": result.confidence_score,
            "pose_keypoints": {
                "keypoints": result.pose_keypoints.keypoints,
                "image_dimensions": result.pose_keypoints.image_dimensions,
                "detection_confidence": result.pose_keypoints.detection_confidence
            },
            "body_ratios": {
                "shoulder_to_hip_ratio": result.body_ratios.shoulder_to_hip_ratio,
                "waist_to_hip_ratio": result.body_ratios.waist_to_hip_ratio,
                "shoulder_to_waist_ratio": result.body_ratios.shoulder_to_waist_ratio,
                "torso_aspect_ratio": result.body_ratios.torso_aspect_ratio
            },
            "hybrid_features": self._serialize_hybrid_features(result.hybrid_features) if result.hybrid_features else None,
            "processing_metadata": result.processing_metadata,
            "serialization_version": "1.0"
        }
    
    def _serialize_hybrid_features(self, features: HybridFeatures) -> Dict[str, Any]:
        """Serialize hybrid features (excluding large DL features to save space)"""
        return {
            "has_dl_features": features.dl_features is not None,
            "dl_feature_dimension": len(features.dl_features) if features.dl_features is not None else 0,
            "body_ratios": {
                "shoulder_to_hip_ratio": features.body_ratios.shoulder_to_hip_ratio,
                "waist_to_hip_ratio": features.body_ratios.waist_to_hip_ratio,
                "shoulder_to_waist_ratio": features.body_ratios.shoulder_to_waist_ratio,
                "torso_aspect_ratio": features.body_ratios.torso_aspect_ratio
            }
        }
    
    def _deserialize_result(self, data: Dict[str, Any]) -> BodyAnalysisResult:
        """Convert JSON data back to BodyAnalysisResult"""
        import numpy as np
        
        # Reconstruct pose keypoints
        pose_data = data["pose_keypoints"]
        pose_keypoints = PoseKeypoints(
            keypoints=pose_data["keypoints"],
            image_dimensions=tuple(pose_data["image_dimensions"]),
            detection_confidence=pose_data["detection_confidence"]
        )
        
        # Reconstruct body ratios
        ratio_data = data["body_ratios"]
        body_ratios = BodyRatios(
            shoulder_to_hip_ratio=ratio_data["shoulder_to_hip_ratio"],
            waist_to_hip_ratio=ratio_data["waist_to_hip_ratio"],
            shoulder_to_waist_ratio=ratio_data["shoulder_to_waist_ratio"],
            torso_aspect_ratio=ratio_data["torso_aspect_ratio"]
        )
        
        # Reconstruct hybrid features (placeholder for DL features)
        hybrid_features = None
        if data.get("hybrid_features"):
            hf_data = data["hybrid_features"]
            dl_features = None
            if hf_data.get("has_dl_features"):
                # Create placeholder DL features (not stored to save space)
                dl_features = np.zeros(hf_data.get("dl_feature_dimension", 512))
            
            hybrid_features = HybridFeatures(
                dl_features=dl_features,
                body_ratios=body_ratios
            )
        
        return BodyAnalysisResult(
            body_type=BodyType(data["body_type"]),
            confidence_score=data["confidence_score"],
            pose_keypoints=pose_keypoints,
            body_ratios=body_ratios,
            hybrid_features=hybrid_features,
            processing_metadata=data["processing_metadata"]
        )
