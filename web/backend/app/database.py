# web/backend/app/database.py
import sqlite3
from typing import Optional, List
from contextlib import contextmanager
import os
import json
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "slidegen.db")

@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database with all tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_vip BOOLEAN DEFAULT 0
            )
        """)
        
        # User profile/info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                bio TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'light',
                default_transition_enabled BOOLEAN DEFAULT 1,
                default_thank_you_enabled BOOLEAN DEFAULT 1,
                default_content_length TEXT DEFAULT 'standard',
                language TEXT DEFAULT 'en',
                settings_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                source_type TEXT NOT NULL,
                source_data TEXT,
                status TEXT DEFAULT 'draft',
                slide_count INTEGER DEFAULT 0,
                thumbnail_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Slides table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                slide_index INTEGER NOT NULL,
                slide_type TEXT NOT NULL,
                title TEXT,
                content_text TEXT,
                html_content TEXT,
                design_settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Project metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER UNIQUE NOT NULL,
                slide_options TEXT,
                workflow_config TEXT,
                generation_params TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slides_project_id ON slides(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC)")
        
        conn.commit()
        print("✅ Database initialized successfully with all tables")

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_user(email: str, username: str, hashed_password: str, is_vip: bool = False) -> int:
    """Create new user and return user ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, username, hashed_password, is_vip) VALUES (?, ?, ?, ?)",
            (email, username, hashed_password, is_vip)
        )
        conn.commit()
        return cursor.lastrowid

def get_all_users() -> List[dict]:
    """Get all users (for admin purposes)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, created_at, is_active, is_vip FROM users")
        return [dict(row) for row in cursor.fetchall()]

def update_user_vip_status(user_id: int, is_vip: bool) -> None:
    """Update user VIP status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET is_vip = ? WHERE id = ?",
            (is_vip, user_id)
        )
        conn.commit()

def migrate_add_vip_column():
    """Migration: Add is_vip column to existing users table"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            # Check if column already exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'is_vip' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_vip BOOLEAN DEFAULT 0")
                conn.commit()
                print("✅ Added is_vip column to users table")
            else:
                print("ℹ️  is_vip column already exists")
        except Exception as e:
            print(f"❌ Migration failed: {e}")

# ==================== User Profile Functions ====================

def get_user_profile(user_id: int) -> Optional[dict]:
    """Get user profile"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_or_update_user_profile(user_id: int, full_name: str = None, 
                                   avatar_url: str = None, bio: str = None):
    """Create or update user profile"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profiles (user_id, full_name, avatar_url, bio, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = COALESCE(?, full_name),
                avatar_url = COALESCE(?, avatar_url),
                bio = COALESCE(?, bio),
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, full_name, avatar_url, bio, full_name, avatar_url, bio))
        conn.commit()

# ==================== User Settings Functions ====================

def get_user_settings(user_id: int) -> Optional[dict]:
    """Get user settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get('settings_json'):
                result['settings_json'] = json.loads(result['settings_json'])
            return result
        return None

def create_default_settings(user_id: int):
    """Create default settings for new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_settings (user_id) VALUES (?)
        """, (user_id,))
        conn.commit()

def update_user_settings(user_id: int, theme: str = None, 
                        default_transition_enabled: bool = None,
                        default_thank_you_enabled: bool = None,
                        default_content_length: str = None,
                        language: str = None,
                        settings_json: dict = None):
    """Update user settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        settings_json_str = json.dumps(settings_json) if settings_json else None
        cursor.execute("""
            INSERT INTO user_settings (user_id, theme, default_transition_enabled, 
                                      default_thank_you_enabled, default_content_length,
                                      language, settings_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                theme = COALESCE(?, theme),
                default_transition_enabled = COALESCE(?, default_transition_enabled),
                default_thank_you_enabled = COALESCE(?, default_thank_you_enabled),
                default_content_length = COALESCE(?, default_content_length),
                language = COALESCE(?, language),
                settings_json = COALESCE(?, settings_json),
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, theme, default_transition_enabled, default_thank_you_enabled,
              default_content_length, language, settings_json_str,
              theme, default_transition_enabled, default_thank_you_enabled,
              default_content_length, language, settings_json_str))
        conn.commit()

# ==================== Project Functions ====================

def create_project(user_id: int, title: str, description: str = None,
                  source_type: str = 'idea', source_data: dict = None) -> int:
    """Create new project and return project ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        source_data_str = json.dumps(source_data) if source_data else None
        cursor.execute("""
            INSERT INTO projects (user_id, title, description, source_type, source_data)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, description, source_type, source_data_str))
        conn.commit()
        return cursor.lastrowid

def get_user_projects(user_id: int, limit: int = 50, offset: int = 0) -> List[dict]:
    """Get all projects for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM projects 
            WHERE user_id = ? 
            ORDER BY updated_at DESC 
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_project(project_id: int) -> Optional[dict]:
    """Get project by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_projects():
    """Get all projects"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_project(project_id: int, title: str = None, description: str = None,
                  status: str = None, slide_count: int = None, 
                  thumbnail_url: str = None):
    """Update project"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects SET
                title = COALESCE(?, title),
                description = COALESCE(?, description),
                status = COALESCE(?, status),
                slide_count = COALESCE(?, slide_count),
                thumbnail_url = COALESCE(?, thumbnail_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, description, status, slide_count, thumbnail_url, project_id))
        conn.commit()

def delete_project(project_id: int):
    """Delete project and all associated slides"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()

# ==================== Slide Functions ====================

def create_slide(project_id: int, slide_index: int, slide_type: str,
                title: str = None, content_text: str = None,
                html_content: str = None, design_settings: dict = None) -> int:
    """Create new slide"""
    with get_db() as conn:
        cursor = conn.cursor()
        design_settings_str = json.dumps(design_settings) if design_settings else None
        cursor.execute("""
            INSERT INTO slides (project_id, slide_index, slide_type, title, 
                              content_text, html_content, design_settings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, slide_index, slide_type, title, content_text, 
              html_content, design_settings_str))
        conn.commit()
        return cursor.lastrowid

def get_project_slides(project_id: int) -> List[dict]:
    """Get all slides for a project"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM slides 
            WHERE project_id = ? 
            ORDER BY slide_index ASC
        """, (project_id,))
        slides = []
        for row in cursor.fetchall():
            slide = dict(row)
            if slide.get('design_settings'):
                slide['design_settings'] = json.loads(slide['design_settings'])
            slides.append(slide)
        return slides

def get_slide(slide_id: int) -> Optional[dict]:
    """Get slide by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM slides WHERE id = ?", (slide_id,))
        row = cursor.fetchone()
        if row:
            slide = dict(row)
            if slide.get('design_settings'):
                slide['design_settings'] = json.loads(slide['design_settings'])
            return slide
        return None

def update_slide(slide_id: int, title: str = None, content_text: str = None,
                html_content: str = None, design_settings: dict = None):
    """Update slide"""
    with get_db() as conn:
        cursor = conn.cursor()
        design_settings_str = json.dumps(design_settings) if design_settings else None
        cursor.execute("""
            UPDATE slides SET
                title = COALESCE(?, title),
                content_text = COALESCE(?, content_text),
                html_content = COALESCE(?, html_content),
                design_settings = COALESCE(?, design_settings),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, content_text, html_content, design_settings_str, slide_id))
        conn.commit()

def delete_slide(slide_id: int):
    """Delete slide"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM slides WHERE id = ?", (slide_id,))
        conn.commit()

# ==================== Project Metadata Functions ====================

def save_project_metadata(project_id: int, slide_options: dict = None,
                         workflow_config: dict = None, generation_params: dict = None):
    """Save project metadata"""
    with get_db() as conn:
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

def get_project_metadata(project_id: int) -> Optional[dict]:
    """Get project metadata"""
    with get_db() as conn:
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
