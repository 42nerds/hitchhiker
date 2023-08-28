import os
import git
import click
import hitchhiker.cli.config as config

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__)
@click.option("--workdir", default="./", help="working directory")
@click.pass_context
def main(ctx: click.Context, workdir):
    repo = git.Repo(workdir)
    ctx.obj = config.create_context_from_raw_config(os.path.join(repo.working_tree_dir, "pyproject.toml"), repo)
