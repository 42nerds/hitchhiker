import click
import hitchhiker.cli.modules.list as list_mod


@click.group()
@click.pass_context
def modules(ctx: click.Context):
    ctx.ensure_object(dict)


modules.add_command(list_mod.list_cmd)
