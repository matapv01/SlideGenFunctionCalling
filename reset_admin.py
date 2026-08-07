import os
import sys

# Add project root to sys.path so we can import backend modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository
from backend.application.services.auth_service import AuthService

def create_admin():
    try:
        repo = SqliteUserRepository()
        auth = AuthService(repo)
        
        email = "admin@slidegen.com"
        password = "password123"
        
        user = repo.get_by_email(email)
        if user:
            print(f"User {email} exists, updating password...")
            new_hashed = auth.get_password_hash(password)
            repo.update_password(user.id, new_hashed)
            print(f"Password updated to: {password}")
        else:
            print(f"Creating new user {email}...")
            auth.register_user(email, "Admin User", password)
            print(f"User created. Email: {email} | Password: {password}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin()
