from __future__ import annotations

import os
from dotenv import load_dotenv
from storage import MinioSetting
from storage import MinioService
from storage import MinioServiceInput
from io import BytesIO

load_dotenv()
MINIO__BUCKET = "test-bucket"
MINIO__ENDPOINT = os.getenv("MINIO__ENDPOINT", "localhost:17000")
MINIO__ACCESS_KEY = os.getenv("MINIO__ACCESS_KEY")
MINIO__SECRET_KEY = os.getenv("MINIO__SECRET_KEY")

class TestMinioService:
    
    def __init__(self):
        minio_setting = MinioSetting(
            endpoint=MINIO__ENDPOINT,
            access_key=MINIO__ACCESS_KEY,
            secret_key=MINIO__SECRET_KEY,
            bucket='test-bucket',
            secure=False
        )
        self.minio_service = MinioService(settings=minio_setting)
        
    def test_create_bucket(self):
        bucket_name = "test-bucket"
        self.minio_service.create_bucket(bucket_name=bucket_name)
        assert self.minio_service.bucket_exists(bucket_name)
        
    def test_upload_file(self):
        file_path = "test_file.txt"
        object_name = "test_file.txt"
        self.minio_service.upload_file(MinioServiceInput(
            
            bucket_name=MINIO__BUCKET,
            object_name=file_path,
            file_path=file_path,
            content_type='text/plain',
        ))
        
    def test_download_file(self):
        object_name = "test_file.txt"
        download_path = "downloaded_sample.txt"
        self.minio_service.download_file(
            MinioServiceInput(
                bucket_name=MINIO__BUCKET,
                object_name=object_name,
                file_path=download_path,
            )
        )
        assert os.path.exists(download_path)
        os.remove(download_path)
        
    def test_delete_file(self):
        test_data = BytesIO(b'Test data content')
        self.minio_service.delete_file(
            input=MinioServiceInput(
                bucket_name='test-bucket',
                object_name='data-object.txt',
                data=test_data,
                content_type='text/plain',
                metadata={'source': 'memory'},
            )
        )
if __name__ == "__main__":
        
    test_minio_service = TestMinioService()

    test_minio_service.test_create_bucket()
    test_minio_service.test_upload_file()
    test_minio_service.test_download_file()
    test_minio_service.test_delete_file()
    
