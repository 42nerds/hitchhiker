import os
import git
import click
import tomlkit
import hitchhiker.cli.release.config as conf
import hitchhiker.cli.release.version as version


@click.group()
@click.option(
    "--config",
    default="pyproject.toml",
    help="configuration file path (relative to working directory)",
)
@click.option("--workdir", default="./", help="working directory")
@click.pass_context
def release(ctx: click.Context, workdir, config):
    ctx.ensure_object(dict)
    try:
        repo = git.Repo(workdir)
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        raise click.ClickException(message="Could not find git repository")
    try:
        ctx.obj["RELEASE_CONF"] = conf.create_context_from_raw_config(
            os.path.join(repo.working_tree_dir, config), repo
        )
    except (FileNotFoundError, tomlkit.exceptions.NonExistentKey) as e:
        raise click.FileError(os.path.join(repo.working_tree_dir, config), hint=str(e))


release.add_command(version.version)
