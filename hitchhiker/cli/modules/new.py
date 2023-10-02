import click
import copier


@click.command(name="new", short_help="Create new Odoo module from copier template")
@click.argument("name")
@click.option("--template", is_flag=False, default="https://github.com/42nerds/copier_odoo_module.git", help="Copier template URL")
@click.pass_context
def new_cmd(ctx: click.Context, name, template):
    """Create new Odoo module from copier template"""
    click.echo(f"Creating {name} from {template}")
    copier.run_copy(template, name)

