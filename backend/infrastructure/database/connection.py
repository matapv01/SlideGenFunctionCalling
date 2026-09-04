# File: backend/infrastructure/database/connection.py

import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "slidegen.db")


@contextmanager
def get_db_connection():
    """Context manager for database connection"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with all tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users table - now with subscription fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                subscription_tier TEXT DEFAULT 'free',
                subscription_expires_at TIMESTAMP,
                daily_usage_reset_date DATE DEFAULT CURRENT_DATE,
                idea_usage_today INTEGER DEFAULT 0,
                docx_usage_today INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
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

        # Project collaborators and access control. Owners are represented by
        # projects.user_id; this table stores invited members only.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_collaborators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                invited_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, user_id),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Immutable snapshots of a project at save/restore points.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                label TEXT,
                snapshot_json TEXT NOT NULL,
                snapshot_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Slide/element comments. Comments are soft-resolved instead of deleted
        # so a review trail remains useful after a version is restored.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                slide_index INTEGER,
                element_id TEXT,
                body TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Subscription codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                tier TEXT NOT NULL,
                duration_days INTEGER DEFAULT 30,
                max_uses INTEGER DEFAULT 1,
                current_uses INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                code_type TEXT DEFAULT 'limited',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Code redemption history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_redemptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                tier_granted TEXT NOT NULL,
                expires_at TIMESTAMP,
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Usage logs for analytics/debugging
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature_type TEXT NOT NULL,
                feature_data TEXT,
                usage_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_slides_project_id ON slides(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_logs_user_date ON daily_usage_logs(user_id, usage_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_code_redemptions_user ON code_redemptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_collaborators_user ON project_collaborators(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_versions_project ON project_versions(project_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_comments_project ON project_comments(project_id, created_at DESC)")

        # Migrate: add code_type column to existing DB if missing (must run before INSERT below)
        try:
            cursor.execute("ALTER TABLE subscription_codes ADD COLUMN code_type TEXT DEFAULT 'limited'")
        except Exception:
            pass  # Column already exists

        # Insert default subscription codes if they don't exist
        cursor.execute("""
            INSERT OR IGNORE INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
            VALUES ('SLIDEGENIUS', 'ultra', 30, -1, 'unlimited')
        """)

        # Ensure existing codes use 30-day duration
        cursor.execute("""
            UPDATE subscription_codes SET duration_days = 30
            WHERE code = 'SLIDEGENIUS' AND duration_days != 30
        """)

        # Set SLIDEGENIUS to unlimited type in existing DBs
        cursor.execute("""
            UPDATE subscription_codes SET code_type = 'unlimited'
            WHERE code = 'SLIDEGENIUS' AND (code_type IS NULL OR code_type = 'limited')
        """)

        # Migrate: add cancel_at_period_end column to users if missing
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN cancel_at_period_end BOOLEAN DEFAULT 0")
        except Exception:
            pass  # Column already exists

        # Migrate existing paid users with NULL expires_at → set 30-day expiry from now
        cursor.execute("""
            UPDATE users SET subscription_expires_at = datetime('now', '+30 days')
            WHERE subscription_tier != 'free' AND subscription_expires_at IS NULL
        """)

        # Add default subscription fields to existing users who don't have them
        cursor.execute("""
            UPDATE users SET
                subscription_tier = 'free',
                daily_usage_reset_date = CURRENT_DATE,
                idea_usage_today = 0,
                docx_usage_today = 0
            WHERE subscription_tier IS NULL
        """)

        conn.commit()
        print("[OK] Database initialized successfully with all tables")
