import shutil
from pathlib import Path

import pytest

from trove_setup.app import TroveSetupApp


@pytest.fixture(
    params=[
        Path("./tests/flit/"),
        Path("./tests/poetry/"),
        Path("./tests/pep621/"),
    ]
)
def app(request, tmp_path: Path):
    pyproject_path: Path = request.param / "pyproject.toml"
    target_path = tmp_path / "pyproject.toml"
    shutil.copy(pyproject_path, target_path)
    app_ = TroveSetupApp(pyproject_path=target_path)

    yield app_
