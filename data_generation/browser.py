import json
import random
import time
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

ROOT_DIR = Path(__file__).parent.parent


class Browser:
    def __init__(self, headless=True, undetectable=True):
        self.headless = headless
        self.undetectable = undetectable
        self.playwright = None
        self._browser = None
        self.page = None
        self.cookie_path = ROOT_DIR / "tmp" / "cookies.json"
        self.last_request = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self._browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self._browser.new_context(viewport={"width": 1920, "height": 1080})
        self.context.set_default_timeout(10000)
        # Load cookies
        try:
            with open(self.cookie_path, "r") as f:
                cookies = json.loads(f.read())
                self.context.add_cookies(cookies)
        except FileNotFoundError:
            logger.debug("Cookies not found")
        except JSONDecodeError:
            logger.debug("Cookies empty")
        self.page = self.context.new_page()
        if self.undetectable:
            stealth_sync(self.page)
        return self

    def goto(self, url: str, no_wait=False) -> Page:
        if not no_wait:
            long_sleep(self.last_request)
            self.last_request = time.time()
        response = self.page.goto(url, wait_until="domcontentloaded")
        if response.status == 429:
            logger.error(f"429: Too many requests. Failed to load {url}\nSleep 60s")
            if not self.headless:
                logger.info("30s to solve captcha etc.")
                time.sleep(30)
        assert response.ok, f"{response.status} Failed to load: {url}"
        return self.page.content()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Save cookies
        with open(self.cookie_path, "w") as f:
            f.write(json.dumps(self.context.cookies()))
        self.playwright.stop()


def long_sleep(last_request=None, min_duration=10, max_duration=60):
    wait_duration = random.randint(min_duration, max_duration)
    if last_request:
        time_since_last_request = time.time() - last_request
        remaining_sleep_duration = wait_duration - time_since_last_request
        if remaining_sleep_duration > 0:
            logger.debug(f"Wait {wait_duration:.1f} (remaining {remaining_sleep_duration:.1f}s)")
            time.sleep(remaining_sleep_duration)
