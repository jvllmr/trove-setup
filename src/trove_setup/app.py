from __future__ import annotations

import math
import os
import typing as t
from enum import Enum
from pathlib import Path, PurePath

import jmespath
import tomlkit
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.driver import Driver
from textual.widgets import Button, Collapsible, SelectionList
from textual.widgets.selection_list import Selection
from tomlkit import TOMLDocument, items
from trove_classifiers import classifiers as official_classifiers
from trove_classifiers import sorted_classifiers

from .guide import run_guided
from .trove_tree import STUB_MARKER, TTreeNode, get_classifiers_tree


# TODO: replace with literal when typer supports it
class TConfigType(Enum):
    poetry = "poetry"
    flit = "flit"
    pep621 = "pep621"
    auto = "auto"


def remove_invalid_chars(str_: str) -> str:
    return (
        str_.replace(" ", "_")
        .replace(":", "_")
        .replace("-", "_")
        .replace("(", "_")
        .replace(")", "_")
        .replace("/", "_")
        .replace(".", "_")
        .lower()
    )


def selection_list_id(classifier_path: str) -> str:
    return remove_invalid_chars(f"selection_list_{classifier_path}")


def select_option_id(classifier: str) -> str:
    return remove_invalid_chars(f"select_option_{classifier}")


def get_classifier_path(classifier: str) -> str:
    if ":" not in classifier:
        return classifier
    path = ""
    rest = classifier
    while ":" in rest:
        index = rest.index("::")
        path += rest[: index + 3]
        rest = rest[index + 3 :]

    return path.rstrip(": ")


def collapsible_id(classifier_path: str) -> str:
    return f"collapsible_{remove_invalid_chars(classifier_path)}"


def _compose_sub_classifiers(
    tree_node: TTreeNode, path: str, present_classifiers: list[str]
) -> t.Generator[SelectionList[str] | Collapsible, None, None]:
    for key, sub_tree_node in tree_node.items():
        if key == STUB_MARKER:
            continue
        assert isinstance(sub_tree_node, dict)
        classifier_path = path + " :: " + key
        sub_widgets = list(
            _compose_sub_classifiers(
                sub_tree_node,
                classifier_path,
                present_classifiers,
            )
        )

        yield Collapsible(*sub_widgets, title=key, id=collapsible_id(classifier_path))
    selections = [
        Selection(
            (classifier_path := path + " :: " + item),
            classifier_path,
            classifier_path in present_classifiers,
            id=select_option_id(classifier_path),
        )
        for item in tree_node[STUB_MARKER]
    ]
    yield SelectionList(*selections, id=selection_list_id(path))


def compose_classifiers(
    present_classifiers: list[str],
) -> t.Generator[SelectionList[str] | Collapsible, None, None]:
    tree = get_classifiers_tree()
    for key, tree_node in tree.items():
        if key == STUB_MARKER:
            continue
        assert isinstance(tree_node, dict)
        sub_widgets = list(
            _compose_sub_classifiers(tree_node, key, present_classifiers)
        )
        yield Collapsible(*sub_widgets, title=key, id=collapsible_id(key))
    selections = [
        Selection(item, item, item in present_classifiers, id=select_option_id(item))
        for item in tree[STUB_MARKER]
    ]
    selection_list = SelectionList(*selections)

    yield selection_list


def find_pyproject_path(search_base: Path = Path()) -> Path:
    for dirpath, _, filenames in os.walk(str(search_base)):
        if "pyproject.toml" in filenames:
            return Path(dirpath, "pyproject.toml")
    raise RuntimeError(
        "Could not find pyproject.toml in current working directory or subpath"
    )


def classifier_sort_key(classifier: str) -> float | int:
    if classifier in official_classifiers:
        return sorted_classifiers.index(classifier)
    return math.inf


CLASSIFIER_LIST_GETTERS: dict[TConfigType, tuple[jmespath.parser.ParsedResult, str]] = {
    TConfigType.pep621: (jmespath.compile("project"), "classifiers"),
    TConfigType.flit: (jmespath.compile("tool.flit.metadata"), "classifiers"),
    TConfigType.poetry: (jmespath.compile("tool.poetry"), "classifiers"),
}


class TroveSetupApp(App[t.List[str]]):
    DEFAULT_CSS = """
    OptionList {
        max-height: 50vh;
    }

    #selected_classifiers {
        height: 85%;
        max-height: 85%;
    }

    #save_button {
        width: 50vw;
        height: 15%;
    }
    """

    def __init__(
        self,
        driver_class: type[Driver] | None = None,
        css_path: str | PurePath | list[str | PurePath] | None = None,
        watch_css: bool = False,
        pyproject_path: Path = Path(),
        type_: TConfigType = TConfigType.auto,
    ):
        self.pyproject_path = (
            find_pyproject_path(pyproject_path)
            if pyproject_path.is_dir()
            else pyproject_path
        ).absolute()

        with self.pyproject_path.open(mode="rb") as f:
            self.pyproject = tomlkit.load(f)

        if type_ == TConfigType.auto:
            for type_key, path in CLASSIFIER_LIST_GETTERS.items():
                try:
                    self._load_table(self.pyproject, path[0])
                    self.project_type = type_key
                    break
                except KeyError:
                    pass
            else:
                raise KeyError("Could not locate classifiers in pyproject.toml")
        else:
            self.project_type = type_

        present_classifiers = self.read_classifiers()
        if not present_classifiers:
            self.write_classifiers(run_guided())

        super().__init__(driver_class, css_path, watch_css)

    def _load_table(
        self, doc: TOMLDocument, path: jmespath.parser.ParsedResult
    ) -> items.Table:
        table = path.search(doc)
        if table is None:
            raise KeyError(path.expression)
        assert isinstance(table, (items.Table)), type(table)
        return table

    @property
    def table_classifiers_attr(self) -> str:
        return CLASSIFIER_LIST_GETTERS[self.project_type][1]

    @property
    def target_table_path(self) -> jmespath.parser.ParsedResult:
        return CLASSIFIER_LIST_GETTERS[self.project_type][0]

    @property
    def pyproject_target_table(self) -> items.Table:
        return self._load_table(self.pyproject, self.target_table_path)

    def write_classifiers(self, classifiers: list[str]) -> None:
        table = self.pyproject_target_table
        table[self.table_classifiers_attr] = classifiers

    def read_classifiers(self) -> list[str]:
        table = self.pyproject_target_table
        key = self.table_classifiers_attr
        if key not in table:
            table[key] = []
        classifiers = table[key]
        assert isinstance(classifiers, (list, items.Array)), type(classifiers)
        return sorted(classifiers, key=classifier_sort_key)

    def compose(self) -> ComposeResult:
        selected: list[Selection[str]] = []
        present_classifiers = self.read_classifiers()

        for pyproject_classifier in present_classifiers:
            if pyproject_classifier not in official_classifiers:
                continue
            selected.append(
                Selection(
                    pyproject_classifier,
                    pyproject_classifier,
                    True,
                    id=pyproject_classifier,
                )
            )
        collapsibles = list(compose_classifiers(present_classifiers))
        selected_component = SelectionList(*selected, id="selected_classifiers")

        yield Horizontal(
            VerticalScroll(*collapsibles, id="shop-scroll"),
            VerticalScroll(
                selected_component,
                Button("Save & Quit", variant="success", id="save_button"),
                id="selected-classifiers-scroll",
            ),
        )

    def get_result_list(self) -> SelectionList[str]:
        return self.query_one("#selected_classifiers", SelectionList)

    def on_selection_list_selection_toggled(
        self, event: SelectionList.SelectionToggled[str]
    ) -> None:
        result_list = self.get_result_list()
        value = event.selection.value

        if event.selection_list is result_list:
            path = get_classifier_path(value)

            select_list = self.query_one(f"#{selection_list_id(path)}", SelectionList)

            option = select_list.get_option(select_option_id(value))

            select_list.deselect(option)

            if value in result_list._option_ids.keys():
                result_list.remove_option(value)
        else:
            if value not in result_list._option_ids.keys():
                result_list.add_option(Selection(value, value, True, id=value))
            else:
                result_list.remove_option(value)

    @property
    def current_classifiers(self) -> list[str]:
        result_list = self.get_result_list()
        return sorted(result_list.selected, key=classifier_sort_key)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_button":
            array_items_str = (
                f'"{classifier}"' for classifier in self.current_classifiers
            )

            self.write_classifiers(
                tomlkit.array("[" + ",".join(array_items_str) + "]").multiline(True)
            )

            with open(self.pyproject_path, "w") as f:
                tomlkit.dump(self.pyproject, f)
            self.exit(
                result=self.read_classifiers(),
                message=f"New classifiers written to {str(self.pyproject_path)}",
            )
