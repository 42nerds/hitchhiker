import click
import hitchhiker.cli.modules.list as list_mod
import hitchhiker.cli.modules.generate_addons_path as generate_addons_path_mod

# FIXME: all these commands need tests


@click.group()
@click.pass_context
def modules(ctx: click.Context) -> None:
    """
    Commands related to Odoo modules
    """
    ctx.ensure_object(dict)


modules.add_command(list_mod.list_cmd)
modules.add_command(generate_addons_path_mod.generate_addons_path_cmd)

try:
    import hitchhiker.cli.modules.new as new_mod

    modules.add_command(new_mod.new_cmd)
except ImportError as e:
    click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")
