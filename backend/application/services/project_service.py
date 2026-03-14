# File: backend/application/services/project_service.py

import re
import zipfile
from typing import List, Dict, Optional, Union
from pathlib import Path
from fastapi import HTTPException
from backend.domain.entities.project import Project, Slide
from backend.domain.ports.project_repository import ProjectRepository
from backend.application.services.conversion_service import ConversionService
from backend.api.schemas.project_schema import ProjectCreate, ProjectUpdate, SlideCreate, SlideUpdate
import logging

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, conversion_service: Optional[ConversionService] = None):
        self.repo = project_repo
        self.conversion_service = conversion_service


    def create_project(self, user_id: int, data: Union[ProjectCreate, dict]) -> int:
        if isinstance(data, ProjectCreate):
            data_dict = data.model_dump()
        else:
            data_dict = data

        return self.repo.create_project(
            user_id=user_id,
            title=data_dict.get("title", "Untitled Project"),
            description=data_dict.get("description"),
            source_type=data_dict.get("source_type", "idea"),
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
        # Logic nghiệp vụ: Kiểm tra quyền sở hữu
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")

        project.metadata = self.repo.get_metadata(project_id) or {}
        
        return project


    def update_project(self, project_id: int, user_id: int, data: Union[ProjectUpdate, dict]) -> None:
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")
        
        # Convert Pydantic to dict
        if isinstance(data, ProjectUpdate):
            update_data = data.model_dump(exclude_unset=True)
        else:
            update_data = data
            
        self.repo.update_project(project_id, **update_data)


    def delete_project(self, project_id: int, user_id: int) -> None:
        project = self.repo.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")
            
        self.repo.delete_project(project_id)


    def create_slide(self, project_id: int, user_id: int, data: Union[SlideCreate, dict]) -> int:
        project = self.repo.get_project(project_id)
        if not project or project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")
        
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
            
        # Check ownership thông qua Project
        project = self.repo.get_project(slide.project_id)
        if not project or project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")
            
        return slide


    def update_slide(self, slide_id: int, user_id: int, data: dict) -> None:
        # Lấy slide hiện tại từ DB (Entity)
        slide = self.repo.get_slide(slide_id)
        if not slide:
             raise HTTPException(status_code=404, detail="Slide not found")

        # Check ownership
        project = self.repo.get_project(slide.project_id)
        if not project or project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

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
        project_id = slide.project_id
        
        self.repo.delete_slide(slide_id)
        
        # Recalculate slide count
        slides = self.repo.get_project_slides(project_id)
        self.repo.update_project(project_id, slide_count=len(slides))


    def extract_slide_index(self, path):
        """
        Extract slide index from filename like:
        slide_10_0.html → 10
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
        output_folder: Path
    ) -> int:
        """
        Import project từ kết quả workflow AI.
        Xử lý giải nén, convert HTML, và lưu vào DB.
        """
        try:
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

            # 3. Handle File Extraction & Conversion
            html_folder = output_folder / "html"
            converted_folder = output_folder / "converted"

            # 4. Insert Slides to DB
            # Ưu tiên lấy file đã convert
            use_converted = converted_folder.exists() and any(converted_folder.iterdir())
            source_dir = converted_folder if use_converted else html_folder
            
            if not source_dir.exists():
                logger.error(f"❌ No source_dir found: {source_dir}")
                return project_id

            html_files = sorted(source_dir.glob("*.html"), key=self.extract_slide_index)
            logger.info(f"📄 Found {len(html_files)} HTML files in {source_dir}")

            for idx, html_file in enumerate(html_files):
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Determine slide type logic
                slide_type = 'content'
                name_lower = html_file.stem.lower()
                if 'intro' in name_lower or idx == 0: slide_type = 'intro'
                elif 'transition' in name_lower: slide_type = 'transition'
                elif 'thank' in name_lower: slide_type = 'thank_you'

                slide = Slide(
                    id=None,
                    project_id=project_id,
                    slide_index=idx,
                    slide_type=slide_type,
                    title=f"Slide {idx + 1}",
                    content_text="", # Có thể để trống hoặc tách text từ HTML nếu cần
                    html_content=html_content,
                    design_settings={}
                )
                self.repo.create_slide(slide)

            # 5. Finalize Project
            self.repo.update_project(
                project_id=project_id,
                slide_count=len(html_files),
                status='completed'
            )
            
            logger.info(f"✅ Imported project {project_id} successfully")
            return project_id

        except Exception as e:
            logger.error(f"Failed to import project: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Không raise exception để tránh crash luồng streaming, trả về 0 hoặc project_id lỗi
            return 0