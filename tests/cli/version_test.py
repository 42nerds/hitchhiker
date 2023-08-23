from tests.git_fixtures import *
from click.testing import CliRunner
import hitchhiker_module_control.version.semver as semver
from hitchhiker_module_control.cli import main


# versions: [(project, version)]
def invoke_cli_version_cmd(repo, main_version, versions, prerelease=False):
    workdir = repo.working_tree_dir

    args = ["--workdir", workdir, "version"]
    if prerelease:
        args.append("--prerelease")
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0
    # TODO: check output here

    expected_output = f"main version: {str(semver.Version().parse(main_version))}\n"
    for project, version in versions:
        expected_output += (
            f"project: {project} version: {str(semver.Version().parse(version))}\n"
        )
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.output == expected_output
    assert result.exit_code == 0


def test_version_repo_empty(repo_empty):
    """test for Version"""
    repo = repo_empty
    invoke_cli_version_cmd(repo, "0.0.0", [("project1", "0.0.0")])


def test_version_repo_one_fix(repo_one_fix):
    """test for Version"""
    repo = repo_one_fix
    invoke_cli_version_cmd(repo, "0.0.1", [("project1", "0.0.1")])


def test_version_repo_multi_one_breaking_change(repo_multi_one_breaking_change):
    """test for Version"""
    repo = repo_multi_one_breaking_change
    invoke_cli_version_cmd(
        repo, "1.0.0", [("project1", "0.0.0"), ("project2", "1.0.0")]
    )


def test_version_repo_multi_project_commits(repo_multi_project_commits):
    """test for Version"""
    repo = repo_multi_project_commits
    invoke_cli_version_cmd(
        repo,
        "1.0.0",
        [
            ("project1", "0.0.1"),
            ("project2", "1.0.0"),
            ("1another_project", "0.1.0"),
            ("2another_project", "1.0.0"),
        ],
    )


def test_version_repo_multi_project_commits_before_tag(
    repo_multi_project_commits_before_tag,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_tag
    invoke_cli_version_cmd(
        repo,
        "0.0.0",
        [
            ("project1", "0.0.0"),
            ("project2", "0.0.0"),
            ("1another_project", "0.0.0"),
            ("2another_project", "0.0.0"),
        ],
    )


def test_version_repo_multi_project_commits_before_tag_fix_after(
    repo_multi_project_commits_before_tag_fix_after,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_tag_fix_after
    invoke_cli_version_cmd(
        repo,
        "0.0.1",
        [
            ("project1", "0.0.1"),
            ("project2", "0.0.1"),
            ("1another_project", "0.0.0"),
            ("2another_project", "0.0.0"),
        ],
    )


def test_version_repo_multi_project_commits_before_prerelease_tag1(
    repo_multi_project_commits_before_prerelease_tag,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_prerelease_tag
    invoke_cli_version_cmd(
        repo,
        "1.0.0",
        [
            ("project1", "0.0.1"),
            ("project2", "1.0.0"),
            ("1another_project", "0.1.0"),
            ("2another_project", "1.0.0"),
        ],
    )


def test_version_repo_multi_project_commits_before_prerelease_tag2(
    repo_multi_project_commits_before_prerelease_tag,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_prerelease_tag
    invoke_cli_version_cmd(
        repo,
        "0.0.0",
        [
            ("project1", "0.0.0"),
            ("project2", "0.0.0"),
            ("1another_project", "0.0.0"),
            ("2another_project", "0.0.0"),
        ],
        prerelease=True,
    )


def test_version_repo_multi_project_commits_before_prerelease_tag_fix_after1(
    repo_multi_project_commits_before_prerelease_tag_fix_after,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_prerelease_tag_fix_after
    invoke_cli_version_cmd(
        repo,
        "1.0.0",
        [
            ("project1", "0.0.1"),
            ("project2", "1.0.0"),
            ("1another_project", "0.1.0"),
            ("2another_project", "1.0.0"),
        ],
    )


def test_version_repo_multi_project_commits_before_prerelease_tag_fix_after2(
    repo_multi_project_commits_before_prerelease_tag_fix_after,
):
    """test for Version"""
    repo = repo_multi_project_commits_before_prerelease_tag_fix_after
    invoke_cli_version_cmd(
        repo,
        "0.0.1-rc.0",
        [
            ("project1", "0.0.0"),
            ("project2", "0.0.1-rc.0"),
            ("1another_project", "0.0.1-rc.0"),
            ("2another_project", "0.0.0"),
        ],
        prerelease=True,
    )
