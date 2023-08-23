import os
import random
import git
import pytest

def create_git_repo(path):
    repo = git.Repo.init(path)
    repo.git.branch("-M", "main")
    with repo.config_writer("repository") as config:
        config.set_value("user", "name", "example")
        config.set_value("user", "email", "example@example.com")
    return repo


def create_configs(repo, projects):
    print(repo.working_tree_dir)
    with open(f"{repo.working_tree_dir}/pyproject.toml", "w") as f:
        f.write(f"""[project]
version = "0.0.0"

[tool.hitchhiker_module_control]
projects = {str(projects)}
version_toml = ["pyproject.toml:project.version"]
""")
        for project in projects:
            f.write(f"""
[tool.hitchhiker_module_control.project.{project}]
path = "{project}/"
version_variables = ["{project}/__init__.py:__version__"]
""")
    for project in projects:
        if not os.path.isdir(f"{repo.working_tree_dir}/{project}"):
            os.mkdir(f"{repo.working_tree_dir}/{project}")
        with open(f"{repo.working_tree_dir}/{project}/__init__.py", "w") as f:
            f.write("__version__ = \"0.0.0\"\n")


def create_random_file(repo, path = ""):
    fname = f"{repo.working_tree_dir}/{path}/{random.randint(0, 999999999)}"
    with open(fname, "w") as f:
        f.write(f"test file\n{fname}\n")
    repo.git.add(fname)


def create_commits(repo, commits):
    for commit in commits:
        for _ in range(0, random.randint(1, 5)):
            create_random_file(repo, commit[1])
        repo.git.commit(m=commit[0])


@pytest.fixture
def repo_empty(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1"])
    create_commits(repo, [["Initial commit", ""]])

    yield repo
    repo.close()


@pytest.fixture
def repo_one_fix(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1"])
    create_commits(repo, [["Initial commit", ""], ["fix: abcd", "project1"]])

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_one_breaking_change(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2"])
    create_commits(repo, [["Initial commit", ""], ["fix: something", "project2"], ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"], ["fix: something else", "project2"],])

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2", "1another_project", "2another_project"])
    create_commits(repo, [["Initial commit", ""], ["fix: something", "project1"], ["feat: abcd\n\nBREAKING CHANGE: some change", "/project2"], ["fix: something else", "/project2"], ["feat: some feature", "1another_project"], ["feat!: some feature that breaks things", "2another_project"]])

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2", "1another_project", "2another_project"])
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(repo, [["fix: something", "project1"], ["feat: abcd\n\nBREAKING CHANGE: some change", "project2"], ["fix: something else", "/project2"], ["feat: some feature", "1another_project"], ["feat!: some feature that breaks things", "2another_project"]])
    repo.git.tag("v1.0.0", m="v1.0.0")

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag_fix_after(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2", "1another_project", "2another_project"])
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(repo, [["fix: something", "/project1"], ["feat: abcd\n\nBREAKING CHANGE: some change", "/project2"], ["fix: something else", "/project2"], ["feat: some feature", "1another_project"], ["feat!: some feature that breaks things", "2another_project"]])
    repo.git.tag("v1.0.0", m="v1.0.0")
    create_commits(repo, [["fix: something", "project1"], ["fix: something else", "project2"]])

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_prerelease_tag(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2", "1another_project", "2another_project"])
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(repo, [["fix: something", "/project1"], ["feat: abcd\n\nBREAKING CHANGE: some change", "/project2"], ["fix: something else", "/project2"], ["feat: some feature", "1another_project"], ["feat!: some feature that breaks things", "2another_project"]])
    repo.git.tag("v1.0.0-rc.0", m="v1.0.0-rc.0")

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_prerelease_tag_fix_after(tmp_path_factory):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(repo, ["project1", "project2", "1another_project", "2another_project"])
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.0", m="v0.0.0")
    create_commits(repo, [["fix: something", "/project1"], ["feat: abcd\n\nBREAKING CHANGE: some change", "/project2"], ["fix: something else", "/project2"], ["feat: some feature", "1another_project"], ["feat!: some feature that breaks things", "2another_project"]])
    repo.git.tag("v1.0.0-rc.0", m="v1.0.0-rc.0")
    create_commits(repo, [["fix: something", "1another_project"], ["fix: something else", "project2"]])
    
    yield repo
    repo.close()
