from functools import cmp_to_key
import click
import hitchhiker.odoo.module as odoo_mod


@click.command(name="list", short_help="Figure out new version and apply it")
@click.option("--glob", is_flag=False, default="./**", help="module search path glob")
@click.pass_context
def list_cmd(ctx: click.Context, glob):
    """list all odoo modules"""

    def cmp_module(a, b):
        if len(a.get_int_name()) < len(b.get_int_name()):
            return -1
        elif len(a.get_int_name()) > len(b.get_int_name()):
            return 1
        else:
            return 0

    modules = odoo_mod.discover_modules(glob)
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