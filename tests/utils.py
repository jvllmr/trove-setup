from textual.pilot import Pilot
from textual.widgets import Collapsible, SelectionList
from trove_classifiers import sorted_classifiers

from trove_setup.app import (
    TroveSetupApp,
    collapsible_id,
    get_classifier_path,
    select_option_id,
    selection_list_id,
)


async def open_collapsible(app: TroveSetupApp, pilot: Pilot, classifier: str):
    classifier_parts = [part.strip(" ") for part in classifier.split("::")]
    for part_index in range(1, len(classifier_parts)):
        path = " :: ".join(classifier_parts[:part_index])
        id_ = collapsible_id(path)
        collapsible = app.query_one(f"#{id_}", Collapsible)
        collapsible.collapsed = False
        await pilot.wait_for_scheduled_animations()


def add_classifier(app: TroveSetupApp, classifier: str):
    option_id = select_option_id(classifier)
    selection_list = app.query_one(
        f"#{selection_list_id(get_classifier_path(classifier))}", SelectionList
    )

    if classifier not in selection_list.selected:
        selection_list.toggle(selection_list.get_option(option_id))


def remove_classifier(app: TroveSetupApp, classifier: str):
    option_id = select_option_id(classifier)
    selection_list = app.query_one(
        f"#{selection_list_id(get_classifier_path(classifier))}", SelectionList
    )

    if classifier in selection_list.selected:
        selection_list.toggle(selection_list.get_option(option_id))


def remove_classifier_via_result_list(app: TroveSetupApp, classifier: str):
    result_list = app.get_result_list()
    if classifier in result_list.selected:
        result_list.toggle(result_list.get_option(classifier))


async def save_and_quit(pilot: Pilot):
    await pilot.click("#save_button")


classifiers_to_test = sorted_classifiers[::30]
