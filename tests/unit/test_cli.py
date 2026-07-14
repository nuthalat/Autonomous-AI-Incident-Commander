"""CLI smoke tests."""

from __future__ import annotations

import pytest

from incident_commander import __version__
from incident_commander.cli.__main__ import main


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == __version__


def test_cli_info_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["info", "--json"]) == 0
    output = capsys.readouterr().out
    assert "fake" in output
    assert __version__ in output
