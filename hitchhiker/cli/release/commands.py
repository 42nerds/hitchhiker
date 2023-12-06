import os

import click
import git

import hitchhiker.cli.release.config as conf
from hitchhiker.cli.release import version


@click.group()
@click.option("--workdir", default="./", help="working directory")
@click.pass_context
def release(ctx: click.Context, workdir: str) -> None:
    """
    Prepares the release context for a git repository.

    Parameters:
        workdir (str): The path to the working directory.

    Description:
    This command group prepares the release context for a git repository based on the provided working directory.
    It first checks if the working directory is a valid git repository.
    It then attempts to read the configuration from "pyproject.toml" or "setup.cfg" in the repository.
    The configuration is used to create the release context.

    """
    ctx.ensure_object(dict)
    try:
        repo = git.Repo(workdir)  # type: ignore[attr-defined]
    except (git.InvalidGitRepositoryError, git.NoSuchPathError) as e:
        raise click.ClickException(message="Could not find git repository") from e
    assert repo.working_tree_dir is not None
    cfgpath = os.path.join(repo.working_tree_dir, "pyproject.toml")
    if os.path.isfile(cfgpath):
        ctx.obj["RELEASE_CONF"] = conf.create_context_from_raw_config(
            cfgpath, repo, False
        )
    else:
        cfgpath = os.path.join(repo.working_tree_dir, "setup.cfg")
        ctx.obj["RELEASE_CONF"] = conf.create_context_from_raw_config(
            cfgpath, repo, True
        )


release.add_command(version.version)
