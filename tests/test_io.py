import pytest
import tomli

from trove_setup.app import CLASSIFIER_LIST_GETTERS, TroveSetupApp

from .utils import add_classifier, classifiers_to_test, save_and_quit

pytestmark = pytest.mark.asyncio


def read_classifiers_from_file(app: TroveSetupApp) -> list[str]:
    path, attr = CLASSIFIER_LIST_GETTERS[app.project_type]
    with app.pyproject_path.open("rb") as f:
        content = tomli.load(f)
    target_table = path.search(content)
    classifiers = target_table[attr]
    assert isinstance(classifiers, list)
    return classifiers


@pytest.mark.parametrize(
    ["classifier"], [(classifier,) for classifier in classifiers_to_test]
)
async def test_io(app: TroveSetupApp, classifier: str):
    prev_classifiers = read_classifiers_from_file(app)

    if classifier not in prev_classifiers:
        async with app.run_test() as pilot:
            add_classifier(app, classifier)
            await pilot.pause()
            await save_and_quit(pilot=pilot)
            new_classifiers = read_classifiers_from_file(app)
            assert classifier in new_classifiers
