from __future__ import annotations

import typing as t
from collections import defaultdict

from trove_classifiers import sorted_classifiers

STUB_MARKER = "$STUB$"

TTreeNode = t.Dict[str, t.Union["TTreeNode", t.List[str]]]


def _tree_node_factory() -> TTreeNode:
    return defaultdict(dict, ((STUB_MARKER, []),))


def _get_classifiers_tree(classifier: str, tree_node: TTreeNode) -> None:
    parts = [part.strip(" ") for part in classifier.split("::", 1)]
    if len(parts) == 1:
        tree_node[STUB_MARKER].append(parts[0])  # type: ignore
    else:
        node, others = parts
        if node not in tree_node:
            tree_node[node] = _tree_node_factory()
        _get_classifiers_tree(others, tree_node[node])  # type: ignore


def get_classifiers_tree() -> TTreeNode:
    main_tree_node = _tree_node_factory()
    for classifier in sorted_classifiers:
        _get_classifiers_tree(classifier, main_tree_node)
    return main_tree_node


__all__ = ["STUB_MARKER", "get_classifiers_tree", "TTreeNode"]
