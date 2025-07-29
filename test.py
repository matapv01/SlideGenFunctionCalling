from src.utils import config

driver = config.initialize_chromedriver()
if not driver:
    raise RuntimeError("Không thể khởi tạo ChromeDriver.")