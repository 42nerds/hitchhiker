from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]

from . import click_odoo_ext


@click.command("neutralize")
@click_odoo_ext.env_options(default_log_level="error")  # type: ignore[misc]
def neutralize_cmd(env: Any) -> None:  # pylint: disable=unused-argument
    """Neutralize Odoo database"""
    dbname = odoo.tools.config["db_name"]
    click.echo(f"neutralizing database: {dbname}")
    odoo.modules.neutralize.neutralize_database(env.cr)
    click.echo("neutralized.")
