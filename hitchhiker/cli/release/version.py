import copy
import os
import re
from typing import Optional, Dict
import git
import github
import click
import hitchhiker.release.version.semver as semver
import hitchhiker.release.version.commit as commit
import hitchhiker.cli.release.config as config
import hitchhiker.release.enums as enums
import hitchhiker.release.changelog as changelog


def get_repo_owner_name(ctx: click.Context) -> tuple[Optional[str], Optional[str]]:
    """Uses regex to figure out github repo owner and name from remote URL"""
    # regex from: https://stackoverflow.com/a/25102190
    try:
        _match = re.match(
            r"^(?:(?:git@|https:\/\/)(?:[\w\.@]+)(?:\/|:))([\w,\-,\_]+)\/([\w,\-,\_]+)(?:.git){0,1}(?:(?:\/){0,1})$",
            str(
                git.cmd.Git(ctx.obj["RELEASE_CONF"]["repo"].working_tree_dir).execute(
                    ["git", "config", "--get", "remote.origin.url"]
                )
            ),
        )
        repo_owner = _match.group(1) if _match is not None else None
        repo_name = _match.group(2) if _match is not None else None
    except git.GitCommandError:
        repo_owner = None
        repo_name = None
    return (repo_owner, repo_name)


def write_changelog(
    ctx: click.Context, changelog_newtext: str, changedfiles: list[str]
) -> None:
    """Appends changes to changelog"""
    changelog_path = os.path.join(
        ctx.obj["RELEASE_CONF"]["repo"].working_tree_dir, "CHANGELOG.md"
    )
    if not os.path.isfile(changelog_path):
        with open(changelog_path, "w") as f:
            f.write("# CHANGELOG\n" + changelog_newtext)
    else:
        with open(changelog_path, "a") as f:
            f.write(changelog_newtext)
    changedfiles.append("CHANGELOG.md")


def commit_and_tag(
    ctx: click.Context, changedfiles: list[str], commitmsg: str, newtag: str
) -> None:
    """Creates commit and tags it"""
    ctx.obj["RELEASE_CONF"]["repo"].git.add(changedfiles)
    ctx.obj["RELEASE_CONF"]["repo"].git.commit(m=commitmsg)
    if newtag not in [tag.name for tag in ctx.obj["RELEASE_CONF"]["repo"].tags]:
        ctx.obj["RELEASE_CONF"]["repo"].git.tag("-a", newtag, m=newtag)
    else:
        click.secho(f'tag "{newtag}" already exists', fg="red", err=True)


def do_gh_release(
    ctx: click.Context, newtag: str, message: str, prerelease: bool, ghtoken: str
) -> None:
    """Creates a github release"""
    repo_owner, repo_name = get_repo_owner_name(ctx)
    if repo_owner is None or repo_name is None:
        raise click.ClickException(
            message="could not parse remote URL to get owner & repository name"
        )
    try:
        auth = github.Auth.Token(ghtoken)
        gh = github.Github(auth=auth)
    except Exception:  # TODO: figure out which exceptions could be thrown here
        raise click.ClickException(
            message="Failed to authenticate at GitHub with token"
        )

    try:
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
    except Exception:  # TODO: figure out which exceptions could be thrown here
        raise click.ClickException(message="Failed to get repository from github")

    try:
        repo.create_git_release(
            tag=newtag,
            name=newtag,
            message=message,
            prerelease=prerelease,
            target_commitish=ctx.obj["RELEASE_CONF"]["repo"]
            .commit(ctx.obj["RELEASE_CONF"]["repo"].active_branch)
            .hexsha,
        )
    except Exception:  # TODO: figure out which exceptions could be thrown here
        raise click.ClickException(message="Failed to create release on GitHub")


@click.command(short_help="Figure out new version and apply it")
@click.option("--show", is_flag=True, default=False, help="print versions and exit")
@click.option(
    "--prerelease", is_flag=True, default=False, help="do main release as prerelease"
)
@click.option(
    "--prerelease-token", is_flag=False, default="rc", help="main prerelease token"
)
@click.option("--push", is_flag=True, default=False, help="push to origin")
@click.option("--ghrelease", is_flag=True, default=False, help="create github release")
@click.option(
    "--ghtoken", default=lambda: os.getenv("GITHUB_TOKEN"), help="GitHub token"
)
@click.pass_context
def version(
    ctx: click.Context,
    show: bool,
    prerelease: bool,
    prerelease_token: str,
    push: bool,
    ghrelease: bool,
    ghtoken: str,
) -> None:
    """Figure out new version and apply it"""
    if ghrelease and not push:
        raise click.BadOptionUsage(
            "ghrelease", "--ghrelease must be used together with --push"
        )
    if show:
        click.echo(f"main version: {ctx.obj['RELEASE_CONF']['version']}")
        for project in ctx.obj["RELEASE_CONF"]["projects"]:
            click.echo(f"{project['name']}: {project['version']}")
        return

    click.echo(f"main version: {ctx.obj['RELEASE_CONF']['version']}")
    old_project_objs = copy.deepcopy(ctx.obj["RELEASE_CONF"]["projects"])
    mainbump = enums.VersionBump.NONE
    bumped = False
    changedfiles = []
    change_commits: Dict[
        str, tuple[semver.Version, list[git.objects.commit.Commit]]
    ] = {}
    for project in ctx.obj["RELEASE_CONF"]["projects"]:
        click.echo(f"{project['name']}: {project['version']}")
        if (
            re.match(
                f"^{project['branch_match']}$",
                str(ctx.obj["RELEASE_CONF"]["repo"].active_branch),
            )
            is None
        ):
            click.secho(
                "    -> ignoring project (branch_match does not match)", fg="yellow"
            )
            continue
        bump, commits = commit.find_next_version(
            ctx.obj["RELEASE_CONF"], project, project["prerelease"]
        )
        mainbump = bump if bump > mainbump else mainbump
        if bump != enums.VersionBump.NONE:
            ver_prev = copy.deepcopy(project["version"])
            project["version"].bump(
                bump,
                project["prerelease"],
                prerelease_token=project["prerelease_token"],
            )
            if ver_prev != project["version"]:
                bumped = True

            if project["name"] not in change_commits:
                change_commits[project["name"]] = (
                    project["version"],
                    [commitmsg for commitmsg, _ in commits],
                )

            changedfiles += config.set_version(ctx.obj["RELEASE_CONF"], project)
            click.secho(f"    -> new version: {project['version']}", fg="green")

    if bumped:
        ctx.obj["RELEASE_CONF"]["version"].bump(
            mainbump, prerelease, prerelease_token=prerelease_token
        )
        changedfiles += config.set_version(
            ctx.obj["RELEASE_CONF"], ctx.obj["RELEASE_CONF"]
        )
        click.secho(
            f"new main version: {ctx.obj['RELEASE_CONF']['version']}", fg="green"
        )

    assert len(changedfiles) > 0 if bumped else True

    if len(changedfiles) > 0:
        repo_owner, repo_name = get_repo_owner_name(ctx)

        changelog_newtext = changelog.gen_changelog(
            change_commits=change_commits,
            new_version=ctx.obj["RELEASE_CONF"]["version"],
            projects_old=old_project_objs,
            projects_new=ctx.obj["RELEASE_CONF"]["projects"],
            repo_owner=repo_owner,
            repo_name=repo_name,
        )
        write_changelog(ctx, changelog_newtext, changedfiles)

        newtag = f"v{str(ctx.obj['RELEASE_CONF']['version'])}"
        commitmsg = (
            f"{str(ctx.obj['RELEASE_CONF']['version'])}\n\nAutogenerated by hitchhiker"
        )
        commit_and_tag(ctx, changedfiles, commitmsg, newtag)

        if push:
            try:
                ctx.obj["RELEASE_CONF"]["repo"].remote(
                    name="origin"
                ).push().raise_if_error()
            except Exception:  # TODO: figure out which exceptions could be thrown here
                raise click.ClickException(message="Failed to push")
        if ghrelease:
            if ghtoken is None:
                raise click.ClickException(message='Failed to get "GITHUB_TOKEN"')
            do_gh_release(ctx, newtag, changelog_newtext, prerelease, ghtoken)
