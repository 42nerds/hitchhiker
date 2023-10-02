import sys
import subprocess
import click
import github
import hitchhiker.release.version.semver as semver


def get_latest(ctx) -> semver.Version:
    try:
        if not ctx.obj["CONF"].has_key("GITHUB_TOKEN"):
            raise Exception("GitHub token not found")
        gh = github.Github(ctx.obj["CONF"].get_key("GITHUB_TOKEN"))
        releases = gh.get_repo("42nerds/hitchhiker").get_releases()
    except Exception as e:
        click.secho(
            "Error getting releases from GitHub. Is something wrong with your token?",
            err=True,
            fg="red",
        )
        raise e
    if len(list(releases)) > 0:
        return semver.Version().parse(releases[0].tag_name)
    raise Exception("no release found")


@click.command()
@click.pass_context
def update(ctx):
    """Check for updates"""
    version = semver.Version().parse(ctx.obj["VERSION"])
    click.echo(f"Current version: {version}")
    try:
        latest = get_latest(ctx)
        if latest > version:
            click.echo(f"New version version available: {latest}")
        elif version > latest:
            click.echo(
                f"Your version is newer than the remote version. Remote is {version}!"
            )
            return
        else:
            click.echo(f"You are on latest")
            return
    except Exception as e:
        click.echo(f"error checking for new version: {e}")
        return

    git_url = "https://github.com/42nerds/hitchhiker.git"
    click.echo(
        f'command to update: {sys.executable} -m pip install "hitchhiker @ git+{git_url}"'
    )
    if click.confirm("Do you want to run it now?"):
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"hitchhiker @ git+{git_url}",
            ]
        )
