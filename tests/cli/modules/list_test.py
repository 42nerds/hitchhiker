import os

from click.testing import CliRunner

from hitchhiker.cli.cli import cli
from tests.cli.modules.mod_fixtures import *  # noqa: F403, F401


def test_list_no_mods(no_mods):
    os.chdir(no_mods)
    expected_output = "No Odoo modules found\n"
    result = CliRunner().invoke(cli, ["modules", "list"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_one_mod(one_mod):
    os.chdir(one_mod)
    expected_output = "MODULE                VERSION\nsome_cool_odoo_module 1.5.3\n"
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "text"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_ten_mods(ten_mods):
    os.chdir(ten_mods)
    expected_output = """MODULE                       VERSION
a_another_cool_odoo_module   19.8.1
a_b_c                        64.128.256
b_very_cool_odoo_module      0.0.1
boring_odoo_module           1.2.3
c_some_cool_odoo_module      0.5.3
d_extremely_cool_odoo_module 5.3.1
epic_odoo_module             0.0.0
interesting_odoo_module      256.128.64
something                    8.2.7
z_some_mod                   15.0.0
"""
    result = CliRunner().invoke(cli, ["modules", "list"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_ten_mods_markdown(ten_mods):
    os.chdir(ten_mods)
    expected_output = """| module | version |
|---|---|
| a_another_cool_odoo_module | 19.8.1 |
| a_b_c | 64.128.256 |
| b_very_cool_odoo_module | 0.0.1 |
| boring_odoo_module | 1.2.3 |
| c_some_cool_odoo_module | 0.5.3 |
| d_extremely_cool_odoo_module | 5.3.1 |
| epic_odoo_module | 0.0.0 |
| interesting_odoo_module | 256.128.64 |
| something | 8.2.7 |
| z_some_mod | 15.0.0 |
"""
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "markdown"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_dupe_mods(dupe_mods):
    os.chdir(dupe_mods)
    expected_output = """MODULE                       VERSION
a_another_cool_odoo_module   19.8.1
b_very_cool_odoo_module      1.2.3
    !!! duplicate: b_very_cool_odoo_module
b_very_cool_odoo_module      1.2.3
    !!! duplicate: b_very_cool_odoo_module
c_some_cool_odoo_module      0.5.3
d_extremely_cool_odoo_module 0.0.0
    !!! duplicate: d_extremely_cool_odoo_module
d_extremely_cool_odoo_module 0.0.0
    !!! duplicate: d_extremely_cool_odoo_module
"""
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "text"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output
