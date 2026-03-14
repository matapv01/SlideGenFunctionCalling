# Database Migration Script
# Add this to fix existing database schema

import sqlite3
import os

def migrate_database():
    """Migrate existing database to add subscription fields"""
    db_path = "backend/infrastructure/database/slidegen.db"

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

        # Run migrations
        for migration in migrations:
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