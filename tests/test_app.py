import pytest
from textual.widgets import SelectionList

from trove_setup.app import TroveSetupApp, get_classifier_path, selection_list_id

from .utils import (
    add_classifier,
    classifiers_to_test,
    remove_classifier,
    remove_classifier_via_result_list,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    ["classifier"], [(classifier,) for classifier in classifiers_to_test]
)
async def test_add_classifiers(app: TroveSetupApp, classifier: str):
    async with app.run_test() as pilot:
        already_in = classifier in app.current_classifiers

        old_count = len(app.current_classifiers)
        add_classifier(app, classifier)
        await pilot.pause()
        assert classifier in app.current_classifiers
        if already_in:
            assert len(app.current_classifiers) == old_count
        else:
            assert len(app.current_classifiers) == old_count + 1


@pytest.mark.parametrize(
    ["classifier"], [(classifier,) for classifier in classifiers_to_test]
)
async def test_remove_classifiers(app: TroveSetupApp, classifier: str):
    async with app.run_test() as pilot:
        was_not_in = classifier not in app.current_classifiers
        old_count = len(app.current_classifiers)
        if old_count == 0:
            return
        remove_classifier(app, classifier)
        await pilot.pause()
        assert classifier not in app.current_classifiers
        if was_not_in:
            assert len(app.current_classifiers) == old_count
        else:
            assert len(app.current_classifiers) == old_count - 1


@pytest.mark.parametrize(
    ["classifier"], [(classifier,) for classifier in classifiers_to_test]
)
async def test_remove_via_result_list_classifiers(app: TroveSetupApp, classifier: str):
    async with app.run_test() as pilot:
        old_count = len(app.current_classifiers)
        was_not_in = classifier not in app.current_classifiers
        selection_list = app.query_one(
            f"#{selection_list_id(get_classifier_path(classifier))}", SelectionList
        )
        if old_count == 0:
            return
        remove_classifier_via_result_list(app, classifier)
        await pilot.pause()
        assert classifier not in selection_list.selected
        assert classifier not in app.current_classifiers
        if was_not_in:
            assert len(app.current_classifiers) == old_count
        else:
            assert len(app.current_classifiers) == old_count - 1
