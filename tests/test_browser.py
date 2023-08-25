import os
import tempfile
from pathlib import Path

import pytest

from data_generation.browser import Browser


@pytest.fixture
def temporary_html():
    html = "<html><body><h1>Test</h1></body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        f.close()
        yield Path(f.name)
    os.remove(f.name)


def test_playwright(temporary_html):
    url = temporary_html.absolute().as_uri()

    with Browser() as browser:
        res = browser.goto(url, no_wait=True)

    assert isinstance(res, str)
    assert "Test" in res
