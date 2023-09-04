import pathlib
import subprocess
import hitchhiker.release.version.semver as semver
import hitchhiker.release.enums as enums
import hitchhiker.cli.release.config as config
from hitchhiker.release.commitparser.conventional import ConventionalCommitParser # TODO: commit parser config

def find_latest_tag_in_commits(tags, commits):
    def search_commit(commit, commits):
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
    emptysha = subprocess.run(["git", "hash-object", "-t", "tree", "/dev/null"],
        capture_output=True, text=True, check=True).stdout.strip() # get empty tree SHA
    return (None, emptysha)


def get_tag_versions(tags):
    tag_ver = []
    for tag in tags:
        tag_ver.append((tag, semver.Version().parse(tag.name)))
    return sorted(tag_ver, reverse=True, key=lambda t: t[1])


def find_next_version(config, project, prerelease):
    tags = [(t, v) for t, v in get_tag_versions(config["repo"].tags) if (True if prerelease else v.prerelease is None)]
    commit_list, lastsha = find_latest_tag_in_commits(tags, list(config["repo"].iter_commits(config["repo"].active_branch)))
    if commit_list is None:
        commit_list = list(config["repo"].iter_commits(config["repo"].active_branch))
    commits = [] # [(msg: str, [file: str])]
    bump = enums.VersionBump.NONE

    for commit in reversed(commit_list):
        changed_files = [item.a_path for item in commit.tree.diff(lastsha) if str(pathlib.Path(item.a_path)).startswith(str(pathlib.Path(project["path"])))]
        if len(changed_files) > 0:
            parsed = ConventionalCommitParser(commit.message)
            if parsed.is_conventional and bump < parsed.get_version_bump():
                bump = parsed.get_version_bump()
            commits.append((commit, changed_files))
        lastsha = commit.hexsha
    return (bump, commits)
