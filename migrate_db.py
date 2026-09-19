# Database Migration Script
# Add this to fix existing database schema

import sqlite3
import os

def migrate_database():
    """Migrate existing database to add subscription fields"""
    db_path = os.getenv(
        "SLIDEGEN_DATABASE_PATH",
        "backend/infrastructure/database/slidegen.db",
    )

    if not os.path.exists(db_path):
        print("Database not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if subscription columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        migrations = []
        if "subscription_tier" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'")

        if "subscription_expires_at" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP")

        if "daily_usage_reset_date" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN daily_usage_reset_date DATE DEFAULT CURRENT_DATE")

        if "idea_usage_today" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN idea_usage_today INTEGER DEFAULT 0")

        if "docx_usage_today" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN docx_usage_today INTEGER DEFAULT 0")

        if "usage_window_started_at" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN usage_window_started_at TIMESTAMP")

        if "chat_usage_5h" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN chat_usage_5h INTEGER DEFAULT 0")

        if "chat_usage_credits_5h" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN chat_usage_credits_5h REAL DEFAULT 0")

        if "chat_messages_5h" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN chat_messages_5h INTEGER DEFAULT 0")

        if "docx_usage_5h" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN docx_usage_5h INTEGER DEFAULT 0")

        if "is_admin" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")

        # Run migrations
        for migration in migrations:
            print(f"Running: {migration}")
            cursor.execute(migration)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_admin ON users(is_admin)")

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
        cursor.execute("PRAGMA table_info(subscription_plan_limits)")
        plan_columns = [column[1] for column in cursor.fetchall()]
        for column, definition in (
            ("max_docx_file_mb", "INTEGER NOT NULL DEFAULT 10"),
            ("max_docx_total_mb", "INTEGER NOT NULL DEFAULT 50"),
        ):
            if column not in plan_columns:
                migration = f"ALTER TABLE subscription_plan_limits ADD COLUMN {column} {definition}"
                print(f"Running: {migration}")
                cursor.execute(migration)
        cursor.executemany(
            """
            INSERT OR IGNORE INTO subscription_plan_limits
                (tier, chat_credits, docx_upload, max_docx_slides,
                 max_docx_file_mb, max_docx_total_mb)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                # Bootstrap values are only for a database that has never
                # received an admin policy. Existing rows are preserved by
                # INSERT OR IGNORE; runtime changes always come from Admin.
                ("free", 20, 3, 30, 30, 150),
                ("plus", 50, 10, 50, 50, 250),
                ("ultra", 100, 20, 50, 80, 400),
            ),
        )

        # Persist the original upload size for the conversation-wide DOCX cap.
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'chatbot_documents'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(chatbot_documents)")
            document_columns = [column[1] for column in cursor.fetchall()]
            if "size_bytes" not in document_columns:
                migration = "ALTER TABLE chatbot_documents ADD COLUMN size_bytes INTEGER NOT NULL DEFAULT 0"
                print(f"Running: {migration}")
                cursor.execute(migration)
            if "images_json" not in document_columns:
                migration = "ALTER TABLE chatbot_documents ADD COLUMN images_json TEXT"
                print(f"Running: {migration}")
                cursor.execute(migration)

        conn.commit()
        print(f"Migration completed. {len(migrations)} columns added.")

        # Check users
        cursor.execute("SELECT id, email, subscription_tier FROM users")
        users = cursor.fetchall()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user[1]} (ID: {user[0]}, Tier: {user[2]})")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
