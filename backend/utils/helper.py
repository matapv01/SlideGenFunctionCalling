import shutil
from pathlib import Path

def clear_temp_dir(temp_dir: Path):
    """Clear temporary directory"""
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
               print(f"Could not remove {item}: {e}")