from textual.containers import VerticalScroll
from textual.pilot import Pilot

from trove_setup.app import TroveSetupApp, select_option_id


async def add_classifier(app: TroveSetupApp, pilot: Pilot, classifier: str):
    scroll_container = app.query_one("#shop-scroll", VerticalScroll)
    scroll_container.scroll_to(0)
    option_id = select_option_id(classifier)
    await pilot.click(f"#{option_id}")


async def remove_classifier(pilot: Pilot):
    pass


async def remove_classifier_via_selected_section(pilot: Pilot):
    pass
