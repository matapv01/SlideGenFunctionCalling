"""One browser on a dedicated asyncio thread for synchronous GRPO rewards."""
from __future__ import annotations

import atexit
import asyncio
import os
import warnings
from concurrent.futures import Future
from pathlib import Path
from queue import Queue
from threading import Lock, Thread

from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider


class RenderRuntime:
    def __init__(self):
        self._tasks = Queue()
        self._browser = None
        self._playwright = None
        self._capture = PlaywrightCaptureProvider()
        self._thread = Thread(target=self._serve, name="grpo-render", daemon=True)
        self._thread.start()

    def submit(self, xmls, paths, script, workers):
        future = Future()
        self._tasks.put((xmls, paths, script, workers, future))
        return future

    def close(self):
        self._tasks.put(None)
        self._thread.join(timeout=30)
        if self._thread.is_alive():
            warnings.warn("GRPO render thread did not stop within 30 seconds")

    def _serve(self):
        with asyncio.Runner() as runner:
            try:
                while (task := self._tasks.get()) is not None:
                    xmls, paths, script, workers, future = task
                    if not future.set_running_or_notify_cancel():
                        continue
                    try:
                        future.set_result(runner.run(self._render(xmls, paths, script, workers)))
                    except BaseException as exc:
                        future.set_exception(exc)
            finally:
                runner.run(self._shutdown())

    async def _shutdown(self):
        browser, playwright = self._browser, self._playwright
        self._browser = self._playwright = None
        try:
            if browser is not None:
                await browser.close()
        finally:
            if playwright is not None:
                await playwright.stop()

    async def _ensure_browser(self):
        if self._browser is not None and self._browser.is_connected():
            return
        await self._shutdown()
        from playwright.async_api import async_playwright
        options = {"headless": True, "args": ["--disable-gpu", "--disable-software-rasterizer"]}
        executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        if executable:
            path = Path(executable).expanduser()
            if not path.is_file():
                raise FileNotFoundError(f"Configured Chromium not found: {path}")
            options["executable_path"] = str(path)
        self._playwright = await async_playwright().start()
        try:
            self._browser = await self._playwright.chromium.launch(**options)
        except BaseException:
            await self._shutdown()
            raise

    async def _render(self, xmls, paths, script, workers):
        await self._ensure_browser()
        semaphore = asyncio.Semaphore(max(1, workers))
        timeout = max(1.0, float(os.getenv("RL_RENDER_TIMEOUT_SECONDS", "60")))

        async def render_one(xml, path):
            destination = Path(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            page = await self._browser.new_page(
                viewport=self._capture.viewport,
                device_scale_factor=self._capture.device_scale_factor,
            )
            try:
                await self._capture._prepare_xml_preview_page(page, xml, 0, wait_images=True)
                metrics = await page.evaluate(script)
                await page.screenshot(path=str(destination), full_page=False, clip={
                    "x": 0, "y": 0,
                    "width": self._capture.viewport["width"],
                    "height": self._capture.viewport["height"],
                })
                return metrics
            finally:
                await page.close()

        async def slot(xml, path):
            async with semaphore:
                return await asyncio.wait_for(render_one(xml, path), timeout=timeout)

        # Wait for all page cleanup even if one sample fails. No orphan tasks
        # are left suspended between Runner.run calls or during model training.
        results = await asyncio.gather(
            *(slot(xml, path) for xml, path in zip(xmls, paths, strict=True)),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, BaseException):
                raise result
        return results


_RUNTIME = None
_RUNTIME_LOCK = Lock()


def render_batch(xmls, paths, script, workers):
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is None:
            _RUNTIME = RenderRuntime()
        future = _RUNTIME.submit(xmls, paths, script, workers)
    return future.result()


def close_render_runtime():
    global _RUNTIME
    with _RUNTIME_LOCK:
        runtime, _RUNTIME = _RUNTIME, None
    if runtime is not None:
        runtime.close()


atexit.register(close_render_runtime)
