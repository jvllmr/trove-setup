import pytest

from trove_setup.app import get_classifier_path


@pytest.mark.parametrize(
    ("classifier", "path"),
    [
        ("Typing :: Stubs Only", "Typing"),
        ("Development Status :: 6 - Mature", "Development Status"),
        (
            "Topic :: System :: Systems Administration :: Authentication/Directory :: NIS",
            "Topic :: System :: Systems Administration :: Authentication/Directory",
        ),
        ("Environment :: Console :: Curses", "Environment :: Console"),
    ],
)
def test_get_classifier_path(classifier: str, path: str) -> None:
    assert get_classifier_path(classifier) == path
