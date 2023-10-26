from functools import cmp_to_key
from typing import Dict, Any, Optional
import git
import hitchhiker.release.enums as enums
import hitchhiker.release.commitparser.conventional as conventional
import hitchhiker.release.version.semver as semver

# TODO: this could potentioally be moved to conventional.py??
def _commit_cmp(
    _a: tuple[conventional.ConventionalCommitParser, git.objects.commit.Commit],
    _b: tuple[conventional.ConventionalCommitParser, git.objects.commit.Commit],
) -> int:
    """
    Comparison function for sorting commits based on version bump and conventional commit properties.

    Parameters:
        _a (tuple): A tuple containing a ConventionalCommitParser instance and a Git commit.
        _b (tuple): A tuple containing a ConventionalCommitParser instance and a Git commit.

    Returns:
        int: -1 if _a should come before _b, 1 if _a should come after _b, 0 if they are equal.

    Description:
    This function compares two commits based on their version bump type and conventional commit properties.
    It is intended to be used as a comparison function for sorting commits.
    """
    a, _ = _a
    b, _ = _b
    if a.is_conventional and b.is_conventional:
        if a.get_version_bump() < b.get_version_bump():
            return -1
        elif a.get_version_bump() < b.get_version_bump():
            return 1
        elif (
            a.get_version_bump() == b.get_version_bump()
            and a.get_version_bump() == enums.VersionBump.NONE
        ):
            assert a.type is not None and b.type is not None
            return -1 if a.type < b.type else 1
        elif a.get_version_bump() == b.get_version_bump():
            return 0
    elif not a.is_conventional and not b.is_conventional:
        return -1
    elif not a.is_conventional:
        return -1
    elif not b.is_conventional:
        return 1
    return 0


# change_commits: {"projectname": [version, [commitmsgs]]}
def gen_changelog(
    change_commits: Dict[str, tuple[semver.Version, list[git.objects.commit.Commit]]],
    new_version: semver.Version,
    projects_old: list[Dict[str, Any]],
    projects_new: list[Dict[str, Any]],
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
) -> str:
    """
    Generates a changelog based on commit messages and project versions.

    Parameters:
        change_commits (dict): A dictionary mapping project names to a tuple containing the new version and a list of commits.
        new_version (semver.Version): The new version for the changelog.
        projects_old (list): A list of dictionaries representing the old project versions.
        projects_new (list): A list of dictionaries representing the new project versions.
        repo_owner (str, optional): The owner of the repository (for commit links). Default is None.
        repo_name (str, optional): The name of the repository (for commit links). Default is None.

    Returns:
        str: The generated changelog.

    Description:
    This function generates a changelog based on the provided commit messages, new version, and project versions.
    It organizes commits by project and types, creating a structured changelog with commit messages and links.

    Example:
    ```
    changelog = gen_changelog(change_commits, new_version, projects_old, projects_new)
    print(changelog)
    ```
    """
    out = f"\n## v{new_version}\n"
    out += "### Projects\n| module | version |\n| -------- | ----------- |\n"
    for oldp, newp in zip(projects_old, projects_new):
        assert oldp["name"] == newp["name"]
        version_changed = oldp["version"] != newp["version"]
        out += f"| {newp['name']}{' :boom:' if version_changed else ''} | {newp['version']}{' :new:' if version_changed else ''} |\n"

    for project in change_commits.keys():
        out += f"### {project} (v{str(change_commits[project][0])})\n"
        commits_types: Dict[
            str,
            list[
                tuple[conventional.ConventionalCommitParser, git.objects.commit.Commit]
            ],
        ] = {}
        commits = [
            (conventional.ConventionalCommitParser(str(commit.message)), commit)
            for commit in change_commits[project][1]
        ]
        commits.sort(key=cmp_to_key(_commit_cmp), reverse=True)
        for commit, gitcommit in commits:
            type = commit.type if commit.is_conventional else "unknown"
            type = (
                "breaking" if commit.breaking is not None and commit.breaking else type
            )
            assert type is not None
            if type not in commits_types:
                commits_types[type] = []
            commits_types[type].append((commit, gitcommit))
        for type in commits_types.keys():
            out += f"#### {type}\n"
            for commit, gitcommit in commits_types[type]:
                link = ""
                if repo_owner is not None and repo_name is not None:
                    link = f" ([`{gitcommit.hexsha}`](https://github.com/{repo_owner}/{repo_name}/commit/{gitcommit.hexsha}))"
                out += f"- {commit.get_raw_subject()}{link}\n"  # TODO: config option for URL
    return out
