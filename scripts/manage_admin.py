"""Bootstrap and inspect persisted SlideGen admin roles.

Normal role changes happen in the Admin page. This command exists only for
the one-time bootstrap when a database has no admin yet, so authorization does
not need a hidden environment-variable allowlist.

Examples:
    python scripts/manage_admin.py list
    python scripts/manage_admin.py grant admin@example.com
    python scripts/manage_admin.py revoke user@example.com
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.infrastructure.database.connection import init_db  # noqa: E402
from backend.infrastructure.database.repositories.sqlite_user_repo import (  # noqa: E402
    SqliteUserRepository,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage persisted SlideGen admin roles")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List current admin accounts")
    for command in ("grant", "revoke"):
        command_parser = subparsers.add_parser(command, help=f"{command.title()} admin access")
        command_parser.add_argument("email", help="Target account email")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    init_db()
    repository = SqliteUserRepository()

    if args.command == "list":
        admins = [
            row["email"]
            for row in repository.list_admin_users()
            if row.get("is_admin")
        ]
        print("\n".join(admins) if admins else "No admin accounts.")
        return 0

    user = repository.get_by_email(args.email.strip().lower())
    if user is None:
        print(f"User not found: {args.email}", file=sys.stderr)
        return 1

    should_be_admin = args.command == "grant"
    if not should_be_admin and user.is_admin and repository.count_admin_users() <= 1:
        print("Cannot revoke the last admin account.", file=sys.stderr)
        return 1

    if not repository.set_admin_status(int(user.id), should_be_admin):
        print("Unable to update admin role.", file=sys.stderr)
        return 1

    action = "Granted" if should_be_admin else "Revoked"
    print(f"{action} admin access for {user.email}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
