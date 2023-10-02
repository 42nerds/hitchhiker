import click
import pkg_resources
from hitchhiker.config.config import ConfigManager
from .modules import commands as modules


@click.group()
@click.version_option(version=pkg_resources.get_distribution("hitchhiker").version)
@click.option(
    "--conf", default="~/.config/hitchhiker/config.json", help="Configuration file path"
)
@click.option("--debug", is_flag=True, help="Show debug information")
@click.pass_context
def cli(ctx, debug, conf):
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = debug
    ctx.obj["CONF"] = ConfigManager(conf, {})


cli.add_command(modules.modules)

try:
    from .odoo import commands as odoo_cli

    cli.add_command(odoo_cli.odoo)
except ImportError as e:
    click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")

try:
    from .release import commands as release

    cli.add_command(release.release)
except ImportError as e:
    click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")
