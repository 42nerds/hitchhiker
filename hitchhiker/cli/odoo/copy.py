import os
import subprocess
from contextlib import closing
from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]
from psycopg2 import sql  # pylint: disable=import-error

from . import click_odoo_ext


# https://github.com/odoo/odoo/blob/96a06df867fcef1fd24a1798bd5d6decc423933b/odoo/service/db.py#L153C1-L178C16
def _copy_db(srcdb: str, destdb: str) -> None:
    click.echo(f"copying database {srcdb} to {destdb}")
    odoo.sql_db.close_db(srcdb)
    db = odoo.sql_db.db_connect("postgres")
    with closing(db.cursor()) as cr:
        if odoo.release.version_info[0] <= 14:
            cr.autocommit(True)  # avoid transaction block
        else:
            # database-altering operations cannot be executed inside a transaction
            cr._cnx.autocommit = True  # pylint: disable=protected-access
        odoo.service.db._drop_conn(cr, srcdb)  # pylint: disable=protected-access
        cr.execute(
            sql.SQL("CREATE DATABASE {} ENCODING 'unicode' TEMPLATE {}").format(
                sql.Identifier(destdb), sql.Identifier(srcdb)
            )
        )


def _copy_filestore(srcdb: str, destdb: str) -> None:
    click.echo("copying filestore")
    store_src = odoo.tools.config.filestore(srcdb)
    click.echo(f"source filestore: {store_src}")
    if not os.path.isdir(store_src):
        raise RuntimeError(f"could not find filestore at {store_src}")
    store_dst = odoo.tools.config.filestore(destdb)
    click.echo(f"destination filestore: {store_dst}")
    rsync_exec = ["rsync", "-a", "--delete-delay", store_src + "/", store_dst]
    subprocess.check_call(rsync_exec)


@click.command("copy")
@click_odoo_ext.env_options(default_log_level="info", with_database=False, with_rollback=False)  # type: ignore[misc]
@click.option("--source-db", required=True, help="source database name")
@click.option("--dest-db", required=True, help="destination database name")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="overwrite even if the database already exists",
)
# pylint: disable=too-many-arguments
def copy_cmd(
    env: Any,  # pylint: disable=unused-argument
    source_db: str,
    dest_db: str,
    force: bool,
) -> None:
    """Copy Odoo DB & filestore. Does not do any operations on the database. Use reinit & neutralize commands for that"""
    if not odoo.service.db.exp_db_exist(source_db):
        raise RuntimeError("source database does not exist")
    if odoo.service.db.exp_db_exist(dest_db):
        if not force:
            raise RuntimeError("destination database already exists")
        if not odoo.service.db.exp_drop(dest_db):
            raise RuntimeError("error dropping old destination database")
    _copy_db(source_db, dest_db)
    _copy_filestore(source_db, dest_db)
