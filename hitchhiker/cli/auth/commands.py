import click
import hitchhiker.cli.auth.github as github


@click.group()
def auth():
    pass


auth.add_command(github.github)
