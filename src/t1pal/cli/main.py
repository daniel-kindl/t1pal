"""The `t1pal` command.

The command has no subcommands yet. It gives later work an entry point to attach to.
It also gives CI something to run.
"""

from typing import Annotated

import typer

from t1pal import __version__

app = typer.Typer(name="t1pal", no_args_is_help=True)


def _show_version(requested: bool) -> None:
    """If the user gives `--version`, print the version and exit."""
    if requested:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Print the T1Pal version and exit.",
            callback=_show_version,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """A personal, local-first Type 1 diabetes data and analytics companion."""
