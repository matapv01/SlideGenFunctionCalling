from __future__ import annotations

from base import BaseModel
from base import BaseService

from typing import Any
from playwright.async_api import async_playwright


class PlaywrightInput(BaseModel):
    pass

class PlaywrightOutput(BaseModel):

    playwright: Any
    browser: Any
    context: Any

class Playwright(BaseService):

    async def client(self) -> PlaywrightOutput:

        playwright = await async_playwright().__aenter__()

        browser = await playwright.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-extensions",
            "--disable-plugins",
        ])

        context = await browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1
        )

        return PlaywrightOutput(
            playwright=playwright,
            browser=browser,
            context=context
        )
    
