import re

from packaging.version import Version
from rich.prompt import Confirm, Prompt
from trove_classifiers import sorted_classifiers

OLDEST_ALLOWED_VERSION = Version("3.8")
PYTHON_VERSION_CLASSIFIER_REGEX = (
    r"Programming Language :: Python :: (?P<version>\d\.\d+)"
)


def find_python_version_classifiers() -> dict[Version, str]:
    res: dict[Version, str] = {}

    for classifier in sorted_classifiers:
        match = re.match(PYTHON_VERSION_CLASSIFIER_REGEX, classifier)
        if match:
            version = Version(match.group("version"))
            if version < OLDEST_ALLOWED_VERSION:
                continue
            res[version] = classifier

    return res


LICENSE_CLASSIFIER_REGEX = r"License :: (?:.+ :: )*(?P<label>.+)"


def find_license_classifiers() -> dict[str, str]:
    res: dict[str, str] = {}

    for classifier in sorted_classifiers:
        match = re.match(LICENSE_CLASSIFIER_REGEX, classifier)
        if match:
            res[match.group("label")] = classifier

    return res


INTENDED_AUDIENCE_CLASSIFIER_REGEX = r"Intended Audience :: (?:.+ :: )*(?P<label>.+)"


def find_intended_audience_classifiers() -> dict[str, str]:
    res: dict[str, str] = {}

    for classifier in sorted_classifiers:
        match = re.match(INTENDED_AUDIENCE_CLASSIFIER_REGEX, classifier)
        if match:
            res[match.group("label")] = classifier

    return res


def run_guided() -> list[str]:
    classifiers: list[str] = []
    python_versions = find_python_version_classifiers()
    python_version_choices = [str(version) for version in python_versions.keys()]

    min_python_version = Prompt.ask(
        "Which is the oldest python version your project supports?",
        choices=python_version_choices,
        default=str(min(python_versions.keys())),
    )
    max_python_version = Prompt.ask(
        "What is the newest python version you tested your project with?",
        choices=python_version_choices,
        default=str(max(python_versions.keys())),
    )
    parsed_min_python_version = Version(min_python_version)
    parsed_max_python_version = Version(max_python_version)
    assert (
        parsed_min_python_version <= parsed_max_python_version
    ), "You min python version cannot be higher than your max python version"
    for version, classifier in python_versions.items():
        if (
            version >= parsed_min_python_version
            and version <= parsed_max_python_version
        ):
            classifiers.append(classifier)

    is_typed = Confirm.ask("Is your project fully typed?")
    if is_typed:
        classifiers.append("Typing :: Typed")
    else:
        is_typing_stub = Confirm.ask(
            "Does your project provide typing stubs for another package?"
        )
        if is_typing_stub:
            classifiers.append("Typing :: Stubs Only")
    licenses = find_license_classifiers()
    what_license = Prompt.ask(
        "What license does your project use?",
        default="MIT License",
        choices=list(licenses.keys()),
    )
    classifiers.append(licenses[what_license])

    audiences = find_intended_audience_classifiers()
    what_audience = Prompt.ask(
        "What audience is your project intended for?",
        choices=list(audiences.keys()),
        default="Developers",
    )
    classifiers.append(audiences[what_audience])

    return classifiers
