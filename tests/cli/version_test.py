from tests.git_fixtures import *
from click.testing import CliRunner
from hitchhiker_module_control.cli import main

# FIXME: this is a horrible mess

def test_version_repo_empty(repo_empty):
    """test for Version"""
    workdir = repo_empty.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.0\nproject: project1 version: 0.0.0\n"

def test_version_repo_one_fix(repo_one_fix):
    """test for Version"""
    workdir = repo_one_fix.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.1\nproject: project1 version: 0.0.1\n"

def test_version_repo_multi_one_breaking_change(repo_multi_one_breaking_change):
    """test for Version"""
    workdir = repo_multi_one_breaking_change.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 1.0.0\nproject: project1 version: 0.0.0\nproject: project2 version: 1.0.0\n"

def test_version_repo_multi_project_commits(repo_multi_project_commits):
    """test for Version"""
    workdir = repo_multi_project_commits.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 1.0.0\nproject: project1 version: 0.0.1\nproject: project2 version: 1.0.0\nproject: 1another_project version: 0.1.0\nproject: 2another_project version: 1.0.0\n"

def test_version_repo_multi_project_commits_before_tag(repo_multi_project_commits_before_tag):
    """test for Version"""
    workdir = repo_multi_project_commits_before_tag.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.0\nproject: project1 version: 0.0.0\nproject: project2 version: 0.0.0\nproject: 1another_project version: 0.0.0\nproject: 2another_project version: 0.0.0\n"

def test_version_repo_multi_project_commits_before_tag_fix_after(repo_multi_project_commits_before_tag_fix_after):
    """test for Version"""
    workdir = repo_multi_project_commits_before_tag_fix_after.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.1\nproject: project1 version: 0.0.1\nproject: project2 version: 0.0.1\nproject: 1another_project version: 0.0.0\nproject: 2another_project version: 0.0.0\n"

def test_version_repo_multi_project_commits_before_prerelease_tag1(repo_multi_project_commits_before_prerelease_tag):
    """test for Version"""
    workdir = repo_multi_project_commits_before_prerelease_tag.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 1.0.0\nproject: project1 version: 0.0.1\nproject: project2 version: 1.0.0\nproject: 1another_project version: 0.1.0\nproject: 2another_project version: 1.0.0\n"

def test_version_repo_multi_project_commits_before_prerelease_tag2(repo_multi_project_commits_before_prerelease_tag):
    """test for Version"""
    workdir = repo_multi_project_commits_before_prerelease_tag.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--prerelease"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.0\nproject: project1 version: 0.0.0\nproject: project2 version: 0.0.0\nproject: 1another_project version: 0.0.0\nproject: 2another_project version: 0.0.0\n"


def test_version_repo_multi_project_commits_before_prerelease_tag_fix_after1(repo_multi_project_commits_before_prerelease_tag_fix_after):
    """test for Version"""
    workdir = repo_multi_project_commits_before_prerelease_tag_fix_after.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 1.0.0\nproject: project1 version: 0.0.1\nproject: project2 version: 1.0.0\nproject: 1another_project version: 0.1.0\nproject: 2another_project version: 1.0.0\n"

def test_version_repo_multi_project_commits_before_prerelease_tag_fix_after2(repo_multi_project_commits_before_prerelease_tag_fix_after):
    """test for Version"""
    workdir = repo_multi_project_commits_before_prerelease_tag_fix_after.working_tree_dir
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--prerelease"])
    assert result.exit_code == 0
    result = CliRunner().invoke(main, ["--workdir", workdir, "version", "--show"])
    assert result.exit_code == 0
    assert result.output == "main version: 0.0.1-rc.0\nproject: project1 version: 0.0.0\nproject: project2 version: 0.0.1-rc.0\nproject: 1another_project version: 0.0.1-rc.0\nproject: 2another_project version: 0.0.0\n"
