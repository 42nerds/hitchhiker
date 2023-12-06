import click

from hitchhiker.cli.auth import github


@click.group()
def auth() -> None:
    pass


auth.add_command(github.github)
