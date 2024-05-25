import pytest
from textual.pilot import Pilot

from .utils import add_classifier

RUN_APP_PATHS = ["./poetry/run_app.py", "./pep621/run_app.py", "./flit/run_app.py"]


@pytest.mark.parametrize(
    argnames=[
        "app_path",
    ],
    argvalues=[[path] for path in RUN_APP_PATHS],
)
def test_default_view(app_path: str, snap_compare):
    assert snap_compare(app_path)


@pytest.mark.parametrize(
    argnames=[
        "app_path",
    ],
    argvalues=[[path] for path in RUN_APP_PATHS],
)
def test_add_classifier_view(app_path: str, snap_compare):
    async def before(pilot: Pilot) -> None:
        classifier = "Environment :: GPU :: NVIDIA CUDA :: 11.8"
        add_classifier(pilot.app, classifier)

    assert snap_compare(app_path, run_before=before)
