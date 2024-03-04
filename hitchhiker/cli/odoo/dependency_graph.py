from __future__ import annotations

from typing import Any

import click
import click_odoo  # type: ignore[import]
from odoo.tools import cloc  # type: ignore[import] # pylint: disable=import-error

from hitchhiker.odoo.dependency_graph_gen import gen_dependency_graph


@click.command()
@click_odoo.env_options(default_log_level="error")  # type: ignore[misc]
@click.option(
    "--standard", is_flag=True, help="include Odoo standard modules in the output"
)
@click.option("-o", "--output", required=True, help="output html file path")
def dependency_graph(env: Any, standard: bool, output: str) -> None:
    loc = cloc.Cloc()
    loc.count_database(env.cr.dbname)
    loc_modules = loc.code
    modules: list[tuple[str, list[str]]] = []
    for u in env["ir.module.module"].search([("state", "=", "installed")]):
        # exclude standard modules
        if not standard and u.name not in loc_modules:
            continue
        modules.append((u.name, u.dependencies_id.mapped(lambda x: x.name)))
    html = gen_dependency_graph(loc_modules, modules)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
