import click
import hitchhiker.cli.modules.list as list


@click.group()
@click.pass_context
def modules(ctx: click.Context):
    ctx.ensure_object(dict)


modules.add_command(list.list_cmd)
