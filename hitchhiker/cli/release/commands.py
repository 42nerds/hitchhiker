import os
import git
import click
import hitchhiker.cli.release.config as conf
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
