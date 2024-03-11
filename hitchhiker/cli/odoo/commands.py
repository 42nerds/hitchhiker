import click

from hitchhiker.cli.odoo.dependency_graph import dependency_graph

from . import backup, copy, neutralize, restore


@click.group()
def odoo() -> None:
    """Odoo related commands"""


odoo.add_command(dependency_graph)
odoo.add_command(backup.backup_cmd)
odoo.add_command(restore.restore_cmd)
odoo.add_command(neutralize.neutralize_cmd)
odoo.add_command(neutralize.reinit_cmd)
odoo.add_command(copy.copy_cmd)
