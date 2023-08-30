import os
import git
import click
import tomlkit
import hitchhiker.cli.release.config as config
import hitchhiker.cli.release.version as version

@click.group()
@click.option("--workdir", default="./", help="working directory")
@click.pass_context
def release(ctx: click.Context, workdir):
    ctx.ensure_object(dict)
    try:
        repo = git.Repo(workdir)
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        raise click.ClickException(message="Could not find git repository")
    try:
        ctx.obj["RELEASE_CONF"] = config.create_context_from_raw_config(os.path.join(repo.working_tree_dir, "pyproject.toml"), repo)
    except (FileNotFoundError, tomlkit.exceptions.NonExistentKey) as e:
        raise click.FileError("pyproject.toml", hint=str(e))


release.add_command(version.version)
