# File: backend/infrastructure/database/repositories/sqlite_project_repo.py

from typing import Optional, List
import json
from backend.domain.ports.project_repository import ProjectRepository
from backend.infrastructure.database.connection import get_db_connection
from backend.domain.entities.project import Project, Slide


class SqliteProjectRepository(ProjectRepository):
    def _map_slide(self, row) -> Slide:
        if not row: return None
        return Slide(
            id=row['id'],
            project_id=row['project_id'],
            slide_index=row['slide_index'],
            slide_type=row['slide_type'],
            title=row['title'],
            content_text=row['content_text'],
            html_content=row['html_content'],
            design_settings=json.loads(row['design_settings']) if row['design_settings'] else {}
        )

    def _map_project(self, row) -> Project:
        if not row: return None
        return Project(
            id=row['id'],
            user_id=row['user_id'],
            title=row['title'],
            description=row['description'],
            source_type=row['source_type'],
            status=row['status'],
            updated_at=row['updated_at'],
            created_at=row['created_at'],
            slides=[],
            metadata={}
        )

    def create_project(self, user_id: int, title: str, description: str = None,
                    source_type: str = 'idea', source_data: dict = None) -> int:
        """Create new project and return project ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            source_data_str = json.dumps(source_data) if source_data else None
            cursor.execute("""
                INSERT INTO projects (user_id, title, description, source_type, source_data)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, title, description, source_type, source_data_str))
            conn.commit()
            return cursor.lastrowid


    def get_user_projects(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Project]:
        """Get all projects for a user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.* FROM projects p
                LEFT JOIN project_collaborators pc ON pc.project_id = p.id AND pc.user_id = ?
                WHERE p.user_id = ? OR pc.user_id IS NOT NULL
                ORDER BY p.updated_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, user_id, limit, offset))
            rows = cursor.fetchall()
            return [self._map_project(row) for row in rows]


    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            project = self._map_project(row)
            if project:
                project.slides = self.get_project_slides(project_id)
            return project


    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._map_project(row) for row in rows]


    def update_project(self, project_id: int, title: str = None, description: str = None,
                    status: str = None, slide_count: int = None,
                    thumbnail_url: str = None) -> None:
        """Update project"""
        with get_db_connection() as conn:
            # Logic update dynamic
            updates = []
            params = []
            if title is not None: updates.append("title = ?"); params.append(title)
            if description is not None: updates.append("description = ?"); params.append(description)
            if status is not None: updates.append("status = ?"); params.append(status)
            if slide_count is not None: updates.append("slide_count = ?"); params.append(slide_count)
            if thumbnail_url is not None: updates.append("thumbnail_url = ?"); params.append(thumbnail_url)
            
            if not updates: return 
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(project_id)
            
            query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, tuple(params))
            conn.commit()


    def delete_project(self, project_id: int) -> None:
        """Delete project and all associated slides"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()


    def create_slide(self, slide: Slide) -> int:
        """Create new slide"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            design_settings_str = json.dumps(slide.design_settings)
            cursor.execute("""
                INSERT INTO slides (project_id, slide_index, slide_type, title,
                                content_text, html_content, design_settings)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (slide.project_id, slide.slide_index, slide.slide_type, slide.title, slide.content_text,
                slide.html_content, design_settings_str))
            conn.commit()
            return cursor.lastrowid


    def get_project_slides(self, project_id: int) -> List[Slide]:
        """Get all slides for a project"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM slides
                WHERE project_id = ?
                ORDER BY slide_index ASC
            """, (project_id,))
            return [self._map_slide(row) for row in cursor.fetchall()]


    def get_slide(self, slide_id: int) -> Optional[Slide]:
        """Get slide by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM slides WHERE id = ?", (slide_id,))
            return self._map_slide(cursor.fetchone())


    def update_slide(self, slide: Slide):
        """Update slide"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            design_settings_str = json.dumps(slide.design_settings)
            cursor.execute("""
                UPDATE slides SET
                    title = COALESCE(?, title),
                    content_text = COALESCE(?, content_text),
                    html_content = COALESCE(?, html_content),
                    design_settings = COALESCE(?, design_settings),
                    slide_index = COALESCE(?, slide_index),
                    slide_type = COALESCE(?, slide_type),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (slide.title, slide.content_text, slide.html_content, 
                  design_settings_str, slide.slide_index, slide.slide_type, slide.id))
            conn.commit()


    def delete_slide(self, slide_id: int):
        """Delete slide"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM slides WHERE id = ?", (slide_id,))
            conn.commit()


    def save_metadata(self, project_id: int, slide_options: dict = None,
                            workflow_config: dict = None, generation_params: dict = None):
        """Save project metadata"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            slide_options_str = json.dumps(slide_options) if slide_options else None
            workflow_config_str = json.dumps(workflow_config) if workflow_config else None
            generation_params_str = json.dumps(generation_params) if generation_params else None

            cursor.execute("""
                INSERT INTO project_metadata (project_id, slide_options, workflow_config, generation_params)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    slide_options = COALESCE(?, slide_options),
                    workflow_config = COALESCE(?, workflow_config),
                    generation_params = COALESCE(?, generation_params)
            """, (project_id, slide_options_str, workflow_config_str, generation_params_str,
                slide_options_str, workflow_config_str, generation_params_str))
            conn.commit()


    def get_metadata(self, project_id: int) -> Optional[dict]:
        """Get project metadata"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM project_metadata WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                metadata = dict(row)
                if metadata.get('slide_options'):
                    metadata['slide_options'] = json.loads(metadata['slide_options'])
                if metadata.get('workflow_config'):
                    metadata['workflow_config'] = json.loads(metadata['workflow_config'])
                if metadata.get('generation_params'):
                    metadata['generation_params'] = json.loads(metadata['generation_params'])
                return metadata
            return None

    # --- Collaboration / access control ---

    def get_project_role(self, project_id: int, user_id: int) -> Optional[str]:
        """Return owner/editor/viewer for a user, or None when not shared."""
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT user_id FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not row:
                return None
            if int(row["user_id"]) == int(user_id):
                return "owner"
            member = conn.execute(
                "SELECT role FROM project_collaborators WHERE project_id = ? AND user_id = ?",
                (project_id, user_id),
            ).fetchone()
            return str(member["role"]) if member else None

    def list_collaborators(self, project_id: int) -> list[dict]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT pc.id, pc.project_id, pc.user_id, pc.role,
                       pc.created_at, pc.updated_at,
                       u.email, COALESCE(up.full_name, u.email) AS name
                FROM project_collaborators pc
                JOIN users u ON u.id = pc.user_id
                LEFT JOIN user_profiles up ON up.user_id = u.id
                WHERE pc.project_id = ?
                ORDER BY pc.created_at ASC
                """,
                (project_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def find_user_by_email(self, email: str):
        with get_db_connection() as conn:
            return conn.execute(
                "SELECT id, email FROM users WHERE lower(email) = lower(?)", (email.strip(),)
            ).fetchone()

    def upsert_collaborator(self, project_id: int, user_id: int, role: str, invited_by: int) -> dict:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO project_collaborators (project_id, user_id, role, invited_by)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id, user_id) DO UPDATE SET
                    role = excluded.role,
                    invited_by = excluded.invited_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (project_id, user_id, role, invited_by),
            )
            conn.commit()
        return next(item for item in self.list_collaborators(project_id) if item["user_id"] == user_id)

    def update_collaborator_role(self, project_id: int, user_id: int, role: str) -> None:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE project_collaborators SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE project_id = ? AND user_id = ?",
                (role, project_id, user_id),
            )
            conn.commit()

    def remove_collaborator(self, project_id: int, user_id: int) -> None:
        with get_db_connection() as conn:
            conn.execute(
                "DELETE FROM project_collaborators WHERE project_id = ? AND user_id = ?",
                (project_id, user_id),
            )
            conn.commit()
