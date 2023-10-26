from functools import cmp_to_key
import glob as pyglob
from pathlib import Path
import click
import hitchhiker.odoo.module as odoo_mod


@click.command(name="list", short_help="Figure out new version and apply it")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.pass_context
def list_cmd(ctx: click.Context, glob: str) -> None:
    """
    Lists all Odoo modules based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`). 

    Description:
    This command lists all Odoo modules based on the provided glob pattern.
    It prints the module names and versions in a formatted table.

    """
    def cmp_module(a: odoo_mod.Module, b: odoo_mod.Module) -> int:
        if len(a.get_int_name()) < len(b.get_int_name()):
            return -1
        elif len(a.get_int_name()) > len(b.get_int_name()):
            return 1
        else:
            return 0

    modules = odoo_mod.discover_modules(
        list(
            filter(
                lambda n: Path(n).name == "__manifest__.py",
                pyglob.glob(glob, recursive=True),
            )
        )
    )
    if len(modules) == 0:
        click.echo("No Odoo modules found")
        return
    spaces = len(
        sorted(modules, key=cmp_to_key(cmp_module), reverse=True)[0].get_int_name()
    )
    click.echo(f"MODULE {(spaces - 6) * ' '}VERSION")
    for module in modules:
        print(
            f"{module.get_int_name()} {(spaces - len(module.get_int_name())) * ' '}{str(module.get_version())}"
        )
