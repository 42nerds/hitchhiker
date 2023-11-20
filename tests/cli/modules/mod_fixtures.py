import os

import pytest


def get_human_name(name: str):
    name = name.replace("_", " ")
    name = name[:0] + name[0].upper() + name[1:]
    return name


def dict2str(dictionary):
    st = "{"
    for key in dictionary:
        value = dictionary[key]
        st += "    "
        st += f'"{key}": '
        st += f'"{value}",'
    st += "}\n"
    return st


def create_odoo_mod(bpath, name, version):
    os.mkdir(f"{bpath}/{name}")
    with open(f"{bpath}/{name}/__manifest__.py", "w") as f:
        f.write(dict2str({"name": get_human_name(name), "version": version}))


@pytest.fixture
def no_mods(tmp_path_factory):
    path = tmp_path_factory.mktemp("moddir")
    return path


@pytest.fixture
def one_mod(tmp_path_factory):
    path = tmp_path_factory.mktemp("moddir")
    create_odoo_mod(path, "some_cool_odoo_module", "1.5.3")
    return path


@pytest.fixture
def ten_mods(tmp_path_factory):
    path = tmp_path_factory.mktemp("moddir")
    create_odoo_mod(path, "c_some_cool_odoo_module", "0.5.3")
    create_odoo_mod(path, "a_another_cool_odoo_module", "16.0.19.8.1")
    create_odoo_mod(path, "b_very_cool_odoo_module", "0.0.1")
    create_odoo_mod(path, "d_extremely_cool_odoo_module", "5.3.1")
    create_odoo_mod(path, "epic_odoo_module", "1.0.0.0.0")
    create_odoo_mod(path, "boring_odoo_module", "1.2.3")
    create_odoo_mod(path, "interesting_odoo_module", "256.128.64")
    create_odoo_mod(path, "a_b_c", "17.0.64.128.256")
    create_odoo_mod(path, "something", "16.0.8.2.7")
    create_odoo_mod(path, "z_some_mod", "15.0.15.0.0")
    return path


@pytest.fixture
def dupe_mods(tmp_path_factory):
    path = tmp_path_factory.mktemp("moddir")
    create_odoo_mod(path, "c_some_cool_odoo_module", "0.5.3")
    create_odoo_mod(path, "a_another_cool_odoo_module", "16.0.19.8.1")
    create_odoo_mod(path, "b_very_cool_odoo_module", "1.2.3")
    create_odoo_mod(path, "d_extremely_cool_odoo_module", "0.0.0")
    os.mkdir(f"{path}/somedir")
    create_odoo_mod(f"{path}/somedir", "d_extremely_cool_odoo_module", "1.0.0.0.0")
    create_odoo_mod(f"{path}/somedir", "b_very_cool_odoo_module", "1.2.3")
    return path
