from pathlib import Path

import pytest

from data_generation.browser import Browser


@pytest.mark.skip(reason="Check stealth browser, only for manual testing")
@pytest.mark.parametrize(
    "url, filename",
    [
        ("https://bot.sannysoft.com/", "bot_sannysoft.png"),
        ("https://hmaker.github.io/selenium-detector/", "selenium_detector.png"),
    ],
)
def test_playwright_stealth(url, filename):
    with Browser(headless=True, undetectable=True) as browser:
        browser.goto(url, no_wait=True)
        browser.page.screenshot(path=Path("tmp") / filename, full_page=True)

    assert Path(filename).exists()
