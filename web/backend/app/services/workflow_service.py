"""
Workflow Service - Handle AI-powered DOCX to slides conversion using LangGraph
EXACT COPY logic from main_web.py
"""
import os
import sys
import logging
import tempfile
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for AI workflow operations using LangGraph"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.workflow_available = self._check_workflow_availability()
    
    def _check_workflow_availability(self) -> bool:
        """Check if workflow module is available"""
        try:
            # Add parent directory to path to import workflow
            # project_dir is: N:\slidegen\SlideGenFunctionCalling\web
            # Need to go up 1 level to: N:\slidegen\SlideGenFunctionCalling
            parent_dir = os.path.dirname(self.project_dir)
            
            logger.info(f"project_dir: {self.project_dir}")
            logger.info(f"parent_dir to add: {parent_dir}")
            
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
                logger.info(f"✅ Added to sys.path: {parent_dir}")
            
            # Try to import workflow
            from workflow import main_workflow
            logger.info("✅ LangGraph workflow module available")
            return True
        except ImportError as e:
            logger.warning(f"⚠️ LangGraph workflow not available: {e}")
            logger.warning(f"   sys.path: {sys.path[:3]}...")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking workflow: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if workflow service is available"""
        return self.workflow_available
    
    async def process_docx_with_workflow(
        self, 
        docx_path: str, 
        output_folder: str,
        router_flags: bool = False
    ) -> Optional[str]:
        """
        Process DOCX file using LangGraph AI workflow - EXACT COPY from main_web.py
        
        Args:
            docx_path: Path to DOCX file
            output_folder: Output folder for slides
            router_flags: Enable router flags in workflow
            
        Returns:
            Path to result ZIP file or None if failed
        """
        if not self.workflow_available:
            logger.error("Workflow not available")
            return None
        
        try:
            logger.info(f"🤖 Processing DOCX with AI workflow: {os.path.basename(docx_path)}")
            
            # Load environment variables from backend .env and root .env
            from dotenv import load_dotenv
            backend_env = os.path.join(os.path.dirname(self.project_dir), 'backend', '.env')
            root_env = os.path.join(os.path.dirname(self.project_dir), '.env')
            
            # Load both env files
            if os.path.exists(backend_env):
                load_dotenv(backend_env)
                logger.info(f"Loaded env from: {backend_env}")
            if os.path.exists(root_env):
                load_dotenv(root_env)
                logger.info(f"Loaded env from: {root_env}")
            
            # Verify GEMINI_API_KEY is available
            gemini_key = os.getenv('GEMINI_API_KEY')
            if not gemini_key:
                logger.error("❌ GEMINI_API_KEY not found in environment")
                return None
            else:
                logger.info(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...")
            
            # Import workflow function
            from workflow import main_workflow
            
            # Create temporary workflow directory
            temp_workflow_dir = tempfile.mkdtemp(prefix="slidegen_workflow_")
            logger.info(f"Created temporary workflow directory: {temp_workflow_dir}")
            
            # Pre-create required subdirectories
            subdirs = ["html", "png", "temp_debug", "temp_debug/html", "temp_debug/png"]
            for subdir in subdirs:
                dir_path = os.path.join(temp_workflow_dir, subdir)
                os.makedirs(dir_path, exist_ok=True)
            
            try:
                # Run workflow in temporary directory
                logger.info(f"Running workflow with temp directory: {temp_workflow_dir}")
                result = await main_workflow(
                    router_flags=router_flags,
                    docx_file=docx_path,
                    output_folder=temp_workflow_dir
                )
                
                # Find result ZIP file
                result_zip = self._find_result_zip(result, temp_workflow_dir, output_folder)
                
                if result_zip and os.path.exists(result_zip):
                    logger.info(f"✅ Workflow completed successfully: {result_zip}")
                    return result_zip
                else:
                    logger.error("❌ Workflow did not produce valid output")
                    return None
                    
            finally:
                # Cleanup temporary directory
                try:
                    if os.path.exists(temp_workflow_dir):
                        shutil.rmtree(temp_workflow_dir, ignore_errors=True)
                        logger.info(f"Cleaned up temp directory: {temp_workflow_dir}")
                except Exception as e:
                    logger.warning(f"Could not cleanup temp directory: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error in workflow processing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _find_result_zip(self, result: Any, temp_dir: str, output_folder: str) -> Optional[str]:
        """Find and copy result ZIP file - EXACT COPY from main_web.py"""
        try:
            result_zip = None
            
            # Check if result is a message string
            if isinstance(result, str):
                if "được lưu tại:" in result or "saved at:" in result.lower() or "hoàn thành" in result.lower():
                    # Try to extract path from message
                    import re
                    path_match = re.search(r'(?:được lưu tại:|saved at:|at:)\s*(.+)', result)
                    if path_match:
                        zip_path = path_match.group(1).strip()
                        if os.path.exists(zip_path):
                            logger.info(f"Found zip file from message: {zip_path}")
                            result_zip = zip_path
                
                # If path extraction failed, search for zip files
                if not result_zip:
                    zip_files = [f for f in os.listdir(temp_dir) if f.endswith('.zip')]
                    if zip_files:
                        result_zip = os.path.join(temp_dir, zip_files[0])
                        logger.info(f"Using found zip file: {result_zip}")
                        
            # Last resort: search for any zip files in temp_dir
            if not result_zip:
                zip_files = [f for f in os.listdir(temp_dir) if f.endswith('.zip')]
                if zip_files:
                    result_zip = os.path.join(temp_dir, zip_files[0])
                    logger.info(f"Found zip file in temp dir: {result_zip}")
                else:
                    # Try to create ZIP from html and png contents
                    html_dir = os.path.join(temp_dir, "html")
                    png_dir = os.path.join(temp_dir, "png")
                    
                    if os.path.exists(html_dir):
                        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
                        if html_files:
                            result_zip = os.path.join(temp_dir, "slides.zip")
                            with zipfile.ZipFile(result_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                # Add HTML files
                                for file in html_files:
                                    file_path = os.path.join(html_dir, file)
                                    zipf.write(file_path, f"html/{file}")
                                
                                # Add PNG files if they exist
                                if os.path.exists(png_dir):
                                    png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
                                    for file in png_files:
                                        file_path = os.path.join(png_dir, file)
                                        zipf.write(file_path, f"png/{file}")
                            
                            logger.info(f"Created zip from html/png: {result_zip}")
                        else:
                            logger.error("No HTML files found in workflow output")
                            return None
                    else:
                        logger.error("Workflow did not produce html directory")
                        return None
            
            # Copy to permanent location in output folder
            if result_zip and os.path.exists(result_zip):
                import uuid
                final_zip = os.path.join(output_folder, f"slides_result_{uuid.uuid4().hex[:8]}.zip")
                os.makedirs(output_folder, exist_ok=True)
                shutil.copy2(result_zip, final_zip)
                logger.info(f"Copied result to: {final_zip}")
                return final_zip
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error finding result zip: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """Check workflow service health"""
        try:
            health = {
                "workflow_available": self.workflow_available,
                "can_import": False,
                "langgraph_installed": False
            }
            
            if self.workflow_available:
                try:
                    from workflow import main_workflow
                    health["can_import"] = True
                except Exception as e:
                    health["import_error"] = str(e)
                
                # Check LangGraph installation
                try:
                    import langgraph
                    health["langgraph_installed"] = True
                    health["langgraph_version"] = getattr(langgraph, "__version__", "unknown")
                except ImportError:
                    health["langgraph_installed"] = False
            
            return health
            
        except Exception as e:
            logger.error(f"Workflow health check error: {e}")
            return {
                "workflow_available": False,
                "error": str(e)
            }
