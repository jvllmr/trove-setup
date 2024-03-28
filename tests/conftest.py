import shutil
from pathlib import Path

import pytest

from trove_setup.app import TroveSetupApp


@pytest.fixture(
    params=[
        Path("./tests/flit/pyproject.toml"),
        Path("./tests/poetry/pyproject.toml"),
        Path("./tests/pep621/pyproject.toml"),
    ]
)
def app(request):
    pyproject_path: Path = request.param
    example_file = Path(str(pyproject_path).rstrip("toml") + "example.toml")
    shutil.copy(example_file, pyproject_path)
    app_ = TroveSetupApp(pyproject_path=pyproject_path)

    yield app_
    pyproject_path.unlink(missing_ok=True)
