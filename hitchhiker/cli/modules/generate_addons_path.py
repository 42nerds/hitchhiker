from __future__ import annotations

from pathlib import Path

import click

from hitchhiker.cli.modules.list import discover_modules


@click.command(name="generate_addons_path", short_help="Generate an Odoo addons path")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.pass_context
def generate_addons_path_cmd(_ctx: click.Context, glob: str) -> None:
    """
    Generates Odoo addons path based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).

    Description:
    This command generates a Odoo addons path based on the provided glob pattern.
    It outputs all directories that contain modules as a comma-seperated list

    """

    modules = discover_modules(glob)
    moduledirs: list[str] = []
    for module in modules:
        moddir = str(Path(module.get_dir()).parent.absolute())
        if moddir not in moduledirs:
            moduledirs.append(moddir)

    if len(moduledirs) != 0:
        print(",".join(moduledirs))
    else:
        print("./")
