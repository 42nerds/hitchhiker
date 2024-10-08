import sys

import click

from hitchhiker.config.config import ConfigManager

from .auth import commands as auth
from .modules import commands as modules

if sys.version_info[1] > 7:
    import importlib.metadata

    _hitchhiker_version = importlib.metadata.version("hitchhiker")
else:
    import pkg_resources

    _hitchhiker_version = pkg_resources.get_distribution("hitchhiker").version


@click.group()
@click.version_option(version=_hitchhiker_version)
@click.option(
    "--conf", default="~/.config/hitchhiker/config.json", help="Configuration file path"
)
@click.option("--debug", is_flag=True, help="Show debug information")
@click.pass_context
def cli(ctx: click.Context, debug: bool, conf: str) -> None:
    """hitchhiker CLI entry point"""
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = debug
    ctx.obj["CONF"] = ConfigManager(conf, {})
    ctx.obj["VERSION"] = _hitchhiker_version


cli.add_command(modules.modules)
cli.add_command(auth.auth)

try:
    from .odoo import commands as odoo_cli

    cli.add_command(odoo_cli.odoo)
except ImportError:
    pass
    # FIXME: do these errors differently
    # click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")

try:
    from .release import commands as release

    cli.add_command(release.release)
except ImportError:
    pass
    # FIXME: do these errors differently
    # click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")

try:
    from .update import commands as update

    cli.add_command(update.update)
except ImportError:
    pass
    # FIXME: do these errors differently
    # click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")

try:
    from .gcloud import commands as gcloud

    cli.add_command(gcloud.gcloud)
except ImportError:
    pass
    # FIXME: do these errors differently
    # click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")
