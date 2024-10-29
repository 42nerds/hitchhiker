import os
from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]

from . import click_odoo_ext


@click.command("restore")
@click_odoo_ext.env_options(default_log_level="info", with_database=False, with_rollback=False, with_addons_path=True)  # type: ignore[misc]
@click.option("-i", "--input", "input_path", required=True, help="input zip file path")
@click.option("-d", "--db_name", required=True, help="database name")
@click.option(
    "--copy/--move",
    is_flag=True,
    default=True,
    help="Is this a database copy or move? When i doubt always use copy",
)
@click.option("--neutralize", is_flag=True, default=False, help="neutralize?")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="overwrite even if the database already exists",
)
# pylint: disable=too-many-arguments
def restore_cmd(
    env: Any,  # pylint: disable=unused-argument
    input_path: str,
    db_name: str,
    copy: bool,
    neutralize: bool,
    force: bool,
) -> None:
    """Restore Odoo DB & filestore"""
    if os.path.isfile(input_path):
        click.echo(f"restoring database: {db_name}")
        if odoo.service.db.exp_db_exist(db_name):
            if not force:
                raise RuntimeError("database already exists")
            if not odoo.service.db.exp_drop(db_name):
                raise RuntimeError("error dropping old database")
        odoo.service.db.restore_db(db_name, input_path, copy, neutralize)
    else:
        raise RuntimeError("unsupported backup format")
