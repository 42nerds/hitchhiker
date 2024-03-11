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
    expected_output = "MODULE                VERSION PATH\nsome_cool_odoo_module 1.5.3   some_cool_odoo_module\n"
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "text"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_ten_mods(ten_mods):
    os.chdir(ten_mods)
    expected_output = """MODULE                       VERSION    PATH
a_another_cool_odoo_module   19.8.1     a_another_cool_odoo_module
a_b_c                        64.128.256 a_b_c
b_very_cool_odoo_module      0.0.1      b_very_cool_odoo_module
boring_odoo_module           1.2.3      boring_odoo_module
c_some_cool_odoo_module      0.5.3      c_some_cool_odoo_module
d_extremely_cool_odoo_module 5.3.1      d_extremely_cool_odoo_module
epic_odoo_module             0.0.0      epic_odoo_module
interesting_odoo_module      256.128.64 interesting_odoo_module
something                    8.2.7      something
z_some_mod                   15.0.0     z_some_mod
"""
    result = CliRunner().invoke(cli, ["modules", "list"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_ten_mods_markdown(ten_mods):
    os.chdir(ten_mods)
    expected_output = """| module | version | path |
|---|---|---|
| a_another_cool_odoo_module | 19.8.1 | a_another_cool_odoo_module |
| a_b_c | 64.128.256 | a_b_c |
| b_very_cool_odoo_module | 0.0.1 | b_very_cool_odoo_module |
| boring_odoo_module | 1.2.3 | boring_odoo_module |
| c_some_cool_odoo_module | 0.5.3 | c_some_cool_odoo_module |
| d_extremely_cool_odoo_module | 5.3.1 | d_extremely_cool_odoo_module |
| epic_odoo_module | 0.0.0 | epic_odoo_module |
| interesting_odoo_module | 256.128.64 | interesting_odoo_module |
| something | 8.2.7 | something |
| z_some_mod | 15.0.0 | z_some_mod |
"""
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "markdown"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_dupe_mods(dupe_mods):
    os.chdir(dupe_mods)
    expected_output = """MODULE                       VERSION PATH
a_another_cool_odoo_module   19.8.1  a_another_cool_odoo_module
b_very_cool_odoo_module      1.2.3   b_very_cool_odoo_module
    !!! duplicate: b_very_cool_odoo_module (./somedir/b_very_cool_odoo_module, ./b_very_cool_odoo_module)
b_very_cool_odoo_module      1.2.3   somedir/b_very_cool_odoo_module
    !!! duplicate: b_very_cool_odoo_module (./b_very_cool_odoo_module, ./somedir/b_very_cool_odoo_module)
c_some_cool_odoo_module      0.5.3   c_some_cool_odoo_module
d_extremely_cool_odoo_module 0.0.0   d_extremely_cool_odoo_module
    !!! duplicate: d_extremely_cool_odoo_module (./somedir/d_extremely_cool_odoo_module, ./d_extremely_cool_odoo_module)
d_extremely_cool_odoo_module 0.0.0   somedir/d_extremely_cool_odoo_module
    !!! duplicate: d_extremely_cool_odoo_module (./d_extremely_cool_odoo_module, ./somedir/d_extremely_cool_odoo_module)
"""
    result = CliRunner().invoke(cli, ["modules", "list", "--output-format", "text"])
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output


def test_list_ten_mods_markdown_save(ten_mods, tmp_path_factory):
    os.chdir(ten_mods)
    expected_output = """| module | version | path |
|---|---|---|
| a_another_cool_odoo_module | 19.8.1 | a_another_cool_odoo_module |
| a_b_c | 64.128.256 | a_b_c |
| b_very_cool_odoo_module | 0.0.1 | b_very_cool_odoo_module |
| boring_odoo_module | 1.2.3 | boring_odoo_module |
| c_some_cool_odoo_module | 0.5.3 | c_some_cool_odoo_module |
| d_extremely_cool_odoo_module | 5.3.1 | d_extremely_cool_odoo_module |
| epic_odoo_module | 0.0.0 | epic_odoo_module |
| interesting_odoo_module | 256.128.64 | interesting_odoo_module |
| something | 8.2.7 | something |
| z_some_mod | 15.0.0 | z_some_mod |
"""
    testf = tmp_path_factory.mktemp("tdir") / "test.md"
    with open(testf, "w") as f:
        f.write(
            """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
this will be replaced
replaced<!-- END HITCHHIKER MODULES LIST -->test
hii
Hello world this is some text
hello
"""
        )
    expect_f_out = """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
| module | version | path |
|---|---|---|
| a_another_cool_odoo_module | 19.8.1 | a_another_cool_odoo_module |
| a_b_c | 64.128.256 | a_b_c |
| b_very_cool_odoo_module | 0.0.1 | b_very_cool_odoo_module |
| boring_odoo_module | 1.2.3 | boring_odoo_module |
| c_some_cool_odoo_module | 0.5.3 | c_some_cool_odoo_module |
| d_extremely_cool_odoo_module | 5.3.1 | d_extremely_cool_odoo_module |
| epic_odoo_module | 0.0.0 | epic_odoo_module |
| interesting_odoo_module | 256.128.64 | interesting_odoo_module |
| something | 8.2.7 | something |
| z_some_mod | 15.0.0 | z_some_mod |



<!-- END HITCHHIKER MODULES LIST -->test
hii
Hello world this is some text
hello
"""
    result = CliRunner().invoke(
        cli, ["modules", "list", "--output-format", "markdown", "--save", testf]
    )
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output
    with open(testf) as f:
        assert f.read() == expect_f_out


def test_list_ten_mods_markdown_save_noinsert(ten_mods, tmp_path_factory):
    os.chdir(ten_mods)
    expected_output = """| module | version | path |
|---|---|---|
| a_another_cool_odoo_module | 19.8.1 | a_another_cool_odoo_module |
| a_b_c | 64.128.256 | a_b_c |
| b_very_cool_odoo_module | 0.0.1 | b_very_cool_odoo_module |
| boring_odoo_module | 1.2.3 | boring_odoo_module |
| c_some_cool_odoo_module | 0.5.3 | c_some_cool_odoo_module |
| d_extremely_cool_odoo_module | 5.3.1 | d_extremely_cool_odoo_module |
| epic_odoo_module | 0.0.0 | epic_odoo_module |
| interesting_odoo_module | 256.128.64 | interesting_odoo_module |
| something | 8.2.7 | something |
| z_some_mod | 15.0.0 | z_some_mod |
"""
    testf = tmp_path_factory.mktemp("tdir") / "test.md"
    with open(testf, "w") as f:
        f.write(
            """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
this will be replaced
replacedtest
hii
Hello world this is some text
hello
"""
        )
    expect_f_out = """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
this will be replaced
replacedtest
hii
Hello world this is some text
hello
"""
    result = CliRunner().invoke(
        cli, ["modules", "list", "--output-format", "markdown", "--save", testf]
    )
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output
    with open(testf) as f:
        assert f.read() == expect_f_out


def test_list_dupe_mods_save(dupe_mods, tmp_path_factory):
    os.chdir(dupe_mods)
    expected_output = """MODULE                       VERSION PATH
a_another_cool_odoo_module   19.8.1  a_another_cool_odoo_module
b_very_cool_odoo_module      1.2.3   b_very_cool_odoo_module
    !!! duplicate: b_very_cool_odoo_module (./somedir/b_very_cool_odoo_module, ./b_very_cool_odoo_module)
b_very_cool_odoo_module      1.2.3   somedir/b_very_cool_odoo_module
    !!! duplicate: b_very_cool_odoo_module (./b_very_cool_odoo_module, ./somedir/b_very_cool_odoo_module)
c_some_cool_odoo_module      0.5.3   c_some_cool_odoo_module
d_extremely_cool_odoo_module 0.0.0   d_extremely_cool_odoo_module
    !!! duplicate: d_extremely_cool_odoo_module (./somedir/d_extremely_cool_odoo_module, ./d_extremely_cool_odoo_module)
d_extremely_cool_odoo_module 0.0.0   somedir/d_extremely_cool_odoo_module
    !!! duplicate: d_extremely_cool_odoo_module (./d_extremely_cool_odoo_module, ./somedir/d_extremely_cool_odoo_module)
"""
    testf = tmp_path_factory.mktemp("tdir") / "test.md"
    with open(testf, "w") as f:
        f.write(
            """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
this will be replaced
replaced<!-- END HITCHHIKER MODULES LIST -->test
hii
Hello world this is some text
hello
"""
        )
    expect_f_out = """test text

test<!-- BEGIN HITCHHIKER MODULES LIST -->
| module | version | path |
|---|---|---|
| a_another_cool_odoo_module | 19.8.1 | a_another_cool_odoo_module |
| b_very_cool_odoo_module | 1.2.3 | b_very_cool_odoo_module |
| b_very_cool_odoo_module | 1.2.3 | somedir/b_very_cool_odoo_module |
| c_some_cool_odoo_module | 0.5.3 | c_some_cool_odoo_module |
| d_extremely_cool_odoo_module | 0.0.0 | d_extremely_cool_odoo_module |
| d_extremely_cool_odoo_module | 0.0.0 | somedir/d_extremely_cool_odoo_module |


<span style="color:red">duplicate module: b_very_cool_odoo_module</span><br>
<span style="color:red">duplicate module: b_very_cool_odoo_module</span><br>
<span style="color:red">duplicate module: d_extremely_cool_odoo_module</span><br>
<span style="color:red">duplicate module: d_extremely_cool_odoo_module</span><br>

<!-- END HITCHHIKER MODULES LIST -->test
hii
Hello world this is some text
hello
"""
    result = CliRunner().invoke(
        cli, ["modules", "list", "--output-format", "text", "--save", testf]
    )
    print(f'got: """{result.output}""" expected: """{expected_output}"""')
    assert result.exit_code == 0
    assert result.output == expected_output
    with open(testf) as f:
        assert f.read() == expect_f_out
