from __future__ import annotations

import glob as pyglob
from functools import cmp_to_key
from pathlib import Path
from typing import Union

import click

import hitchhiker.odoo.module as odoo_mod


def discover_modules(glob: str) -> list[odoo_mod.Module]:
    return odoo_mod.discover_modules(
        list(
            filter(
                lambda n: Path(n).name == "__manifest__.py",
                pyglob.glob(glob, recursive=True),
            )
        )
    )


def _gen_list_output(output_format: str, modules: list[odoo_mod.Module]) -> None:
    def cmp_module(a: odoo_mod.Module, b: odoo_mod.Module) -> int:
        if len(a.get_int_name()) < len(b.get_int_name()):
            return -1
        if len(a.get_int_name()) > len(b.get_int_name()):
            return 1
        return 0

    if output_format == "text":
        spaces = len(
            sorted(modules, key=cmp_to_key(cmp_module), reverse=True)[0].get_int_name()
        )
        print(f"MODULE {(spaces - 6) * ' '}VERSION")
        for module in modules:
            print(
                f"{module.get_int_name()} {(spaces - len(module.get_int_name())) * ' '}{str(module.get_version())}"
            )
            for mod in modules:
                if (
                    mod.get_int_name() == module.get_int_name()
                    and mod.get_dir() != module.get_dir()
                ):
                    print(f"    !!! duplicate: {mod.get_int_name()} ({mod.get_dir()}, {module.get_dir()})")
    elif output_format == "markdown":
        print("| module | version |\n|---|---|")
        for module in modules:
            print(f"| {module.get_int_name()} | {str(module.get_version())} |")


@click.command(name="list", short_help="list Odoo modules and their versions")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.option(
    "--save",
    is_flag=False,
    default=None,
    help="file to update modules list in",
)
@click.option(
    "--output-format",
    is_flag=False,
    default="text",
    help='output format, "text" (default) or "markdown"',
)
@click.pass_context
def list_cmd(
    _ctx: click.Context, glob: str, save: Union[str, None], output_format: str
) -> None:
    """
    Lists all Odoo modules based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).
        --output-format (str): "text" (default) or "markdown"
        --save (str): File to update modules list in

    Description:
    This command lists all Odoo modules based on the provided glob pattern.
    It prints the module names and versions in a formatted table.

    """

    modules = discover_modules(glob)
    modules.sort(key=lambda x: (x.get_int_name(), x.get_dir()))

    if save is not None:
        with open(save, "r+", encoding="utf-8") as f:
            start_marker = "<!-- BEGIN HITCHHIKER MODULES LIST -->"
            end_marker = "<!-- END HITCHHIKER MODULES LIST -->"
            content = f.read()
            start_pos = content.find(start_marker)
            end_pos = content.find(end_marker)
            ncontent = content
            if start_pos >= 0 and end_pos >= 0:
                ncontent = f"{content[: start_pos + len(start_marker)]}\n"
                ncontent += "| module | version |\n|---|---|\n"
                for module in modules:
                    ncontent += (
                        f"| {module.get_int_name()} | {str(module.get_version())} |\n"
                    )
                ncontent += "\n\n"
                for module in modules:
                    for mod in modules:
                        if (
                            mod.get_int_name() == module.get_int_name()
                            and mod.get_dir() != module.get_dir()
                        ):
                            ncontent += f'<span style="color:red">duplicate module: {mod.get_int_name()}</span><br>\n'
                ncontent += f"\n{content[end_pos:]}"
            f.seek(0)
            f.write(ncontent)
            f.truncate()

    if len(modules) == 0:
        click.echo("No Odoo modules found")
        return

    _gen_list_output(output_format, modules)
