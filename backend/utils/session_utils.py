# File: backend/utils/session_utils.py

"""Utilities for session file management"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException
import aiofiles

from backend.config import TEMP_DIR
from backend.api.constants import FilePatterns, SourceTypes

class SessionManager:
    """Manages session file operations with async I/O"""

    @staticmethod
    def get_session_path(session_id: str, session_type: str = "idea") -> Path:
        """Get the file path for a session"""
        if session_type == "idea":
            return TEMP_DIR / FilePatterns.IDEA_SESSION.format(session_id)
        elif session_type == "structure":
            return TEMP_DIR / FilePatterns.APPROVED_STRUCTURE.format(session_id)
        else:
            raise ValueError(f"Unknown session type: {session_type}")

    @staticmethod
    async def read_session_json(session_id: str, session_type: str = "idea") -> Dict[str, Any]:
        """Safely read JSON session file with async I/O"""
        file_path = SessionManager.get_session_path(session_id, session_type)

        if not file_path.exists():
            raise HTTPException(400, f"Session not found: {session_id}")

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(500, f"Invalid session data: {str(e)}")
        except Exception as e:
            raise HTTPException(500, f"Failed to read session: {str(e)}")

    @staticmethod
    async def write_session_json(session_id: str, data: Dict[str, Any], session_type: str = "idea") -> None:
        """Write session data with async I/O"""
        file_path = SessionManager.get_session_path(session_id, session_type)

        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                content = json.dumps(data, ensure_ascii=False, indent=2)
                await f.write(content)
        except Exception as e:
            raise HTTPException(500, f"Failed to save session: {str(e)}")

    @staticmethod
    async def delete_session(session_id: str, session_type: str = "idea") -> bool:
        """Delete a session file"""
        file_path = SessionManager.get_session_path(session_id, session_type)

        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def session_exists(session_id: str, session_type: str = "idea") -> bool:
        """Check if session file exists without raising exceptions"""
        file_path = SessionManager.get_session_path(session_id, session_type)
        return file_path.exists()

    @staticmethod
    async def cleanup_expired_sessions(max_age_hours: int = 24) -> int:
        """Clean up session files older than max_age_hours"""
        import time

        cleanup_count = 0
        cutoff_time = time.time() - (max_age_hours * 3600)

        try:
            for file_path in TEMP_DIR.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleanup_count += 1
                    except Exception:
                        pass
        except Exception:
            pass

        return cleanup_count