from functools import cmp_to_key
import glob as pyglob
from pathlib import Path
import click
import hitchhiker.odoo.module as odoo_mod


@click.command(name="list", short_help="list Odoo modules and their versions")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.option(
    "--output-format",
    is_flag=False,
    default="text",
    help='output format, "text" (default) or "markdown"',
)
@click.pass_context
def list_cmd(ctx: click.Context, glob: str, output_format: str) -> None:
    """
    Lists all Odoo modules based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).
        --output-format (str): "text" (default) or "markdown"

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
    modules.sort(key=lambda x: x.get_int_name())
    if len(modules) == 0:
        click.echo("No Odoo modules found")
        return
    if output_format == "text":
        spaces = len(
            sorted(modules, key=cmp_to_key(cmp_module), reverse=True)[0].get_int_name()
        )
        print(f"MODULE {(spaces - 6) * ' '}VERSION")
        for module in modules:
            print(
                f"{module.get_int_name()} {(spaces - len(module.get_int_name())) * ' '}{str(module.get_version())}"
            )
    elif output_format == "markdown":
        print("| module | version |\n|---|---|")
        for module in modules:
            print(f"| {module.get_int_name()} | {str(module.get_version())} |")
