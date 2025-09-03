"""
Infrastructure Layer - Data Repositories
Implements data persistence interfaces
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from ...domain.entities import BodyAnalysisResult, BodyType
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class InMemoryAnalysisRepository(IAnalysisRepository):
    """In-memory repository for development and testing"""
    
    def __init__(self):
        self.results: Dict[str, BodyAnalysisResult] = {}
        self.user_results: Dict[str, List[str]] = {}  # user_id -> list of result_ids
    
    async def save_result(self, result: BodyAnalysisResult, user_id: Optional[str] = None) -> str:
        """Save analysis result and return result ID"""
        result_id = str(uuid.uuid4())
        
        # Add timestamp to metadata
        result.processing_metadata["created_at"] = datetime.utcnow().isoformat()
        result.processing_metadata["result_id"] = result_id
        
        # Store result
        self.results[result_id] = result
        
        # Track user results
        if user_id:
            if user_id not in self.user_results:
                self.user_results[user_id] = []
            self.user_results[user_id].append(result_id)
        
        return result_id
    
    async def get_result(self, result_id: str) -> Optional[BodyAnalysisResult]:
        """Retrieve analysis result by ID"""
        return self.results.get(result_id)
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[BodyAnalysisResult]:
        """Get user's analysis history"""
        result_ids = self.user_results.get(user_id, [])
        
        # Get most recent results
        recent_ids = result_ids[-limit:] if len(result_ids) > limit else result_ids
        
        # Retrieve results
        results = []
        for result_id in recent_ids:
            result = self.results.get(result_id)
            if result:
                results.append(result)
        
        return results


class FileBasedAnalysisRepository(IAnalysisRepository):
    """File-based repository for persistent storage"""
    
    def __init__(self, data_directory: str = "./data"):
        self.data_directory = data_directory
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create data directory if it doesn't exist"""
        import os
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(f"{self.data_directory}/results", exist_ok=True)
        os.makedirs(f"{self.data_directory}/users", exist_ok=True)
    
    async def save_result(self, result: BodyAnalysisResult, user_id: Optional[str] = None) -> str:
        """Save analysis result to file"""
        result_id = str(uuid.uuid4())
        
        # Add metadata
        result.processing_metadata["created_at"] = datetime.utcnow().isoformat()
        result.processing_metadata["result_id"] = result_id
        
        # Convert result to serializable format
        result_data = self._serialize_result(result)
        
        # Save result file
        result_file = f"{self.data_directory}/results/{result_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Update user history
        if user_id:
            await self._update_user_history(user_id, result_id)
        
        logger.info(f"Saved analysis result {result_id} to file")
        return result_id
    
    async def get_result(self, result_id: str) -> Optional[BodyAnalysisResult]:
        """Retrieve analysis result from file"""
        result_file = f"{self.data_directory}/results/{result_id}.json"
        
        try:
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            return self._deserialize_result(result_data)
        except FileNotFoundError:
            logger.warning(f"Result file not found: {result_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to load result {result_id}: {str(e)}")
            return None
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[BodyAnalysisResult]:
        """Get user's analysis history from files"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            with open(user_file, 'r') as f:
                user_data = json.load(f)
            
            result_ids = user_data.get("result_ids", [])
            recent_ids = result_ids[-limit:] if len(result_ids) > limit else result_ids
            
            # Load results
            results = []
            for result_id in recent_ids:
                result = await self.get_result(result_id)
                if result:
                    results.append(result)
            
            return results
            
        except FileNotFoundError:
            logger.info(f"No history found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Failed to load history for user {user_id}: {str(e)}")
            return []
    
    async def _update_user_history(self, user_id: str, result_id: str):
        """Update user's result history"""
        user_file = f"{self.data_directory}/users/{user_id}.json"
        
        try:
            # Load existing data
            try:
                with open(user_file, 'r') as f:
                    user_data = json.load(f)
            except FileNotFoundError:
                user_data = {"user_id": user_id, "result_ids": []}
            
            # Add new result
            user_data["result_ids"].append(result_id)
            user_data["last_updated"] = datetime.utcnow().isoformat()
            
            # Save updated data
            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update user history for {user_id}: {str(e)}")
    
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
            "dl_embeddings": {
                "model_name": result.dl_embeddings.model_name if result.dl_embeddings else None,
                "embedding_dimension": result.dl_embeddings.embedding_dimension if result.dl_embeddings else None,
                # Note: Not serializing actual embeddings to save space
            } if result.dl_embeddings else None,
            "processing_metadata": result.processing_metadata
        }
    
    def _deserialize_result(self, data: Dict[str, Any]) -> BodyAnalysisResult:
        """Convert JSON data back to BodyAnalysisResult"""
        from ...domain.entities import PoseKeypoints, BodyRatios, DLEmbeddings
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
        
        # Reconstruct DL embeddings (placeholder since we didn't save actual embeddings)
        dl_embeddings = None
        if data.get("dl_embeddings"):
            dl_data = data["dl_embeddings"]
            if dl_data["model_name"]:
                dl_embeddings = DLEmbeddings(
                    embeddings=np.zeros(dl_data["embedding_dimension"]),  # Placeholder
                    model_name=dl_data["model_name"],
                    embedding_dimension=dl_data["embedding_dimension"]
                )
        
        return BodyAnalysisResult(
            body_type=BodyType(data["body_type"]),
            confidence_score=data["confidence_score"],
            pose_keypoints=pose_keypoints,
            body_ratios=body_ratios,
            dl_embeddings=dl_embeddings,
            processing_metadata=data["processing_metadata"]
        )
