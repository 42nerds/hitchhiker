import click
import pkg_resources

from .odoo import commands as odoo_cli
# from .release import commands as release


@click.group()
@click.version_option(version=pkg_resources.get_distribution("hitchhiker").version)
@click.option("--debug", is_flag=True, help="Show debug information")
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug

cli.add_command(odoo_cli.odoo)
# cli.add_command(release.main)