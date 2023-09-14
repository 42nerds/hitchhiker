import click
import copier


@click.command(name="new", short_help="Create new Odoo module from copier template")
@click.argument("name")
@click.pass_context
def new_cmd(ctx: click.Context, name):
    """Create new Odoo module from copier template"""

