from typer.testing import CliRunner

from cakrawala_radar.cli import app


def test_cli_version_command():
    result = CliRunner().invoke(app, ["version"])

    assert result.exit_code == 0
    assert "cakrawala-radar" in result.stdout
