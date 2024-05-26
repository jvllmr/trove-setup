[![PyPI - Downloads](https://img.shields.io/pypi/dd/trove-setup)](https://pypi.org/p/trove-setup)
[![GitHub license](https://img.shields.io/github/license/jvllmr/trove-setup)](https://github.com/jvllmr/trove-setup/blob/dev/LICENSE)
[![Routine Checks](https://github.com/jvllmr/sqlalchemy-sessionload/actions/workflows/test.yaml/badge.svg)](https://github.com/jvllmr/trove-setup/actions/workflows/test.yaml)

# trove-setup

A simple TUI for adding trove classifiers to your project.
Supports `pep621`, `poetry` and `flit` pyproject.toml files.

![trove-setup demo](demo/demo.gif)

## Installation and usage

Optimal installation with `pipx`:

```shell
pipx install trove-setup
```

Run in your project via

```shell
trove_setup
```

## CLI Params

```
trove_setup
    --pyproject-path: Path to pyproject.toml file. Can be directory or file.
    --type: Type of project. Can be one of pep621, poetry, flit, auto.
```
