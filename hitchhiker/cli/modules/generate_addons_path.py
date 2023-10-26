import glob as pyglob
from pathlib import Path
import click
import hitchhiker.odoo.module as odoo_mod


@click.command(name="generate_addons_path", short_help="Generate an Odoo addons path")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.pass_context
def generate_addons_path_cmd(ctx: click.Context, glob: str) -> None:
    """
    Generates Odoo addons path based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).

    Description:
    This command generates a Odoo addons path based on the provided glob pattern.
    It outputs all directories that contain modules as a comma-seperated list

    """

    modules = odoo_mod.discover_modules(
        list(
            filter(
                lambda n: Path(n).name == "__manifest__.py",
                pyglob.glob(glob, recursive=True),
            )
        )
    )
    moduledirs: list[str] = []
    for module in modules:
        moddir = str(Path(module.get_dir()).parent.absolute())
        if moddir not in moduledirs:
            moduledirs.append(moddir)

    if len(moduledirs) != 0:
        print(",".join(moduledirs))
    else:
        print("./")
