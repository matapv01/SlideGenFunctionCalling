from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from base import BaseModel


class StorageBaseInput(BaseModel):
    bucket_name: str
    object_name: str


class StorageBaseOutput(BaseModel):
    pass


class StorageBase(BaseModel, ABC):

    @property
    @abstractmethod
    def _client(self):
        """Abstract property to get the storage client."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def upload_file(self, input: StorageBaseInput) -> StorageBaseOutput:
        """Upload a file to the storage."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def download_file(self, input: StorageBaseInput) -> StorageBaseOutput:
        """Download a file from the storage."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def delete_file(self, input: StorageBaseInput) -> StorageBaseOutput:
        """Delete a file from the storage."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def upload_data(self, input: StorageBaseInput) -> StorageBaseOutput:
        """Upload data to the storage."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def create_bucket(self, bucket_name: str) -> None:
        """Create a new bucket."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a bucket exists."""
        raise NotImplementedError('Subclasses must implement this method.')

    @abstractmethod
    def delete_bucket(self, bucket_name: str) -> None:
        """Delete a bucket."""
        raise NotImplementedError('Subclasses must implement this method.')
