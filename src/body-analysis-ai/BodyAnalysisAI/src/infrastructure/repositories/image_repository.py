"""
Infrastructure - Image Repository Implementation
File-based image storage with metadata support
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict
import logging

from ...domain.interfaces import IImageRepository

logger = logging.getLogger(__name__)


class FileBasedImageRepository(IImageRepository):
    """File-based image storage implementation"""
    
    def __init__(self, storage_directory: str = "./images"):
        self.storage_directory = storage_directory
        self.metadata_directory = f"{storage_directory}/metadata"
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """Create storage directory structure"""
        directories = [
            self.storage_directory,
            self.metadata_directory,
            f"{self.storage_directory}/raw",
            f"{self.storage_directory}/processed"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"Image storage directories ensured: {self.storage_directory}")
    
    async def save_image(
        self, 
        image_data: bytes, 
        content_type: str,
        user_id: str
    ) -> str:
        """Save image to storage and return unique identifier"""
        image_id = str(uuid.uuid4())
        
        try:
            # Determine file extension from content type
            file_extension = self._get_file_extension(content_type)
            
            # Save raw image data
            image_path = f"{self.storage_directory}/raw/{image_id}{file_extension}"
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # Save metadata
            metadata = {
                "image_id": image_id,
                "user_id": user_id,
                "content_type": content_type,
                "file_extension": file_extension,
                "file_size": len(image_data),
                "storage_path": image_path,
                "created_at": datetime.utcnow().isoformat(),
                "storage_type": "file_based"
            }
            
            metadata_path = f"{self.metadata_directory}/{image_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved image {image_id} for user {user_id}")
            return image_id
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise
    
    async def get_image(self, image_id: str) -> Optional[bytes]:
        """Retrieve image data by ID"""
        try:
            # Get metadata to find storage path
            metadata = await self.get_image_metadata(image_id)
            if not metadata:
                logger.warning(f"Image metadata not found: {image_id}")
                return None
            
            storage_path = metadata.get("storage_path")
            if not storage_path or not os.path.exists(storage_path):
                logger.warning(f"Image file not found: {storage_path}")
                return None
            
            # Read image data
            with open(storage_path, 'rb') as f:
                image_data = f.read()
            
            logger.debug(f"Retrieved image {image_id}")
            return image_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve image {image_id}: {str(e)}")
            return None
    
    async def delete_image(self, image_id: str) -> bool:
        """Delete an image from storage"""
        try:
            # Get metadata to find all associated files
            metadata = await self.get_image_metadata(image_id)
            if not metadata:
                logger.warning(f"Image metadata not found for deletion: {image_id}")
                return False
            
            # Delete image file
            storage_path = metadata.get("storage_path")
            if storage_path and os.path.exists(storage_path):
                os.remove(storage_path)
                logger.debug(f"Deleted image file: {storage_path}")
            
            # Delete processed version if exists
            file_extension = metadata.get("file_extension", "")
            processed_path = f"{self.storage_directory}/processed/{image_id}{file_extension}"
            if os.path.exists(processed_path):
                os.remove(processed_path)
                logger.debug(f"Deleted processed image: {processed_path}")
            
            # Delete metadata
            metadata_path = f"{self.metadata_directory}/{image_id}.json"
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                logger.debug(f"Deleted metadata: {metadata_path}")
            
            logger.info(f"Successfully deleted image {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete image {image_id}: {str(e)}")
            return False
    
    async def get_image_metadata(self, image_id: str) -> Optional[Dict]:
        """Get metadata for an image"""
        metadata_path = f"{self.metadata_directory}/{image_id}.json"
        
        try:
            if not os.path.exists(metadata_path):
                return None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load image metadata {image_id}: {str(e)}")
            return None
    
    def _get_file_extension(self, content_type: str) -> str:
        """Get file extension from content type"""
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp'
        }
        
        return content_type_map.get(content_type.lower(), '.jpg')
    
    async def save_processed_image(
        self, 
        image_id: str, 
        processed_data: bytes
    ) -> bool:
        """Save processed version of an image"""
        try:
            # Get original metadata
            metadata = await self.get_image_metadata(image_id)
            if not metadata:
                logger.warning(f"Cannot save processed image: metadata not found for {image_id}")
                return False
            
            # Save processed image
            file_extension = metadata.get("file_extension", ".jpg")
            processed_path = f"{self.storage_directory}/processed/{image_id}{file_extension}"
            
            with open(processed_path, 'wb') as f:
                f.write(processed_data)
            
            # Update metadata
            metadata["processed_path"] = processed_path
            metadata["processed_size"] = len(processed_data)
            metadata["processed_at"] = datetime.utcnow().isoformat()
            
            metadata_path = f"{self.metadata_directory}/{image_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved processed image {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save processed image {image_id}: {str(e)}")
            return False
    
    async def get_processed_image(self, image_id: str) -> Optional[bytes]:
        """Get processed version of an image"""
        try:
            metadata = await self.get_image_metadata(image_id)
            if not metadata:
                return None
            
            processed_path = metadata.get("processed_path")
            if not processed_path or not os.path.exists(processed_path):
                return None
            
            with open(processed_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to get processed image {image_id}: {str(e)}")
            return None
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            raw_dir = f"{self.storage_directory}/raw"
            processed_dir = f"{self.storage_directory}/processed"
            metadata_dir = self.metadata_directory
            
            raw_count = len([f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]) if os.path.exists(raw_dir) else 0
            processed_count = len([f for f in os.listdir(processed_dir) if os.path.isfile(os.path.join(processed_dir, f))]) if os.path.exists(processed_dir) else 0
            metadata_count = len([f for f in os.listdir(metadata_dir) if f.endswith('.json')]) if os.path.exists(metadata_dir) else 0
            
            return {
                'total_images': metadata_count,
                'raw_images': raw_count,
                'processed_images': processed_count,
                'storage_directory': self.storage_directory,
                'storage_type': 'file_based'
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {'error': str(e)}
