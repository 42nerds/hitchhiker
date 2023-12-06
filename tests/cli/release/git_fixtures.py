import os
import random
import re

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


# regex from https://semver.org/spec/v2.0.0.html (modified to allow versions with a v at the start) and modified to only have a single capture group
_semver_group = (
    r"((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:(?:0|[1-9]\d*|\d*[a-zA-Z-]"
    r"[0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?:[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)"
)


def set_odoo_manifest_version(manifest_path, version):
    with open(
        manifest_path,
        "r+",
        encoding="utf-8",
    ) as f:
        contents = f.read()
        match = re.search(
            rf'^ *"version": ("{_semver_group}"),?$', contents, re.MULTILINE
        )
        assert match is not None, f'could not parse file "{manifest_path}"'
        contents = (
            contents[: match.span(1)[0]] + f'"{version}"' + contents[match.span(1)[1]:]
        )
        f.seek(0)
        f.write(contents)
        f.truncate(f.tell())


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
        msg = commit[0]
        projects = commit[1:]
        for _ in range(10):
            for project in projects:
                create_random_file(repo, project)
        repo.git.commit(m=msg)


def create_commits_fname(repo, commits):
    for commit in commits:
        msg = commit[0]
        fname = commit[1]
        projects = commit[2:]
        for project in projects:
            ffname = f"{repo.working_tree_dir}/{project}/{fname}"
            with open(ffname, "w") as f:
                f.write(f"test file\n{fname}\n")
            repo.git.add(ffname)
            create_random_file(repo, project)
        repo.git.commit(m=msg)


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
            ("another_project_name_with_feat", "1.2.3", False),
            ("project_name_with_feat", "2.3.4", False),
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
            ["fix: something else 2", "another_project_name_with_feat"],
            ["feat: something else 3", "project_name_with_feat"],
        ],
    )
    repo.git.tag("v1.0.0", m="v1.0.0")
    create_commits(
        repo,
        [
            ["fix: something", "project1"],
            ["fix: something else", "project2"],
            ["feat: another feature", "some_project_name_with_extra_feature"],
            ["fix: another fix", "project_name_with_feat"],
        ],
    )

    yield repo
    repo.close()


@pytest.fixture
def repo_multi_project_commits_before_tag_fix_after_odoo_diff_project_name_multibranch(
    tmp_path_factory,
):
    path = tmp_path_factory.mktemp("repo")
    repo = create_git_repo(path)
    create_configs(
        repo,
        [
            ("configurator", "0.1.1", False),
            ("configurator_delivery", "0.1.1", False),
            ("configurator_pim", "0.1.1", False),
            ("configurator_sale", "0.1.1", False),
            ("configurator_website_sale", "0.1.1", False),
            ("website_sale_improved_cart", "0.1.1", False),
        ],
        "0.0.1",
        is_odoo=True,
    )
    create_commits(repo, [["Initial commit", ""]])
    repo.git.tag("v0.0.1", m="v0.0.1")

    defaultbranch = repo.active_branch
    newbranch = repo.create_head("somebranch")
    newbranch.checkout()

    set_odoo_manifest_version(path / "configurator" / "__manifest__.py", "0.0.1")
    repo.git.add(path / "configurator" / "__manifest__.py")
    set_odoo_manifest_version(
        path / "configurator_delivery" / "__manifest__.py", "0.0.1"
    )
    repo.git.add(path / "configurator_delivery" / "__manifest__.py")
    set_odoo_manifest_version(path / "configurator_pim" / "__manifest__.py", "0.0.1")
    repo.git.add(path / "configurator_pim" / "__manifest__.py")
    set_odoo_manifest_version(path / "configurator_sale" / "__manifest__.py", "0.0.1")
    repo.git.add(path / "configurator_sale" / "__manifest__.py")
    set_odoo_manifest_version(
        path / "configurator_website_sale" / "__manifest__.py", "0.0.1"
    )
    repo.git.add(path / "configurator_website_sale" / "__manifest__.py")
    set_odoo_manifest_version(
        path / "website_sale_improved_cart" / "__manifest__.py", "0.0.1"
    )
    repo.git.add(path / "website_sale_improved_cart" / "__manifest__.py")

    repo.git.commit(m="version v0.2.0")
    repo.git.tag("v0.2.0", m="v0.2.0")

    defaultbranch.checkout()

    os.mkdir(repo.working_tree_dir + "/" + "configurator" + "/" + "models")
    os.mkdir(repo.working_tree_dir + "/" + "configurator_pim" + "/" + "models")
    create_commits_fname(
        repo,
        [
            [
                "fix: only sync standard odoo-products",
                "models/product_template.py",
                "configurator",
                "configurator_pim",
            ],
        ],
    )
    newbranch.checkout()
    repo.git.merge(defaultbranch.name, no_ff=True)

    defaultbranch.checkout()

    create_commits_fname(
        repo,
        [
            [
                "fix: another fix",
                "models/product_template.py",
                "configurator",
                "configurator_pim",
            ],
        ],
    )
    newbranch.checkout()
    repo.git.merge(defaultbranch.name, no_ff=True)

    yield repo
    repo.close()
