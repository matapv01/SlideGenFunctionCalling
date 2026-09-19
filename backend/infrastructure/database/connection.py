# File: backend/infrastructure/database/connection.py

import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv(
    "SLIDEGEN_DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "slidegen.db"),
)


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
                usage_window_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chat_usage_5h INTEGER DEFAULT 0,
                chat_usage_credits_5h REAL DEFAULT 0,
                chat_messages_5h INTEGER DEFAULT 0,
                docx_usage_5h INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN NOT NULL DEFAULT 0
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

        # Chatbot sessions and short-term conversation memory. The chatbot is
        # a separate application service, so its conversation state does not
        # share the temporary structure/generation sessions above.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                project_id INTEGER,
                title TEXT,
                history_summary TEXT,
                max_turns INTEGER NOT NULL DEFAULT 5,
                archived BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
                content TEXT NOT NULL,
                standalone_query TEXT,
                model TEXT,
                effort TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chatbot_sessions(id) ON DELETE CASCADE
            )
        """)

        # Canonical documents owned by the chatbot. The original DOCX is
        # preprocessed into Markdown + hierarchical JSON before these rows
        # are indexed for retrieval.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_documents (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                project_id INTEGER,
                original_filename TEXT NOT NULL,
                title TEXT,
                status TEXT NOT NULL DEFAULT 'processing'
                    CHECK (status IN ('processing', 'ready', 'failed')),
                content_hash TEXT NOT NULL,
                size_bytes INTEGER NOT NULL DEFAULT 0,
                markdown_path TEXT,
                structure_json TEXT,
                images_json TEXT,
                error_message TEXT,
                chunk_index_version INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_session_documents (
                session_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, document_id),
                FOREIGN KEY (session_id) REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES chatbot_documents(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                title TEXT NOT NULL,
                section_path TEXT NOT NULL,
                content TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                node_key TEXT NOT NULL DEFAULT '',
                parent_node_key TEXT,
                node_kind TEXT NOT NULL DEFAULT 'content',
                embedding_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(document_id, ordinal),
                FOREIGN KEY (document_id) REFERENCES chatbot_documents(id) ON DELETE CASCADE
            )
        """)

        # Citation rows make retrieved sources auditable instead of keeping
        # them only in an opaque assistant-message blob.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_message_citations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                document_id TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                similarity REAL NOT NULL,
                citation_order INTEGER NOT NULL,
                FOREIGN KEY (message_id) REFERENCES chatbot_messages(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES chatbot_documents(id) ON DELETE CASCADE,
                FOREIGN KEY (chunk_id) REFERENCES chatbot_document_chunks(id) ON DELETE CASCADE
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_usage_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                multiplier REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(kind, name)
            )
        """)

        # Runtime subscription policy is administrator-managed. These rows are
        # only inserted when a database is first created; INSERT OR IGNORE
        # preserves every value changed later from the admin console.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plan_limits (
                tier TEXT PRIMARY KEY,
                chat_credits REAL NOT NULL,
                docx_upload INTEGER NOT NULL,
                max_docx_slides INTEGER NOT NULL,
                max_docx_file_mb INTEGER NOT NULL DEFAULT 10,
                max_docx_total_mb INTEGER NOT NULL DEFAULT 50,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Existing databases may have the original four-column policy table;
        # migrate it before the INSERT below uses the new byte-limit fields.
        for statement in (
            "ALTER TABLE subscription_plan_limits ADD COLUMN max_docx_file_mb INTEGER NOT NULL DEFAULT 10",
            "ALTER TABLE subscription_plan_limits ADD COLUMN max_docx_total_mb INTEGER NOT NULL DEFAULT 50",
        ):
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        cursor.executemany(
            """
            INSERT OR IGNORE INTO chatbot_usage_weights (kind, name, multiplier)
            VALUES (?, ?, ?)
            """,
            (
                ("model", "genius-1", 0.75),
                ("model", "genius-2", 0.875),
                ("model", "genius-3", 1.0),
                ("effort", "low", 0.75),
                ("effort", "medium", 1.0),
                ("effort", "high", 1.5),
            ),
        )
        cursor.executemany(
            """
            INSERT OR IGNORE INTO subscription_plan_limits
                (tier, chat_credits, docx_upload, max_docx_slides,
                 max_docx_file_mb, max_docx_total_mb)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                # Keep first-install defaults aligned with the policy currently
                # managed from the Admin page. INSERT OR IGNORE above ensures
                # existing administrator-edited values remain authoritative.
                ("free", 20, 3, 30, 30, 150),
                ("plus", 50, 10, 50, 50, 250),
                ("ultra", 100, 20, 50, 80, 400),
            ),
        )

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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_user ON chatbot_sessions(user_id, updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_project ON chatbot_sessions(project_id, updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_messages_session ON chatbot_messages(session_id, id DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_documents_user ON chatbot_documents(user_id, updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_documents_status ON chatbot_documents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_session_documents_session ON chatbot_session_documents(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_document_chunks_document ON chatbot_document_chunks(document_id, ordinal)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_citations_message ON chatbot_message_citations(message_id, citation_order)")

        # Add first-class generation choices to databases created before the
        # chatbot model/effort fields were introduced.
        for statement in (
            "ALTER TABLE chatbot_messages ADD COLUMN model TEXT",
            "ALTER TABLE chatbot_messages ADD COLUMN effort TEXT",
            "ALTER TABLE chatbot_documents ADD COLUMN size_bytes INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE chatbot_documents ADD COLUMN chunk_index_version INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE chatbot_documents ADD COLUMN images_json TEXT",
            "ALTER TABLE chatbot_document_chunks ADD COLUMN node_key TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE chatbot_document_chunks ADD COLUMN parent_node_key TEXT",
            "ALTER TABLE chatbot_document_chunks ADD COLUMN node_kind TEXT NOT NULL DEFAULT 'content'",
        ):
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chatbot_document_chunks_tree ON chatbot_document_chunks(document_id, node_key, level)")

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

        # Authorization is persisted per account. Existing databases receive
        # a non-admin default and can then be managed from the admin console
        # after the one-time CLI bootstrap.
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")
        except Exception:
            pass  # Column already exists
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_admin ON users(is_admin)")

        # Migrate usage from the old daily counters to the canonical rolling
        # five-hour window. Existing counters are preserved for the first
        # window, while new writes keep them synchronized for old clients.
        for statement in (
            "ALTER TABLE users ADD COLUMN usage_window_started_at TIMESTAMP",
            "ALTER TABLE users ADD COLUMN chat_usage_5h INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN chat_usage_credits_5h REAL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN chat_messages_5h INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN docx_usage_5h INTEGER DEFAULT 0",
        ):
            try:
                cursor.execute(statement)
            except Exception:
                pass  # Column already exists

        cursor.execute("""
            UPDATE users SET
                usage_window_started_at = COALESCE(usage_window_started_at, datetime('now')),
                chat_usage_5h = CASE
                    WHEN COALESCE(chat_usage_5h, 0) = 0 THEN COALESCE(idea_usage_today, 0)
                    ELSE chat_usage_5h
                END,
                chat_usage_credits_5h = CASE
                    WHEN COALESCE(chat_usage_credits_5h, 0) = 0
                        THEN COALESCE(NULLIF(chat_usage_5h, 0), idea_usage_today, 0)
                    ELSE chat_usage_credits_5h
                END,
                chat_messages_5h = CASE
                    WHEN COALESCE(chat_messages_5h, 0) = 0
                        THEN COALESCE(NULLIF(chat_usage_5h, 0), idea_usage_today, 0)
                    ELSE chat_messages_5h
                END,
                docx_usage_5h = CASE
                    WHEN COALESCE(docx_usage_5h, 0) = 0 THEN COALESCE(docx_usage_today, 0)
                    ELSE docx_usage_5h
                END
        """)

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
