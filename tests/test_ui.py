from pathlib import Path

import pytest
from textual.pilot import Pilot

from .utils import add_classifier

FILE_DIR = Path(__file__).parent
RUN_APP_PATHS = [
    FILE_DIR / "poetry/run_app.py",
    FILE_DIR / "pep621/run_app.py",
    FILE_DIR / "flit/run_app.py",
]


@pytest.mark.parametrize(
    argnames=[
        "app_path",
    ],
    argvalues=[[path] for path in RUN_APP_PATHS],
)
def test_default_view(app_path: Path, snap_compare, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(app_path.parent)
    assert snap_compare(app_path)


@pytest.mark.parametrize(
    argnames=[
        "app_path",
    ],
    argvalues=[[path] for path in RUN_APP_PATHS],
)
def test_add_classifier_view(
    app_path: Path, snap_compare, monkeypatch: pytest.MonkeyPatch
):
    async def before(pilot: Pilot) -> None:
        classifier = "Environment :: GPU :: NVIDIA CUDA :: 11.8"
        add_classifier(pilot.app, classifier)

    monkeypatch.chdir(app_path.parent)

    assert snap_compare(app_path, run_before=before)
