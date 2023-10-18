import click
import hitchhiker.cli.modules.list as list_mod


@click.group()
@click.pass_context
def modules(ctx: click.Context) -> None:
    """
    Ensures the existence of a dictionary object in the Click context.

    Parameters:
        ctx (click.Context): The Click context object.

    Returns:
        None

    Description:
    This function ensures the existence of a dictionary object in the Click context.
    It can be used to store and access data throughout the execution of the CLI application.

    Example:
    ```
    modules(click_ctx)
    ```

    """
    ctx.ensure_object(dict)


modules.add_command(list_mod.list_cmd)

try:
    import hitchhiker.cli.modules.new as new_mod

    modules.add_command(new_mod.new_cmd)
except ImportError as e:
    click.secho(f"Please install {e.name} for full functionality.", err=True, fg="red")
