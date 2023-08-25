import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def root_directory(request):
    """Change to the root directory for the duration of the tests."""
    old_cwd = Path.cwd()
    os.chdir(request.config.rootdir)
    try:
        yield
        assert Path.cwd() == request.config.rootdir, "Test changed working directory"
    finally:
        os.chdir(old_cwd)
