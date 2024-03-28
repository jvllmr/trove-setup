import pytest

RUN_APP_PATHS = ["./poetry/run_app.py", "./pep621/run_app.py", "./flit/run_app.py"]


@pytest.mark.parametrize(
    argnames=[
        "app_path",
    ],
    argvalues=[[path] for path in RUN_APP_PATHS],
)
def test_default_view(app_path: str, snap_compare):
    assert snap_compare(app_path)
