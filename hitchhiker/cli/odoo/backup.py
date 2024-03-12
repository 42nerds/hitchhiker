import json
import os
import subprocess
import tempfile
from typing import Any

import click
from click_odoo import odoo  # type: ignore[import, import-untyped]

from hitchhiker.tools import backup

from . import click_odoo_ext


def __backup_filestore(b: backup.GenericBackup, dbname: str) -> None:
    path = odoo.tools.config.filestore(dbname)
    if not os.path.isdir(path):
        raise RuntimeError(f"could not find filestore at {path}")
    b.add_dir(path, "filestore")


def __backup_database(b: backup.GenericBackup, dbname: str) -> None:
    cmd = [odoo.tools.find_pg_tool("pg_dump"), "--no-owner", dbname]
    env = odoo.tools.exec_pg_environ()
    with tempfile.NamedTemporaryFile("w") as f:
        cmd.insert(-1, "--file=" + f.name)
        subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            check=True,
        )
        f.flush()
        os.fsync(f.fileno())
        b.add_file(f.name, "dump.sql")


def __dump_manifest(b: backup.GenericBackup, dbname: str) -> None:
    with tempfile.NamedTemporaryFile("w") as f:
        db = odoo.sql_db.db_connect(dbname)
        with db.cursor() as cr:
            json.dump(odoo.service.db.dump_db_manifest(cr), f, indent=4)
        f.flush()
        os.fsync(f.fileno())
        b.add_file(f.name, "manifest.json")


@click.command("backup")
@click_odoo_ext.env_options(default_log_level="error")  # type: ignore[misc]
@click.option("-o", "--output", required=True, help="output zip file path")
def backup_cmd(env: Any, output: str) -> None:  # pylint: disable=unused-argument
    """Backup Odoo"""
    dbname = odoo.tools.config["db_name"]
    click.echo(f"starting backup on database: {dbname}")
    with backup.backup(output, "zip") as b:
        click.echo("backing up filestore")
        __backup_filestore(b, dbname)
        click.echo("backing up database")
        __backup_database(b, dbname)
        click.echo("creating manifest")
        __dump_manifest(b, dbname)
    click.echo(f"created backup: {output}")
