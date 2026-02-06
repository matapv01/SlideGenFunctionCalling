"""
Translation Tool - Dịch tiếng Việt sang tiếng Anh
Không cần cài package thêm, chỉ dùng requests có sẵn
"""

import requests
from functools import lru_cache
from typing import Optional
import urllib.parse


class TranslateTool:
    """
    Tool dịch văn bản sử dụng nhiều API miễn phí
    Không cần API key, không giới hạn (có fallback)
    """
    
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @lru_cache(maxsize=1000)
    def translate(self, text: str, source: str = 'vi', target: str = 'en') -> str:
        """
        Dịch văn bản với nhiều API fallback
        
        Args:
            text: Văn bản cần dịch
            source: Ngôn ngữ nguồn (mặc định 'vi')
            target: Ngôn ngữ đích (mặc định 'en')
        
        Returns:
            Văn bản đã dịch
        """
        if not text or not text.strip():
            return text
        
        # Thử các API theo thứ tự ưu tiên
        apis = [
            self._translate_google,
            self._translate_libretranslate,
            self._translate_mymemory,
        ]
        
        for api_func in apis:
            try:
                result = api_func(text, source, target)
                if result and result.strip() and result != text:
                    return result
            except Exception as e:
                print(f"Translation API failed: {api_func.__name__} - {e}")
                continue
        
        # Nếu tất cả đều fail, trả về text gốc
        return text
    
    def _translate_google(self, text: str, source: str, target: str) -> Optional[str]:
        """
        Google Translate (unofficial API - miễn phí, không giới hạn)
        """
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': source,
            'tl': target,
            'dt': 't',
            'q': text
        }
        
        response = self.session.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        if result and len(result) > 0 and len(result[0]) > 0:
            translated = ''.join([item[0] for item in result[0] if item[0]])
            return translated
        
        return None
    
    def _translate_libretranslate(self, text: str, source: str, target: str) -> Optional[str]:
        """
        LibreTranslate (free, open source)
        """
        url = "https://libretranslate.de/translate"
        payload = {
            'q': text,
            'source': source,
            'target': target,
            'format': 'text'
        }
        
        response = self.session.post(url, json=payload, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return data.get('translatedText')
    
    def _translate_mymemory(self, text: str, source: str, target: str) -> Optional[str]:
        """
        MyMemory Translation API (free, có giới hạn 1000 req/day)
        """
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f'{source}|{target}'
        }
        
        response = self.session.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get('responseStatus') == 200:
            return data.get('responseData', {}).get('translatedText')
        
        return None
    
    def translate_vi_to_en(self, text: str) -> str:
        """
        Shortcut: Dịch tiếng Việt sang tiếng Anh
        """
        return self.translate(text, source='vi', target='en')
    
    def clear_cache(self):
        """Xóa cache dịch"""
        self.translate.cache_clear()
        self.cache.clear()


# Singleton instance
_translator = None

def get_translator() -> TranslateTool:
    """Lấy translator instance (singleton)"""
    global _translator
    if _translator is None:
        _translator = TranslateTool()
    return _translator
