PROJECT_NAME_MAX_LENGTH = 40


def normalize_project_name(value: str | None, fallback: str = "Untitled Project") -> str:
    """Return the compact, user-visible project name used across workflows."""
    name = " ".join(str(value or "").split()).strip()
    fallback_name = " ".join(str(fallback or "").split()).strip() or "Project"
    return (name or fallback_name)[:PROJECT_NAME_MAX_LENGTH].rstrip() or "Project"
