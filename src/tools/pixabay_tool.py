"""
Pixabay API Tool - Tìm kiếm và lấy hình ảnh/video từ Pixabay
Docs: https://pixabay.com/api/docs/
"""
import requests
from typing import List, Dict, Optional, Literal
import json
import logging

logger = logging.getLogger(__name__)


class PixabayTool:
    """Tool để tìm kiếm và lấy hình ảnh/video từ Pixabay API"""
    
    API_KEY = "54167480-1cbc91f10888131422616cb30"
    IMAGES_API_URL = "https://pixabay.com/api/"
    VIDEOS_API_URL = "https://pixabay.com/api/videos/"
    
    @staticmethod
    def search_images(
        q: str,
        image_type: str = "photo",
        orientation: str = "horizontal",
        per_page: int = 20,
        page: int = 1,
        safesearch: bool = True,
        lang: str = "en",
        category: Optional[str] = None,
        colors: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        order: str = "popular"
    ) -> Dict:
        """
        Tìm kiếm hình ảnh trên Pixabay
        
        Args:
            q: Từ khóa tìm kiếm (tối đa 100 ký tự)
            image_type: Loại hình ảnh - "all", "photo", "illustration", "vector"
            orientation: Hướng ảnh - "all", "horizontal", "vertical"
            per_page: Số kết quả trả về (3-200)
            page: Trang kết quả (phân trang)
            safesearch: Chỉ hiển thị ảnh phù hợp mọi lứa tuổi
            lang: Mã ngôn ngữ (en, vi, etc.)
            category: Lọc theo danh mục (backgrounds, fashion, nature, science, etc.)
            colors: Lọc theo màu (grayscale, transparent, red, orange, yellow, etc.)
            min_width: Chiều rộng tối thiểu
            min_height: Chiều cao tối thiểu
            order: Sắp xếp - "popular" hoặc "latest"
            
        Returns:
            Dict: Kết quả tìm kiếm với total, totalHits, và hits
        """
        params = {
            "key": PixabayTool.API_KEY,
            "q": q,
            "image_type": image_type,
            "orientation": orientation,
            "per_page": per_page,
            "page": page,
            "safesearch": str(safesearch).lower(),
            "lang": lang,
            "order": order
        }
        
        if category:
            params["category"] = category
        if colors:
            params["colors"] = colors
        if min_width > 0:
            params["min_width"] = min_width
        if min_height > 0:
            params["min_height"] = min_height
        
        try:
            response = requests.get(PixabayTool.IMAGES_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Pixabay search: '{q}' - Found {data.get('totalHits', 0)} images")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gọi Pixabay API: {e}")
            return {"total": 0, "totalHits": 0, "hits": []}
    
    @staticmethod
    def search_videos(
        q: str,
        video_type: str = "all",
        per_page: int = 20,
        page: int = 1,
        safesearch: bool = True,
        lang: str = "en",
        category: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        order: str = "popular"
    ) -> Dict:
        """
        Tìm kiếm video trên Pixabay
        
        Args:
            q: Từ khóa tìm kiếm (tối đa 100 ký tự)
            video_type: Loại video - "all", "film", "animation"
            per_page: Số kết quả trả về (3-200)
            page: Trang kết quả
            safesearch: Chỉ hiển thị video phù hợp mọi lứa tuổi
            lang: Mã ngôn ngữ
            category: Lọc theo danh mục
            min_width: Chiều rộng tối thiểu
            min_height: Chiều cao tối thiểu
            order: Sắp xếp - "popular" hoặc "latest"
            
        Returns:
            Dict: Kết quả tìm kiếm với total, totalHits, và hits
        """
        params = {
            "key": PixabayTool.API_KEY,
            "q": q,
            "video_type": video_type,
            "per_page": per_page,
            "page": page,
            "safesearch": str(safesearch).lower(),
            "lang": lang,
            "order": order
        }
        
        if category:
            params["category"] = category
        if min_width > 0:
            params["min_width"] = min_width
        if min_height > 0:
            params["min_height"] = min_height
        
        try:
            response = requests.get(PixabayTool.VIDEOS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Pixabay video search: '{q}' - Found {data.get('totalHits', 0)} videos")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gọi Pixabay Video API: {e}")
            return {"total": 0, "totalHits": 0, "hits": []}
    
    @staticmethod
    def get_image_url_by_quality(image_data: Dict, quality: str = "large") -> str:
        """
        Lấy URL hình ảnh theo chất lượng mong muốn
        
        Args:
            image_data: Dictionary chứa thông tin hình ảnh
            quality: "preview" (150px), "webformat" (640px), "large" (1280px)
            
        Returns:
            str: URL của hình ảnh
        """
        quality_map = {
            "preview": "previewURL",
            "webformat": "webformatURL",
            "large": "largeImageURL"
        }
        
        url_key = quality_map.get(quality, "webformatURL")
        return image_data.get(url_key, "")
    
    @staticmethod
    def search_and_get_best_image(
        query: str,
        orientation: str = "horizontal",
        quality: str = "large",
        image_type: str = "photo"
    ) -> Optional[Dict]:
        """
        Tìm kiếm và trả về thông tin hình ảnh tốt nhất (nhiều downloads nhất)
        
        Args:
            query: Từ khóa tìm kiếm
            orientation: Hướng ảnh mong muốn
            quality: Chất lượng ảnh mong muốn
            image_type: Loại hình ảnh
            
        Returns:
            Optional[Dict]: Thông tin hình ảnh hoặc None nếu không tìm thấy
        """
        result = PixabayTool.search_images(
            q=query,
            orientation=orientation,
            per_page=10,
            image_type=image_type,
            order="popular"
        )
        
        hits = result.get("hits", [])
        if not hits:
            return None
        
        # Lấy ảnh đầu tiên (phổ biến nhất)
        best_image = hits[0]
        
        return {
            "id": best_image.get("id"),
            "url": PixabayTool.get_image_url_by_quality(best_image, quality),
            "pageURL": best_image.get("pageURL"),
            "tags": best_image.get("tags"),
            "user": best_image.get("user"),
            "width": best_image.get("imageWidth"),
            "height": best_image.get("imageHeight"),
            "downloads": best_image.get("downloads"),
            "likes": best_image.get("likes")
        }


# Các hàm wrapper để sử dụng trong function calling

def search_pixabay_images(
    search_query: str,
    image_type: str = "photo",
    orientation: str = "horizontal",
    max_results: int = 20,
    category: Optional[str] = None,
    colors: Optional[str] = None
) -> str:
    """
    Tìm kiếm hình ảnh trên Pixabay
    
    Parameters:
        search_query (str): Từ khóa tìm kiếm bằng tiếng Anh (VD: "business meeting", "technology")
        image_type (str): Loại hình ảnh - "photo", "illustration", hoặc "vector"
        orientation (str): Hướng ảnh - "horizontal", "vertical", hoặc "all"
        max_results (int): Số lượng kết quả tối đa (3-200)
        category (str): Danh mục - backgrounds, fashion, nature, science, education, etc.
        colors (str): Màu sắc - grayscale, transparent, red, orange, yellow, green, etc.
        
    Returns:
        str: JSON string chứa danh sách các hình ảnh tìm được
    """
    tool = PixabayTool()
    result = tool.search_images(
        q=search_query,
        image_type=image_type,
        orientation=orientation,
        per_page=min(max_results, 200),
        category=category,
        colors=colors
    )
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def search_pixabay_videos(
    search_query: str,
    video_type: str = "all",
    max_results: int = 20,
    category: Optional[str] = None
) -> str:
    """
    Tìm kiếm video trên Pixabay
    
    Parameters:
        search_query (str): Từ khóa tìm kiếm bằng tiếng Anh
        video_type (str): Loại video - "all", "film", hoặc "animation"
        max_results (int): Số lượng kết quả tối đa (3-200)
        category (str): Danh mục - backgrounds, fashion, nature, science, education, etc.
        
    Returns:
        str: JSON string chứa danh sách các video tìm được
    """
    tool = PixabayTool()
    result = tool.search_videos(
        q=search_query,
        video_type=video_type,
        per_page=min(max_results, 200),
        category=category
    )
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_best_image_url(
    search_query: str,
    orientation: str = "horizontal",
    image_quality: str = "large",
    image_type: str = "photo"
) -> str:
    """
    Tìm và trả về URL của hình ảnh tốt nhất cho từ khóa
    
    Parameters:
        search_query (str): Từ khóa tìm kiếm
        orientation (str): Hướng ảnh - "horizontal" hoặc "vertical"
        image_quality (str): Chất lượng - "preview", "webformat", hoặc "large"
        image_type (str): Loại hình ảnh - "photo", "illustration", hoặc "vector"
        
    Returns:
        str: URL của hình ảnh hoặc thông báo lỗi
    """
    tool = PixabayTool()
    result = tool.search_and_get_best_image(
        query=search_query,
        orientation=orientation,
        quality=image_quality,
        image_type=image_type
    )
    
    if result:
        return result["url"]
    else:
        return f"Không tìm thấy hình ảnh phù hợp cho '{search_query}'"
