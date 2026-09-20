from backend.application.services.project_service import ProjectService
from backend.domain.project_name import PROJECT_NAME_MAX_LENGTH, normalize_project_name


class CreateProjectRepository:
    def __init__(self):
        self.created = None

    def create_project(self, **kwargs):
        self.created = kwargs
        return 1


class RenameProjectRepository:
    def __init__(self):
        self.updated = None

    def get_project(self, project_id):
        return object()

    def get_project_role(self, project_id, user_id):
        return "owner"

    def update_project(self, project_id, **kwargs):
        self.updated = (project_id, kwargs)


def test_normalize_project_name_keeps_names_within_product_limit():
    value = normalize_project_name(
        "  A   project title that is deliberately longer than forty characters  "
    )

    assert len(value) == PROJECT_NAME_MAX_LENGTH
    assert value == "A project title that is deliberately lon"


def test_project_service_normalizes_created_and_renamed_projects():
    long_name = "A project title that is deliberately longer than forty characters"

    create_repo = CreateProjectRepository()
    ProjectService(create_repo).create_project(7, {"title": long_name})
    assert create_repo.created["title"] == "A project title that is deliberately lon"

    rename_repo = RenameProjectRepository()
    ProjectService(rename_repo).update_project(3, 7, {"title": long_name})
    assert rename_repo.updated == (3, {"title": "A project title that is deliberately lon"})
