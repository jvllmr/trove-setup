import random

import pytest
from trove_classifiers import sorted_classifiers

from trove_setup.app import TroveSetupApp

from .utils import add_classifier

pytestmark = pytest.mark.asyncio


async def test_add_classifiers(app: TroveSetupApp):
    async with app.run_test() as pilot:
        await add_classifier(app, pilot, random.choice(sorted_classifiers))
