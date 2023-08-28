import os
import git
import click
import hitchhiker.cli.release.config as config

@click.group()
@click.option("--workdir", default="./", help="working directory")
@click.pass_context
def main(ctx: click.Context, workdir):
    repo = git.Repo(workdir)
    ctx.obj = config.create_context_from_raw_config(os.path.join(repo.working_tree_dir, "pyproject.toml"), repo)
    pass
