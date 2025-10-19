from __future__ import annotations


from zoneinfo import ZoneInfo
from datetime import datetime

from base import BaseModel
from base import BaseService

from storage import MinioSetting
from storage import MinioService
from storage import MinioServiceInput

import io
from io import BytesIO

from logger import get_logger

logger = get_logger(__name__)

class MinioUploaderInput(BaseModel):
    file_path: str
    file: BytesIO
    metadata: dict | None = None
    
class MinioUploaderOutput(BaseModel):
    object_name: str | None = None
    size: int | None = None
    url: str | None = None

class MinioUploaderService(BaseService):
    
    minio: MinioService
    minio_settings: MinioSetting
    
    def process(self, inputs: MinioUploaderInput) -> MinioUploaderOutput:
        
        try:
            self.minio.create_bucket(
                bucket_name=self.minio_settings.bucket
            )


        except Exception as e:
            logger.exception('Error while creating bucket', extra={'bucket_name': self.minio_settings.bucket})
            raise e
        
        try:
            data = inputs.file.read()
        except Exception as e:
            
            logger.exception('Error while reading file data', extra={'file_path': inputs.file_path})
            raise e

        content_type = getattr(inputs.file, "content_type", None) or "application/octet-stream"
        
        timestamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d-%H-%M-%S")
        object_name = f"{timestamp}/upload/{inputs.file_path}"
                
        logger.info('Starting upload to MinIO', extra={'file_path': inputs.file_path})

        self.minio.upload_file(
            input=MinioServiceInput(
                bucket_name=self.minio_settings.bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                content_type=content_type,
                metadata=inputs.metadata,
            )
        )
        
        logger.info('Successfully uploaded file to MinIO', extra={'file_path': object_name})

        return MinioUploaderOutput(
            object_name=object_name,
            size=len(data) if data is not None else None,
            url=None,
        )