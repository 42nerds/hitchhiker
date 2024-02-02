import click

from hitchhiker.cli.modules.list import discover_modules
from hitchhiker.odoo.dependency_graph_gen import gen_dependency_graph


@click.command(name="graph", short_help="generate a graph from modules directory")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.option("-o", "--output", required=True, help="output html file path")
@click.pass_context
def graph_cmd(_ctx: click.Context, glob: str, output: str) -> None:
    """
    Generates a Odoo module dependency graph in HTML format (+JS) based on the provided glob.

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).
        -o, --output (str): File to save output to
    """

    modules = discover_modules(glob)

    loc_modules: dict[str, int] = {}
    html = gen_dependency_graph(
        loc_modules,
        [(module.get_int_name(), module.get_dependencies()) for module in modules],
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
