import click

import click_odoo  # type: ignore[import]


@click.group()
@click.option(
    "-c",
    "--config",
    default="./odoo.conf",
    help="path to odoo configuration file",
    type=click.Path(exists=True),
)
@click.pass_context
def odoo(ctx: click.Context, config: str) -> None:
    """Odoo related commands"""
    ctx.obj["ODOO_CONF"] = config


@odoo.command()
@click.pass_context
def backup(ctx: click.Context) -> None:
    """Backup Odoo"""
    pass


@odoo.command()
@click.pass_context
def staging(ctx: click.Context) -> None:
    """Backup Odoo"""
