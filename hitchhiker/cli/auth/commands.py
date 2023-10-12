import click
import hitchhiker.cli.auth.github as github


@click.group()
def auth() -> None:
    pass


auth.add_command(github.github)
