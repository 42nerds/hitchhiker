from functools import cmp_to_key
import hitchhiker.release.enums as enums
import hitchhiker.release.commitparser.conventional as conventional


def _commit_cmp(a, b):
    a, _ = a
    b, _ = b
    if a.is_conventional and b.is_conventional:
        if a.get_version_bump() < b.get_version_bump():
            return -1
        elif a.get_version_bump() < b.get_version_bump():
            return 1
        elif (
            a.get_version_bump() == b.get_version_bump()
            and a.get_version_bump() == enums.VersionBump.NONE
        ):
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
def gen_changelog(change_commits, new_version, repo_owner=None, repo_name=None):
    out = f"\n## v{new_version}\n"
    for project in change_commits.keys():
        out += f"### {project} (v{str(change_commits[project][0])})\n"
        commits_types = {}
        commits = [
            (conventional.ConventionalCommitParser(commit.message), commit)
            for commit in change_commits[project][1]
        ]
        commits.sort(key=cmp_to_key(_commit_cmp), reverse=True)
        for commit, gitcommit in commits:
            type = commit.type if commit.is_conventional else "unknown"
            type = (
                "breaking" if commit.breaking is not None and commit.breaking else type
            )
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
