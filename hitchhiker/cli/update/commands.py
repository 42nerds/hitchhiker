import sys
import os
import subprocess
import click
import github
import hitchhiker.release.version.semver as semver


def _get_latest(ctx: click.Context) -> semver.Version:
    """
    Retrieves the latest version from a GitHub repository.

    Parameters:
        ctx (click.Context): The Click context object.

    Returns:
        semver.Version: The latest version parsed using semver.

    Description:
    This function retrieves the latest version from a specified GitHub repository.
    It uses the GitHub API and a provided GitHub token from the configuration to fetch the releases.
    The latest release version is then parsed using semver.

    Example:
    ```
    latest_version = _get_latest(click_ctx)
    ```

    """
    try:
        if (
            not ctx.obj["CONF"].has_key("GITHUB_TOKEN")
            and "GITHUB_TOKEN" not in os.environ
        ):
            raise Exception("GitHub token not found")
        gh = github.Github(
            os.environ.get("GITHUB_TOKEN", ctx.obj["CONF"].get_key("GITHUB_TOKEN"))
        )
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
    raise Exception("no releases found")


@click.command()
@click.pass_context
def update(ctx: click.Context) -> None:
    """
    Checks for updates to the current hitchhiker version and provides update instructions.

    Description:
    This command checks for updates to the current version of the application.
    It retrieves the latest version from a specified GitHub repository and compares it with the current version.
    If a newer version is available, it provides instructions on how to update.

    """
    version = semver.Version().parse(ctx.obj["VERSION"])
    click.echo(f"Current version: {version}")
    try:
        latest = _get_latest(ctx)
        if latest > version:
            click.echo(f"New version available: {latest}")
        elif version > latest:
            click.echo(
                f"Your version is newer than the remote version. Remote is {version}!"
            )
            return
        else:
            click.echo(f"No update available (remote version {latest})")
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
