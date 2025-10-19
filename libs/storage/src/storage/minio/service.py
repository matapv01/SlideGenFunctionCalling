from __future__ import annotations

from minio import Minio
from typing import Optional
from io import BytesIO

from .settings import MinioSetting
from ..base import StorageBase
from ..base import StorageBaseInput
from ..base import StorageBaseOutput
    
class MinioServiceInput(StorageBaseInput):
    file_path: Optional[str] = None
    data: Optional[BytesIO] = None
    content_type: Optional[str] = None
    metadata: Optional[dict] = None

class MinioServiceOutput(StorageBaseOutput):
    pass

class MinioService(StorageBase):
    settings: MinioSetting
    
    @property
    def _client(self) -> Minio:
        return Minio(
            endpoint=self.settings.endpoint,
            access_key=self.settings.access_key,
            secret_key=self.settings.secret_key,
            secure=self.settings.secure,
        )

    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a bucket exists in MinIO.

        Args:
            bucket_name (str): The name of the bucket to check.

        Returns:
            bool: True if the bucket exists, False otherwise.
        """
        is_exist = self._client.bucket_exists(bucket_name)
        return is_exist

    def create_bucket(self, bucket_name: str) -> None:
        """Create a new bucket in MinIO.

        Args:
            bucket_name (str): The name of the bucket to create.
        Raises:
            ValueError: If the bucket already exists.
        """
        if not self.bucket_exists(bucket_name):
            self._client.make_bucket(bucket_name)
        else:
            pass
    def delete_bucket(self, bucket_name: str) -> None:
        """Delete a bucket in MinIO.

        Args:
            bucket_name (str): The name of the bucket to delete.
        Raises:
            ValueError: If the bucket does not exist.
        """
        if self.bucket_exists(bucket_name):
            objects = self._client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                self._client.remove_object(bucket_name, obj.object_name)
            self._client.remove_bucket(bucket_name)
        else:
            raise ValueError(f"Bucket '{bucket_name}' does not exist and cannot be deleted.")

    def upload_file(self, input: MinioServiceInput) -> MinioServiceOutput:
        """Upload a file to MinIO.

        Args:
            input (MinioServiceInput): The input data for the upload.

        Returns:
            MinioServiceOutput: The output data after the upload.
        Raises:
            ValueError: If the bucket does not exist.
        """
        if not self.bucket_exists(input.bucket_name):
            raise ValueError(f"Bucket '{input.bucket_name}' does not exist.")

        if input.file_path:
            self._client.fput_object(
                bucket_name=input.bucket_name,
                object_name=input.object_name,
                file_path=input.file_path,
                content_type=input.content_type,
                metadata=input.metadata if input.metadata else None,
            )

        elif input.data:
            input.data.seek(0)
            self._client.put_object(
                bucket_name=input.bucket_name,
                object_name=input.object_name,
                data=input.data,
                length=input.data.getbuffer().nbytes,
                content_type=input.content_type,
                metadata=input.metadata if input.metadata else None,
            )
        else:
            raise ValueError("Either file_path or data must be provided.")

        return MinioServiceOutput()


    def download_file(self, input: MinioServiceInput) -> MinioServiceOutput:
        """Download a file from MinIO.

        Args:
            input (MinioInput): The input data for the download.

        Raises:
            ValueError: If the bucket does not exist.

        Returns:
            MinioOutput: The output data after the download.
        """
        if not self.bucket_exists(input.bucket_name):
            raise ValueError(f"Bucket '{input.bucket_name}' does not exist.")

        self._client.fget_object(
            bucket_name=input.bucket_name,
            object_name=input.object_name,
            file_path=input.file_path,
        )
        return MinioServiceOutput()

    def delete_file(self, input: MinioServiceInput) -> MinioServiceOutput:
        """Delete a file from MinIO.

        Args:
            input (MinioServiceInput): The input data for the delete.

        Returns:
            MinioOutput: The output data after the delete.
        Raises:
            ValueError: If the bucket does not exist.
        """
        if not self.bucket_exists(input.bucket_name):
            raise ValueError(f"Bucket '{input.bucket_name}' does not exist.")

        self._client.remove_object(
            bucket_name=input.bucket_name,
            object_name=input.object_name,
        )
        return MinioServiceOutput()

    def upload_data(self, input: MinioServiceInput) -> MinioServiceOutput:
        """Upload data to MinIO.

        Args:
            input (MinioServiceInput): The input data for the upload.

        Returns:
            MinioOutput: The output data after the upload.
        Raises:
            ValueError: If the bucket does not exist.
        """
        if not self.bucket_exists(input.bucket_name):
            raise ValueError(f"Bucket '{input.bucket_name}' does not exist.")

        self._client.put_object(
            bucket_name=input.bucket_name,
            object_name=input.object_name,
            data=input.data,
            length=input.data.getbuffer().nbytes if input.data else 0,
            content_type=input.content_type,
            metadata=input.metadata if input.metadata else None,
        )
        return MinioServiceOutput()
