import json
import tempfile
import unittest
from pathlib import Path

from backend.domain.entities.user import User
from backend.infrastructure.database import connection
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository


class OnboardingPersistenceTests(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory(prefix="slidegen-onboarding-")
        self._original_database_path = connection.DATABASE_PATH
        connection.DATABASE_PATH = str(Path(self._temporary_directory.name) / "onboarding.db")
        connection.init_db()

    def tearDown(self):
        connection.DATABASE_PATH = self._original_database_path
        self._temporary_directory.cleanup()

    def test_new_account_stays_pending_until_answers_are_saved(self):
        repo = SqliteUserRepository()
        new_user = repo.create(
            User(id=None, email="new@example.com", hashed_password="hash", onboarding_completed=False)
        )
        self.assertFalse(new_user.onboarding_completed)
        connection.init_db()  # A restart must not mark an unfinished account complete.
        self.assertFalse(repo.get_by_email("new@example.com").onboarding_completed)

        repo.complete_onboarding(new_user.id, ["work", "reports"], "professional")
        self.assertTrue(repo.get_by_id(new_user.id).onboarding_completed)
        with connection.get_db_connection() as conn:
            saved = conn.execute(
                "SELECT onboarding_use_cases, onboarding_role FROM users WHERE id = ?",
                (new_user.id,),
            ).fetchone()
        self.assertEqual(json.loads(saved["onboarding_use_cases"]), ["work", "reports"])
        self.assertEqual(saved["onboarding_role"], "professional")

    def test_existing_account_defaults_to_completed_onboarding(self):
        with connection.get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
                ("existing@example.com", "hash"),
            )
            conn.commit()

        self.assertTrue(SqliteUserRepository().get_by_email("existing@example.com").onboarding_completed)


if __name__ == "__main__":
    unittest.main()
