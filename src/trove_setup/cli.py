import typing as t
from pathlib import Path

import typer

from .app import TConfigType, TroveSetupApp


def cli_main(
    type: t.Annotated[TConfigType, typer.Option()] = "auto",  # type: ignore
    pyproject_path: t.Annotated[Path, typer.Option(dir_okay=True)] = Path(),
) -> None:
    app = TroveSetupApp(pyproject_path=pyproject_path, type_=type)

    app.run()


def run_typer() -> None:
    typer.run(cli_main)
