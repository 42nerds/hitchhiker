from click.testing import CliRunner
import pytest

cli = pytest.importorskip("hitchhiker.cli.cli").cli

def test_cli_entry():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
