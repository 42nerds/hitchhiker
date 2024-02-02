import click

from hitchhiker.cli.odoo.dependency_graph import dependency_graph


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
def backup(_ctx: click.Context) -> None:
    """Backup Odoo"""


@odoo.command()
@click.pass_context
def staging(_ctx: click.Context) -> None:
    """Backup Odoo"""


odoo.add_command(dependency_graph)
