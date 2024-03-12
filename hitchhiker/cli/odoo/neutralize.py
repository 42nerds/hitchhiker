from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]

from . import click_odoo_ext


@click.command("neutralize")
@click_odoo_ext.env_options(default_log_level="info", with_addons_path=True)  # type: ignore[misc]
def neutralize_cmd(env: Any) -> None:  # pylint: disable=unused-argument
    """Neutralize Odoo database"""
    dbname = odoo.tools.config["db_name"]
    click.echo(f"neutralizing database: {dbname}")
    odoo.modules.neutralize.neutralize_database(env.cr)
    click.echo("neutralized.")


@click.command("reinit")
@click_odoo_ext.env_options(default_log_level="info", with_addons_path=True)  # type: ignore[misc]
def reinit_cmd(env: Any) -> None:  # pylint: disable=unused-argument
    """Generates a new dbuuid and stuff (same operation done when you copy a database)"""
    dbname = odoo.tools.config["db_name"]
    click.echo(f"reinitializing database {dbname}")
    # force generation of a new dbuuid
    env = odoo.api.Environment(env.cr, odoo.SUPERUSER_ID, {})
    env["ir.config_parameter"].init(force=True)
