import os
import random

import pytest

git = pytest.importorskip("git")


def randomid(chars=10, ranges=None):
    if ranges is None:
        ranges = [("0", "9"), ("a", "z"), ("A", "Z")]
    allowed = []
    for start, end in ranges:
        allowed += range(ord(start), ord(end))
    rid = ""
    for _ in range(chars):
        rid += chr(random.choice(allowed))
    return rid


def create_git_repo(path):
    repo = git.Repo.init(path)
    repo.git.branch("-M", "main")
    with repo.config_writer("repository") as config:
        config.set_value("user", "name", "example")
        config.set_value("user", "email", "example@example.com")
    return repo


def create_configs(repo, projects, main_version, prerelease_token="rc", is_odoo=False):
    print(repo.working_tree_dir)
    if not is_odoo:
        with open(f"{repo.working_tree_dir}/pyproject.toml", "w") as f:
            f.write(
                f"""[project]
version = "{main_version}"

[tool.hitchhiker]
projects = {str([n for n, _, _ in projects])}
version_toml = ["pyproject.toml:project.version"]
"""
            )
            for project, version, prerelease in projects:
                f.write(
                    f"""
[tool.hitchhiker.project.{project}]
path = "{project}/"
version_variables = ["{project}/__init__.py:__version__"]
prerelease = {"true" if prerelease else "false"}
prerelease_token = "{prerelease_token}"
"""
                )
        repo.git.add("pyproject.toml")
    else:
        with open(f"{repo.working_tree_dir}/setup.cfg", "w") as f:
            f.write(
                f"""[tool.hitchhiker]
project_version = {main_version}
version_cfg = setup.cfg:tool.hitchhiker:project_version
"""
            )
        repo.git.add("setup.cfg")
    for project, version, prerelease in projects:
        if not os.path.isdir(f"{repo.working_tree_dir}/{project}"):
            os.mkdir(f"{repo.working_tree_dir}/{project}")
        with open(f"{repo.working_tree_dir}/{project}/__init__.py", "w") as f:
            f.write(f'__version__ = "{version}"\n')
        repo.git.add(f"{project}/__init__.py")
        if is_odoo:
            with open(f"{repo.working_tree_dir}/{project}/__manifest__.py", "w") as f:
                f.write(f'{{\n    "version": "{version}"\n}}')


def create_random_file(repo, path=""):
    fname = f"{repo.working_tree_dir}/{path}/{randomid(chars=20)}"
    with open(fname, "w") as f:
        f.write(f"test file\n{fname}\n")
    repo.git.add(fname)


def create_commits(repo, commits):
    for commit in commits:
        for _ in range(10):
            create_random_file(repo, commit[1])
        repo.git.commit(m=commit[0])


@pytest.fixture
def repo_empty(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, [("project1", "0.0.0", False)], "0.0.0")
    create_commits(repo, [["Initial commit", ""]])

    yield repo
    repo.close()


@pytest.fixture
def repo_one_fix(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, [("project1", "0.0.0", False)], "0.0.0")
    create_commits(repo, [["Initial commit", ""], ["fix: abcd", "project1"]])

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_one_breaking_change(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo, [("project1", "0.0.0", False), ("project2", "0.0.0", False)], "0.0.0"
    )
    create_commits(
        repo,
        [
            ["Initial commit", ""],
            ["fix: something", "project2"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
        ],
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", False),
            ("project2", "0.0.0", False),
            ("1another_project", "0.0.0", False),
            ("2another_project", "0.0.0", False),
        ],
        "0.0.0",
    )
    create_commits(
        repo,
        [
            ["Initial commit", ""],
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", False),
            ("project2", "0.0.0", False),
            ("1another_project", "0.0.0", False),
            ("2another_project", "1.0.0", False),
        ],
        "1.0.0",
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )
    repo.git.tag("v1.0.0", m="v1.0.0")

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag_fix_after(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", False),
            ("project2", "0.0.0", False),
            ("1another_project", "0.0.0", False),
            ("2another_project", "1.0.0", False),
        ],
        "1.0.0",
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )
    repo.git.tag("v1.0.0", m="v1.0.0")
    create_commits(
        repo, [["fix: something", "project1"], ["fix: something else", "project2"]]
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_prerelease_tag(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", True),
            ("project2", "0.0.0", True),
            ("1another_project", "0.0.0", True),
            ("2another_project", "0.0.0", False),
        ],
        "0.0.0",
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )
    repo.git.tag("v1.0.0-rc.0", m="v1.0.0-rc.0")

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_prerelease_tag_fix_after(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", True),
            ("project2", "0.0.0", False),
            ("1another_project", "0.0.0", False),
            ("2another_project", "0.0.0", True),
        ],
        "0.0.0",
        prerelease_token="alpha",
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )
    repo.git.tag("v1.0.0-rc.0", m="v1.0.0-rc.0")
    create_commits(
        repo,
        [
            ["fix: something", "1another_project"],
            ["fix: something else", "project2"],
            ["feat: something else", "project1"],
        ],
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag_fix_after_odoo(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", False),
            ("project2", "0.0.0", False),
            ("1another_project", "0.0.0", False),
            ("2another_project", "1.0.0", False),
        ],
        "1.0.0",
        is_odoo=True,
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "1another_project"],
            ["feat!: some feature that breaks things", "2another_project"],
        ],
    )
    repo.git.tag("v1.0.0", m="v1.0.0")
    create_commits(
        repo, [["fix: something", "project1"], ["fix: something else", "project2"]]
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag_fix_after_odoo_diff_project_name(
    tmp_path_factory,
):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("project1", "0.0.0", False),
            ("project2", "0.0.0", False),
            ("some_project_name", "0.0.0", False),
            ("some_project_name_with_extra_feature", "1.0.0", False),
        ],
        "1.0.0",
        is_odoo=True,
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"],
            ["fix: something else", "project2"],
            ["feat: some feature", "some_project_name"],
            [
                "feat!: some feature that breaks things",
                "some_project_name_with_extra_feature",
            ],
        ],
    )
    repo.git.tag("v1.0.0", m="v1.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["fix: something else", "project2"],
            ["feat: another feature", "some_project_name_with_extra_feature"],
        ],
    )

    yield repo
    repo.close()
