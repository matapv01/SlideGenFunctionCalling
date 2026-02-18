# File: backend/domain/ports/convert_provider.py

from typing import Protocol
import subprocess

class ConvertProvider(Protocol):
    """Interface giao tiếp với module convert slide từ dạng có cấu trúc sang phi cấu trúc"""
    def __init__(self, project_dir: str): ...
    def check_dependencies(self) -> bool: ...
    def run_conversion_command(self, input_path: str, output_path: str) -> subprocess.CompletedProcess: ...