import click

from hitchhiker.cli.odoo.dependency_graph import dependency_graph

from . import backup


@click.group()
def odoo() -> None:
    """Odoo related commands"""


odoo.add_command(dependency_graph)
odoo.add_command(backup.backup_cmd)
