import hashlib
import json
from typing import Any, Optional

from fastapi import HTTPException

from backend.infrastructure.database.connection import get_db_connection
from backend.infrastructure.database.repositories.sqlite_project_repo import SqliteProjectRepository


class CollaborationService:
    """Project versions, comments and member access backed by SQLite."""

    def __init__(self, project_repo: Optional[SqliteProjectRepository] = None):
        self.repo = project_repo or SqliteProjectRepository()

    def _role(self, project_id: int, user_id: int, minimum: str = "viewer") -> str:
        return self._project_service_role(project_id, user_id, minimum)

    def _project_service_role(self, project_id: int, user_id: int, minimum: str) -> str:
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        role = self.repo.get_project_role(project_id, user_id)
        if role is None:
            raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập dự án này")
        ranks = {"viewer": 1, "editor": 2, "owner": 3}
        if ranks.get(role, 0) < ranks.get(minimum, 1):
            raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")
        return role

    # --- Members ---

    def list_collaborators(self, project_id: int, user_id: int) -> list[dict]:
        self._role(project_id, user_id)
        project = self.repo.get_project(project_id)
        with get_db_connection() as conn:
            owner = conn.execute(
                """
                SELECT u.id AS user_id, u.email, COALESCE(up.full_name, u.email) AS name
                FROM users u LEFT JOIN user_profiles up ON up.user_id = u.id
                WHERE u.id = ?
                """,
                (project.user_id,),
            ).fetchone()
        result = []
        if owner:
            result.append({
                "id": None,
                "project_id": project_id,
                "user_id": owner["user_id"],
                "email": owner["email"],
                "name": owner["name"],
                "role": "owner",
                "owner": True,
                "created_at": project.created_at,
            })
        result.extend({**item, "owner": False} for item in self.repo.list_collaborators(project_id))
        return result

    def invite_collaborator(self, project_id: int, owner_id: int, email: str, role: str) -> dict:
        self._role(project_id, owner_id, "owner")
        user = self.repo.find_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản với email này")
        if int(user["id"]) == int(owner_id):
            raise HTTPException(status_code=400, detail="Chủ sở hữu đã có toàn quyền")
        return {**self.repo.upsert_collaborator(project_id, int(user["id"]), role, owner_id), "owner": False}

    def update_collaborator(self, project_id: int, owner_id: int, member_id: int, role: str) -> dict:
        self._role(project_id, owner_id, "owner")
        if not self.repo.get_project_role(project_id, member_id):
            raise HTTPException(status_code=404, detail="Thành viên không thuộc dự án")
        if self.repo.get_project_role(project_id, member_id) == "owner":
            raise HTTPException(status_code=400, detail="Không thể thay đổi quyền chủ sở hữu")
        self.repo.update_collaborator_role(project_id, member_id, role)
        return next(item for item in self.list_collaborators(project_id, owner_id) if item["user_id"] == member_id)

    def remove_collaborator(self, project_id: int, owner_id: int, member_id: int) -> None:
        self._role(project_id, owner_id, "owner")
        if self.repo.get_project_role(project_id, member_id) in (None, "owner"):
            raise HTTPException(status_code=404, detail="Thành viên không thuộc dự án")
        self.repo.remove_collaborator(project_id, member_id)

    # --- Version history ---

    def list_versions(self, project_id: int, user_id: int, limit: int = 50) -> list[dict]:
        self._role(project_id, user_id)
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT v.id, v.project_id, v.label, v.created_at,
                       v.user_id AS created_by_id, u.email AS created_by_email,
                       COALESCE(up.full_name, u.email) AS created_by_name
                FROM project_versions v
                JOIN users u ON u.id = v.user_id
                LEFT JOIN user_profiles up ON up.user_id = u.id
                WHERE v.project_id = ?
                ORDER BY v.created_at DESC, v.id DESC LIMIT ?
                """,
                (project_id, max(1, min(limit, 200))),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "project_id": row["project_id"],
                "label": row["label"],
                "created_at": row["created_at"],
                "created_by": {
                    "id": row["created_by_id"],
                    "email": row["created_by_email"],
                    "name": row["created_by_name"],
                },
            }
            for row in rows
        ]

    def create_version(self, project_id: int, user_id: int, snapshot: dict[str, Any], label: Optional[str] = None) -> dict:
        self._role(project_id, user_id, "editor")
        snapshot_json = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        snapshot_hash = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()
        with get_db_connection() as conn:
            latest = conn.execute(
                "SELECT id, project_id, label, created_at FROM project_versions WHERE project_id = ? ORDER BY id DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            if latest:
                latest_hash = conn.execute("SELECT snapshot_hash FROM project_versions WHERE id = ?", (latest["id"],)).fetchone()
                if latest_hash and latest_hash["snapshot_hash"] == snapshot_hash:
                    return {**dict(latest), "created_by": {"id": user_id}}
            cursor = conn.execute(
                """
                INSERT INTO project_versions (project_id, user_id, label, snapshot_json, snapshot_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, user_id, label or "Autosave", snapshot_json, snapshot_hash),
            )
            version_id = cursor.lastrowid
            conn.execute(
                "DELETE FROM project_versions WHERE project_id = ? AND id NOT IN (SELECT id FROM project_versions WHERE project_id = ? ORDER BY id DESC LIMIT 100)",
                (project_id, project_id),
            )
            conn.commit()
        return {
            "id": version_id,
            "project_id": project_id,
            "label": label or "Autosave",
            "created_by": {"id": user_id},
        }

    def get_version(self, project_id: int, user_id: int, version_id: int) -> dict:
        self._role(project_id, user_id)
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT id, project_id, user_id, label, snapshot_json, created_at FROM project_versions WHERE id = ? AND project_id = ?",
                (version_id, project_id),
            ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên bản")
        return {
            "id": row["id"],
            "project_id": row["project_id"],
            "label": row["label"],
            "created_at": row["created_at"],
            "created_by": {"id": row["user_id"]},
            "snapshot": json.loads(row["snapshot_json"]),
        }

    def restore_version(self, project_id: int, user_id: int, version_id: int) -> dict:
        self._role(project_id, user_id, "editor")
        version = self.get_version(project_id, user_id, version_id)
        slides = (version.get("snapshot") or {}).get("slides")
        if not isinstance(slides, list) or not slides:
            raise HTTPException(status_code=422, detail="Phiên bản không có dữ liệu slide hợp lệ")
        with get_db_connection() as conn:
            try:
                conn.execute("BEGIN")
                conn.execute("DELETE FROM slides WHERE project_id = ?", (project_id,))
                for index, slide in enumerate(slides):
                    conn.execute(
                        """
                        INSERT INTO slides (project_id, slide_index, slide_type, title, content_text, html_content, design_settings)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            project_id,
                            int(slide.get("slide_index", index)),
                            slide.get("slide_type", "intro" if index == 0 else "content"),
                            slide.get("title", f"Slide {index + 1}"),
                            slide.get("content_text", ""),
                            slide.get("html_content", ""),
                            json.dumps(slide.get("design_settings") or {"format": "xml"}, ensure_ascii=False),
                        ),
                    )
                conn.execute(
                    "UPDATE projects SET slide_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (len(slides), project_id),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {"version_id": version_id, "restored": True}

    # --- Comments ---

    def list_comments(self, project_id: int, user_id: int, include_resolved: bool = True) -> list[dict]:
        self._role(project_id, user_id)
        query = """
            SELECT c.*, u.email, COALESCE(up.full_name, u.email) AS name
            FROM project_comments c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN user_profiles up ON up.user_id = u.id
            WHERE c.project_id = ?
        """
        params: list[Any] = [project_id]
        if not include_resolved:
            query += " AND c.resolved = 0"
        query += " ORDER BY c.created_at DESC, c.id DESC"
        with get_db_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._comment_dict(row) for row in rows]

    @staticmethod
    def _comment_dict(row) -> dict:
        return {
            "id": row["id"],
            "project_id": row["project_id"],
            "user_id": row["user_id"],
            "author": {"id": row["user_id"], "email": row["email"], "name": row["name"]},
            "body": row["body"],
            "slide_index": row["slide_index"],
            "element_id": row["element_id"],
            "resolved": bool(row["resolved"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def create_comment(self, project_id: int, user_id: int, body: str, slide_index: Optional[int], element_id: Optional[str]) -> dict:
        self._role(project_id, user_id)
        with get_db_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO project_comments (project_id, user_id, body, slide_index, element_id) VALUES (?, ?, ?, ?, ?)",
                (project_id, user_id, body.strip(), slide_index, element_id),
            )
            conn.commit()
            comment_id = cursor.lastrowid
            row = conn.execute(
                """
                SELECT c.*, u.email, COALESCE(up.full_name, u.email) AS name
                FROM project_comments c JOIN users u ON u.id = c.user_id
                LEFT JOIN user_profiles up ON up.user_id = u.id WHERE c.id = ?
                """,
                (comment_id,),
            ).fetchone()
        return self._comment_dict(row)

    def update_comment(self, project_id: int, user_id: int, comment_id: int, body: Optional[str], resolved: Optional[bool]) -> dict:
        role = self._role(project_id, user_id)
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM project_comments WHERE id = ? AND project_id = ?", (comment_id, project_id)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy bình luận")
            if int(row["user_id"]) != int(user_id) and role not in ("editor", "owner"):
                raise HTTPException(status_code=403, detail="Bạn không có quyền sửa bình luận này")
            updates, params = [], []
            if body is not None:
                updates.append("body = ?")
                params.append(body.strip())
            if resolved is not None:
                if role not in ("editor", "owner"):
                    raise HTTPException(status_code=403, detail="Chỉ người chỉnh sửa mới có thể giải quyết bình luận")
                updates.append("resolved = ?")
                params.append(int(resolved))
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                conn.execute(f"UPDATE project_comments SET {', '.join(updates)} WHERE id = ?", (*params, comment_id))
                conn.commit()
            result = conn.execute(
                """
                SELECT c.*, u.email, COALESCE(up.full_name, u.email) AS name
                FROM project_comments c JOIN users u ON u.id = c.user_id
                LEFT JOIN user_profiles up ON up.user_id = u.id WHERE c.id = ?
                """,
                (comment_id,),
            ).fetchone()
        return self._comment_dict(result)

    def delete_comment(self, project_id: int, user_id: int, comment_id: int) -> None:
        role = self._role(project_id, user_id)
        with get_db_connection() as conn:
            row = conn.execute("SELECT user_id FROM project_comments WHERE id = ? AND project_id = ?", (comment_id, project_id)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy bình luận")
            if int(row["user_id"]) != int(user_id) and role not in ("editor", "owner"):
                raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bình luận này")
            conn.execute("DELETE FROM project_comments WHERE id = ?", (comment_id,))
            conn.commit()
