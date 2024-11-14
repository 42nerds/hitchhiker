from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]

from . import click_odoo_ext

def do_neutralize(env: Any, dbname: str) -> None:
    click.echo(f"neutralizing database: {dbname}")
    if odoo.release.version_info[0] >= 16:
        odoo.modules.neutralize.neutralize_database(env.cr)
    else:
        click.echo("odoo < 16 detected - neutralizing manually")
        env.cr.execute(
            "SELECT EXISTS ( SELECT FROM pg_tables WHERE tablename = 'ir_mail_server');"
        )
        if env.cr.fetchall()[0][0]:
            click.echo("Deleting ir_mail_server records")
            env.cr.execute("DELETE FROM ir_mail_server;")
        env.cr.execute(
            "SELECT EXISTS ( SELECT FROM pg_tables WHERE tablename = 'fetchmail_server');"
        )
        if env.cr.fetchall()[0][0]:
            click.echo("Deleting fetchmail_server records")
            env.cr.execute("DELETE FROM fetchmail_server;")
        env.cr.execute(
            "SELECT EXISTS ( SELECT FROM pg_tables WHERE tablename = 'ir_cron');"
        )
        if env.cr.fetchall()[0][0]:
            click.echo("Disabling ir_cron records")
            env.cr.execute(
                "UPDATE ir_cron SET active = false WHERE id NOT IN ("
                + "SELECT res_id FROM ir_model_data "
                + "WHERE model = 'ir.cron' "
                + "AND name = 'autovacuum_job' "
                + "AND module = 'base');"
            )
        env.cr.execute(
            "SELECT EXISTS ( SELECT FROM pg_tables WHERE tablename = 'account_online_link');"
        )
        if env.cr.fetchall()[0][0]:
            click.echo("Deactivating online synchronisation")
            env.cr.execute("UPDATE account_online_link SET auto_sync = false;")
        env.cr.execute(
            "SELECT EXISTS ( SELECT FROM pg_tables WHERE tablename = 'ir_config_parameter');"
        )
        if env.cr.fetchall()[0][0]:
            click.echo("Setting database.is_neutralized")
            env.cr.execute(
                "INSERT INTO ir_config_parameter (key, value) "
                + "VALUES ('database.is_neutralized', true) "
                + "ON CONFLICT (key) DO "
                + "UPDATE SET value = true;"
            )
    click.echo("neutralized.")

@click.command("neutralize")
@click_odoo_ext.env_options(default_log_level="info", with_addons_path=True)  # type: ignore[misc]
def neutralize_cmd(env: Any) -> None:  # pylint: disable=unused-argument
    """Neutralize Odoo database"""
    dbname = odoo.tools.config["db_name"]
    do_neutralize(env, dbname)

@click.command("reinit")
@click_odoo_ext.env_options(default_log_level="info", with_addons_path=True)  # type: ignore[misc]
def reinit_cmd(env: Any) -> None:  # pylint: disable=unused-argument
    """Generates a new dbuuid and stuff (same operation done when you copy a database)"""
    dbname = odoo.tools.config["db_name"]
    click.echo(f"reinitializing database {dbname}")
    # force generation of a new dbuuid
    env = odoo.api.Environment(env.cr, odoo.SUPERUSER_ID, {})
    env["ir.config_parameter"].init(force=True)
