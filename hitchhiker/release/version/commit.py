import pathlib
from typing import Optional, Dict, Any
import subprocess
import git
import hitchhiker.cli.release.tagfix as tagfix
import hitchhiker.release.version.semver as semver
import hitchhiker.release.enums as enums
from hitchhiker.release.commitparser.conventional import ConventionalCommitParser

# FIXME: this file needs a lot of cleanup

def _find_latest_tag_in_commits(
    tags: list[tuple[git.refs.tag.TagReference, semver.Version]],
    commits: list[git.objects.commit.Commit],
) -> tuple[Optional[list[git.objects.commit.Commit]], str]:
    """
    Finds the latest tag in a list of commits.

    Parameters:
        tags (list): A list of tuples containing tag references and their corresponding semver versions.
        commits (list): A list of Git commit objects.

    Returns:
        tuple: A tuple containing the list of commits up to the latest tag and the hash of the latest tag.

    Description:
    This function searches for the latest tag in a list of commits. It returns the list of commits up to the latest tag
    and the hash of the latest tag.

    Note:
    This function assumes the availability of the `git` command-line utility.

    Example:
    ```
    commits, latest_tag_sha = _find_latest_tag_in_commits(tags, commits_list)
    print(f"The latest tag was at commit: {latest_tag_sha}")
    ```

    """
    def search_commit(
        commit: git.objects.commit.Commit, commits: list[git.objects.commit.Commit]
    ) -> Optional[tuple[list[git.objects.commit.Commit], str]]:
        i = 0
        while i < len(commits):
            if commits[i].binsha == commit.binsha:
                return (commits[:i], commits[i].hexsha)
            i += 1
        return None

    for tag in tags:
        r = search_commit(tag[0].commit, commits)
        if r is not None:
            return r
    # get empty tree SHA
    emptysha = subprocess.run(
        ["git", "hash-object", "-t", "tree", "/dev/null"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return (None, emptysha)


def _get_tag_versions(
    config: Dict[str, Any],
    tags: list[git.refs.tag.TagReference],
) -> list[tuple[git.refs.tag.TagReference, semver.Version]]:
    """
    Retrieves the versions associated with a list of Git tag references.

    Parameters:
        tags (list): A list of Git tag references.

    Returns:
        list: A list of tuples containing tag references and their corresponding semver versions.

    Description:
    This function retrieves the versions associated with a list of Git tag references and returns them as tuples.
    The tags are sorted in descending order based on their semver versions.

    Example:
    ```
    tag_versions = _get_tag_versions(tag_references)
    for tag, version in tag_versions:
        print(f"Tag: {tag.name}, Version: {version}")
    ```

    """
    tag_ver = []
    for tag in tags:
        tag_ver.append(
            (
                tag,
                semver.Version().parse(
                    tagfix.get_tag_without_branch(config, str(tag.name))
                ),
            )
        )
    tag_ver.sort(reverse=True, key=lambda t: t[1])
    return tag_ver


def find_next_version(
    config: Dict[str, Any], project: Dict[str, Any], prerelease: bool
) -> tuple[enums.VersionBump, list[tuple[git.objects.commit.Commit, list[str]]]]:
    """
    Finds the next version bump and associated commits for a project.

    Parameters:
        config (dict): Configuration information for the repository and versioning.
        project (dict): Project information including path and other details.
        prerelease (bool): Whether to consider prerelease versions.

    Returns:
        tuple: A tuple containing the version bump and a list of tuples representing commits and changed files.

    Description:
    This function determines the next version bump based on conventional commit messages in the project.
    It analyzes commits, identifies changes relevant to the project, and associates them with version bumps.

    Example:
    ```
    version_bump, commits = find_next_version(config, project_info, False)
    print(f"Next version bump: {version_bump}")
    print("Commits and changed files:")
    for commit, changed_files in commits:
        print(f"- Commit: {commit.hexsha}, Changed Files: {', '.join(changed_files)}")
    ```

    """
    tags = [
        (t, v)
        for t, v in _get_tag_versions(config, config["repo"].tags)
        if (True if prerelease else v.prerelease is None)
    ]
    commit_list, lastsha = _find_latest_tag_in_commits(
        tags, list(config["repo"].iter_commits(config["repo"].active_branch))
    )
    if commit_list is None:
        commit_list = list(config["repo"].iter_commits(config["repo"].active_branch))
    commits = []
    bump = enums.VersionBump.NONE

    for commit in reversed(commit_list):
        changed_files = [
            item.a_path
            for item in commit.tree.diff(lastsha)
            if str(pathlib.Path(item.a_path)).startswith(
                str(pathlib.Path(project["path"])) + "/"
            )
        ]
        if len(changed_files) > 0:
            parsed = ConventionalCommitParser(str(commit.message))
            if parsed.is_conventional and bump < parsed.get_version_bump():
                bump = parsed.get_version_bump()
            commits.append((commit, changed_files))
        lastsha = commit.hexsha
    return (bump, commits)
