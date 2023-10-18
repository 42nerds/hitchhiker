import click
import copier  # type: ignore[import]


@click.command(name="new", short_help="Create new Odoo module from copier template")
@click.argument("name")
@click.option(
    "--template",
    is_flag=False,
    default="https://github.com/42nerds/copier_odoo_module.git",
    help="Copier template URL",
)
@click.pass_context
def new_cmd(ctx: click.Context, name: str, template: str) -> None:
    """
    Creates a new Odoo module from a copier template.

    Parameters:
        ctx (click.Context): The Click context object.
        name (str): The name of the new module to create.
        template (str): The copier template to use.

    Returns:
        None

    Description:
    This function creates a new Odoo module from a copier template.
    It takes the name of the new module and the copier template as input.
    The copier template is used to generate the new module based on the provided template.

    Example:
    ```
    new_cmd(click_ctx, "my_odoo_module", "path/to/template")
    ```

    """
    click.echo(f"Creating {name} from {template}")
    copier.run_copy(template, name)
