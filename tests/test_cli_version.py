"""The `t1pal --version` contract: it prints the version and exits with code 0."""

import subprocess
import sys
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from t1pal import __version__
from t1pal.cli.main import app

runner = CliRunner()

REPO_ROOT = Path(__file__).parent.parent


def test_version_flag_prints_the_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_the_reported_version_matches_the_manifest() -> None:
    """The version the package reports is the version the manifest declares."""
    manifest = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())

    assert __version__ == manifest["project"]["version"]


def test_console_script_prints_the_version() -> None:
    """The installed `t1pal` entry point works, not only `python -m` or `uv run`."""
    console_script = Path(sys.executable).parent / "t1pal"
    assert console_script.exists(), "the t1pal console script is not installed"

    result = subprocess.run(  # noqa: S603
        [str(console_script), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == __version__
