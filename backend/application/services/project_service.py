# File: backend/application/services/project_service.py

import re
import zipfile
from typing import List, Union
from pathlib import Path
from fastapi import HTTPException
from backend.domain.entities.project import Project, Slide
from backend.domain.project_name import normalize_project_name
from backend.domain.ports.project_repository import ProjectRepository
from backend.api.schemas.project_schema import ProjectCreate, ProjectUpdate, SlideCreate, SlideUpdate
import logging

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, project_repo: ProjectRepository):
        self.repo = project_repo

    def get_project_role(self, project_id: int, user_id: int) -> str | None:
        return self.repo.get_project_role(project_id, user_id)

    def require_project_access(self, project_id: int, user_id: int, minimum_role: str = "viewer") -> str:
        """Check project membership and return the effective role."""
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        role = self.repo.get_project_role(project_id, user_id)
        if role is None:
            raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập dự án này")
        role_rank = {"viewer": 1, "editor": 2, "owner": 3}
        if role_rank.get(role, 0) < role_rank.get(minimum_role, 1):
            raise HTTPException(status_code=403, detail="Bạn không có quyền chỉnh sửa dự án này")
        return role


    def create_project(self, user_id: int, data: Union[ProjectCreate, dict]) -> int:
        if isinstance(data, ProjectCreate):
            data_dict = data.model_dump()
        else:
            data_dict = data

        return self.repo.create_project(
            user_id=user_id,
            title=normalize_project_name(data_dict.get("title")),
            description=data_dict.get("description"),
            source_type=data_dict.get("source_type", "manual"),
            source_data=data_dict.get("source_data")
        )


    def get_user_projects(self, user_id: int, limit: int, offset: int) -> List[Project]:
        return self.repo.get_user_projects(user_id, limit, offset)


    def get_project_slides_by_name(self, project_name: str) -> tuple[int, List[Slide]]:
        # Logic nghiệp vụ: Tìm project theo tên, sau đó lấy slides
        projects = self.repo.get_all_projects()
        project = next((p for p in projects if p.title == project_name), None)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        slides = self.repo.get_project_slides(project.id)
        if not slides:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy slide cho dự án: {project_name}")
        return project.id, slides


    def get_project_details(self, project_id: int, user_id: int) -> Project:
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")

        role = self.require_project_access(project_id, user_id)
        project.metadata = self.repo.get_metadata(project_id) or {}
        project.metadata["access_role"] = role
        
        return project


    def update_project(self, project_id: int, user_id: int, data: Union[ProjectUpdate, dict]) -> None:
        self.require_project_access(project_id, user_id, "editor")
        
        # Convert Pydantic to dict
        if isinstance(data, ProjectUpdate):
            update_data = data.model_dump(exclude_unset=True)
        else:
            update_data = data

        if update_data.get("title") is not None:
            update_data = {**update_data, "title": normalize_project_name(update_data["title"])}
            
        self.repo.update_project(project_id, **update_data)


    def delete_project(self, project_id: int, user_id: int) -> None:
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Chỉ chủ sở hữu mới có thể xóa dự án")
            
        self.repo.delete_project(project_id)


    def create_slide(self, project_id: int, user_id: int, data: Union[SlideCreate, dict]) -> int:
        self.require_project_access(project_id, user_id, "editor")
        
        if isinstance(data, SlideCreate):
            data_dict = data.model_dump()
        else:
            data_dict = data

        new_slide = Slide(
            id=None,
            project_id=project_id,
            slide_index=data_dict.get("slide_index", 0),
            slide_type=data_dict.get("slide_type", "content"),
            title=data_dict.get("title", "Untitled"),
            content_text=data_dict.get("content_text", ""),
            html_content=data_dict.get("html_content", ""),
            design_settings=data_dict.get("design_settings", {})
        )
        
        slide_id = self.repo.create_slide(new_slide)
        
        # Update slide count logic
        slides = self.repo.get_project_slides(project_id)
        self.repo.update_project(project_id, slide_count=len(slides))
        
        return slide_id


    def get_slide(self, slide_id: int, user_id: int) -> Slide:
        slide = self.repo.get_slide(slide_id)
        if not slide:
            raise HTTPException(status_code=404, detail="Không tìm thấy slide")
            
        self.require_project_access(slide.project_id, user_id)
            
        return slide


    def update_slide(self, slide_id: int, user_id: int, data: dict) -> None:
        # Lấy slide hiện tại từ DB (Entity)
        slide = self.repo.get_slide(slide_id)
        if not slide:
             raise HTTPException(status_code=404, detail="Slide not found")

        self.require_project_access(slide.project_id, user_id, "editor")

        # Merge data vào Entity
        if isinstance(data, SlideUpdate):
            update_data = data.model_dump(exclude_unset=True)
        else:
            update_data = data
            
        if 'title' in update_data: slide.title = update_data['title']
        if 'html_content' in update_data: slide.html_content = update_data['html_content']
        if 'content_text' in update_data: slide.content_text = update_data['content_text']
        if 'design_settings' in update_data: slide.design_settings = update_data['design_settings']
        if 'slide_index' in update_data: slide.slide_index = update_data['slide_index']
        if 'slide_type' in update_data: slide.slide_type = update_data['slide_type']
        # Lưu lại vào DB
        self.repo.update_slide(slide)

    def delete_slide(self, slide_id: int, user_id: int) -> None:
        slide = self.get_slide(slide_id, user_id) # Check exist & ownership
        self.require_project_access(slide.project_id, user_id, "editor")
        project_id = slide.project_id
        
        self.repo.delete_slide(slide_id)
        
        # Recalculate slide count
        slides = self.repo.get_project_slides(project_id)
        self.repo.update_project(project_id, slide_count=len(slides))


    def extract_slide_index(self, path):
        """
        Extract slide index from filename like:
        slide_10_0.xml → 10
        """
        match = re.search(r"slide_(\d+)", path.stem)
        return int(match.group(1)) if match else float("inf")


    def import_project_from_workflow(
        self,
        user_id: int,
        project_name: str,
        source_type: str,
        source_data: dict,
        slide_options: dict,
        output_folder: Path | str,
    ) -> int:
        """
        Import project từ kết quả XML workflow AI.
        Lưu các XML slide vào DB.
        """
        try:
            project_name = normalize_project_name(project_name)
            # Workflow adapters may return either a ``Path`` or its serialized
            # string form. Normalize at this application boundary so every
            # caller uses the same filesystem contract below.
            output_folder = Path(output_folder)
            if str((slide_options or {}).get("output_format", "xml")).lower() != "xml":
                raise ValueError("This workflow is XML-only; output_format must be 'xml'.")

            # 1. Create Project
            project_id = self.repo.create_project(
                user_id=user_id,
                title=project_name,
                description=source_data.get('description', ''),
                source_type=source_type,
                source_data=source_data
            )

            # 2. Save Metadata
            self.repo.save_metadata(
                project_id=project_id,
                slide_options=slide_options,
                workflow_config={},
                generation_params={}
            )

            if str((slide_options or {}).get("output_format", "xml")).lower() == "xml":
                sub_output = output_folder / "output"
                base = sub_output if sub_output.exists() else output_folder
                xml_folder = base / "xml"
                xml_files = sorted(xml_folder.glob("*.xml"), key=self.extract_slide_index)
                logger.info(f"Found {len(xml_files)} XML files in {xml_folder}")

                for idx, xml_file in enumerate(xml_files):
                    with open(xml_file, "r", encoding="utf-8") as file:
                        xml_content = file.read()

                    slide = Slide(
                        id=None,
                        project_id=project_id,
                        slide_index=idx,
                        slide_type="intro" if idx == 0 else "content",
                        title=f"Slide {idx + 1}",
                        content_text="",
                        # The current DB schema stores the editable payload in
                        # html_content; design_settings carries its format.
                        html_content=xml_content,
                        design_settings={"format": "xml", "source_file": xml_file.name},
                    )
                    self.repo.create_slide(slide)

                self.repo.update_project(
                    project_id=project_id,
                    slide_count=len(xml_files),
                    status="completed",
                )
                logger.info(f"Imported XML project {project_id} successfully")
                return project_id

            logger.warning("XML output directory was not found; project imported without slides")
            self.repo.update_project(project_id, slide_count=0, status="completed")
            return project_id

        except Exception as e:
            logger.error(f"Failed to import project: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Không raise exception để tránh crash luồng streaming, trả về 0 hoặc project_id lỗi
            return 0
