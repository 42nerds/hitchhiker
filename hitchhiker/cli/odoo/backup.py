import json
import os
import subprocess
import tempfile
from typing import Any

import click
import click_odoo  # type: ignore[import, import-untyped]
from click.decorators import _param_memo
from click_odoo import odoo

from hitchhiker.tools import backup


def __backup_filestore(b: backup.GenericBackup, dbname: str) -> None:
    path = odoo.tools.config.filestore(dbname)
    if os.path.isdir(path):
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


# monkeypatch click_odoo to accept more arguments
def __call_deco(fn: Any) -> Any:
    def wrap(self: Any, f: Any) -> Any:
        ret = fn(self, f)
        _param_memo(
            f,
            click.Option(("--db_password",), help="database password", required=True),
        )
        _param_memo(
            f,
            click.Option(("--db_user",), help="database user", required=True),
        )
        _param_memo(
            f,
            click.Option(("--db_port",), help="database port", required=True, type=int),
        )
        _param_memo(
            f,
            click.Option(("--db_host",), help="database host", required=True),
        )
        return ret

    return wrap


def __pop_params_deco(fn: Any) -> Any:
    def wrap(self: Any, ctx: Any) -> Any:
        fn(self, ctx)
        ctx.params.pop("db_host", None)
        ctx.params.pop("db_port", None)
        ctx.params.pop("db_user", None)
        ctx.params.pop("db_password", None)

    return wrap


def __get_odoo_args_deco(fn: Any) -> Any:
    def wrap(self: Any, ctx: Any) -> Any:
        ret = fn(self, ctx)
        ret.extend(["--db_host", ctx.params.get("db_host")])
        ret.extend(["--db_port", str(ctx.params.get("db_port"))])
        ret.extend(["--db_user", ctx.params.get("db_user")])
        ret.extend(["--db_password", ctx.params.get("db_password")])
        return ret

    return wrap


# pylint: disable=protected-access
click_odoo.env_options.__call__ = __call_deco(click_odoo.env_options.__call__)
# pylint: disable=protected-access
click_odoo.env_options._pop_params = __pop_params_deco(
    click_odoo.env_options._pop_params
)
click_odoo.env_options.get_odoo_args = __get_odoo_args_deco(
    click_odoo.env_options.get_odoo_args
)


@click.command("backup")
@click_odoo.env_options(default_log_level="error")  # type: ignore[misc]
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
