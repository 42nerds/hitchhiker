from __future__ import annotations

import os
import os.path
import re
import shutil
import tarfile
import tempfile
from typing import Any

import click
import github
import requests
import yaml  # type: ignore[import]

from hitchhiker.cli.modules.list import discover_modules
from hitchhiker.release.version import semver


# pylint: disable=R0901
class IndentDumper(yaml.Dumper):  # type: ignore[misc]
    def increase_indent(
        self, flow: bool = False, indentless: bool = False
    ) -> Any:  # the indentless argument is required
        return super().increase_indent(flow, False)


# pylint: disable=R0801
def _get_github_token(ctx: click.Context) -> str:
    if "GITHUB_TOKEN" not in os.environ and not ctx.obj["CONF"].has_key("GITHUB_TOKEN"):
        raise click.UsageError(
            "GitHub token not found, set the GITHUB_TOKEN environment variable or config option"
        )
    return os.environ.get(
        "GITHUB_TOKEN",
        (
            ctx.obj["CONF"].get_key("GITHUB_TOKEN")
            if ctx.obj["CONF"].has_key("GITHUB_TOKEN")
            else None
        ),
    )


_do_cached_download_cache: dict[str, str] = {}


def _do_cached_download(ctx: click.Context, url: str) -> str:
    """
    Returns:
        str: file path
    """
    if url not in _do_cached_download_cache:
        san_url = "".join(i for i in url if i not in "\\/:*?<>|")
        fname = f"tarball_{san_url}.tar.gz"
        req = requests.get(
            url,
            allow_redirects=True,
            headers={"Authorization": f"Bearer {_get_github_token(ctx)}"},
            timeout=30,
        )
        with open(fname, "wb") as f:  # type: ignore[assignment]
            f.write(req.content)  # type: ignore[arg-type]
        _do_cached_download_cache[url] = fname
    return _do_cached_download_cache[url]


def _clear_download_cache() -> None:
    """
    Deletes files downloaded with _do_cached_download
    """
    global _do_cached_download_cache  # pylint: disable=global-statement
    for fname in _do_cached_download_cache.values():
        os.remove(fname)
    _do_cached_download_cache = {}


def _tag_as_version(tag: str, odoo_version: int) -> semver.Version:
    tag_regex = rf"^{odoo_version}\.0-v?(\d+\.\d+\.\d+)$"
    return semver.Version().parse(
        re.match(tag_regex, tag).group(1)  # type: ignore[union-attr]
    )


_get_repo_latest_tag_cache: dict[str, tuple[str, str]] = {}


def _get_repo_latest_tag(
    ctx: click.Context, repo: str, odoo_version: int
) -> tuple[str, str]:
    """
    Retrieves the latest tag from a module repo

    Parameters:
        ctx (click.Context): The Click context object.

    Returns:
        tuple[str, str]: tuple[tagname, tgzurl].

    """
    cache_key = repo + str(odoo_version)
    if cache_key in _get_repo_latest_tag_cache:
        return _get_repo_latest_tag_cache[cache_key]

    try:
        gh = github.Github(_get_github_token(ctx))
        tags = gh.get_repo(repo).get_tags()
    except Exception as e:
        click.secho(
            "Error getting tags from GitHub. Is something wrong with your token?",
            err=True,
            fg="red",
        )
        raise e
    tag_regex = rf"^{odoo_version}\.0-v?(\d+\.\d+\.\d+)$"
    tags_sorted = sorted(
        list(filter(lambda r: re.match(tag_regex, r.name), tags)),
        key=lambda r: _tag_as_version(r.name, odoo_version),
        reverse=True,
    )
    if len(tags_sorted) == 0:
        errstr = f"No tags found in repo {repo} for odoo version {odoo_version}"
        click.secho(
            errstr,
            err=True,
            fg="red",
        )
        raise RuntimeError(errstr)

    tag = tags_sorted[0]

    _get_repo_latest_tag_cache[cache_key] = (tag.name, tag.tarball_url)
    return _get_repo_latest_tag_cache[cache_key]


@click.group("repo")
@click.pass_context
def repo_group(ctx: click.Context) -> None:
    """
    Commands related to Customer repos
    """
    ctx.ensure_object(dict)


@click.command(name="create", short_help="Create vogon.yaml and populate it")
@click.option(
    "--glob",
    is_flag=False,
    default="./**/__manifest__.py",
    help="module search path glob",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="overwrite the vogon.yaml even if it already exists",
)
@click.pass_context
def create_cmd(_ctx: click.Context, glob: str, overwrite: bool) -> None:
    """
    Creates vogon.yaml and populates it with modules found in the current working directory

    Parameters:
        --glob (str): The glob pattern to search for Odoo modules (default: `./**/__manifest__.py`).
        --overwrite (bool): allows overwriting the vogon.yaml

    """
    if not overwrite and os.path.isfile("vogon.yaml"):
        click.echo("vogon.yaml already exists and --overwrite is not set")
        return
    modules = discover_modules(glob)
    modules.sort(key=lambda x: x.get_int_name())
    click.echo("Creating vogon.yaml")
    with open("vogon.yaml", "w", encoding="utf-8") as f:
        mods = []
        for module in modules:
            mod = {}
            mod["name"] = module.get_int_name()
            path = str(os.path.dirname(module.get_dir()))
            if path != ".":
                mod["path"] = path
            mods.append(mod)
        f.write(
            """# Example:
#odoo_version: 17
#modules:
#  - name: test_abc
#    path: ./test_modules
#    git: 42nerds/module_test_inroot
#    git_tag: 17.0-v0.2.0
#    git_path: . # by default git path will be the same as the module name
#  - name: test_abcd
#    path: ./test_modules
#    use_latest: true # if true will always clone the latest version update it in the vogon.yaml. False by default
#    git: 42nerds/module_test
#    git_tag: 17.0-v0.0.1
#  - name: another_module
#    git: 42nerds/module_test
#    git_tag: 17.0-v0.1.0
#  - name: module_without_git
# Autogenerated from modules found in the current working directory:
"""
        )
        f.write("odoo_version: 0 # set this!!!\n")
        f.write(
            yaml.dump(
                {"modules": mods},
                indent=2,
                sort_keys=False,
                Dumper=IndentDumper,
                allow_unicode=True,
            )
        )


repo_group.add_command(create_cmd)


def _extract_tarball(ctx: click.Context, url: str, git_path: str, tgt_path: str) -> None:
    # extract the tar file to a temporary directory, then copy what we need and delete it again
    with tarfile.open(_do_cached_download(ctx, url)) as tar:
        # https://stackoverflow.com/a/43094365
        def remove_top_dir(tf: Any) -> Any:
            top = (
                os.path.commonprefix(tf.getnames()) + "/"
            )  # NOTE: works ONLY with module repos
            for member in tf.getmembers():
                if member.path.startswith(top):
                    member.path = member.path[len(top):]
                    yield member

        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(path=tmpdir, members=remove_top_dir(tar))
            if os.path.isdir(tgt_path):
                shutil.rmtree(tgt_path)
            shutil.copytree(tmpdir + "/" + git_path, tgt_path)


# prospector: disable=MC0001
# pylint: disable=R0901,R0914
@click.command(name="update", short_help="Update modules")
@click.option(
    "--module",
    is_flag=False,
    default=None,
    help="updates only one module",
)
@click.pass_context
def update_cmd(ctx: click.Context, module: str) -> None:
    """
    Finds the latest version for all modules in vogon.yaml and updates their versions in the file.
    Then it downloads each tarball and extracts it in the correct directory (if the version does not match)

    Parameters:
        --module (str): Update only a single module

    """
    if not os.path.isfile("vogon.yaml"):
        click.echo("no vogon.yaml found")
        return
    with open("vogon.yaml", "r", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    to_update = conf["modules"]
    if module is not None:
        try:
            to_update = [
                next(item for item in conf["modules"] if item["name"] == module)
            ]
        except StopIteration:
            click.echo(f"module {module} not found")
            return
    conf["modules"] = []  # we add the modules back into the list after we made changes.
    for mod in to_update:
        click.echo(f"processing {mod['name']}")
        repo = mod.get("git")
        if repo is None:  # no git repo set, continuing is pointless
            click.echo("    skipping.. No repo set")
            conf["modules"].append(mod)
            continue

        # initialize our paths
        mod_path = mod.get("path", ".") + "/" + mod["name"]
        git_path = mod.get("git_path", f"./{mod['name']}")

        # do we not want to upgrade the module?
        if not mod.get("use_latest"):
            # does the module not exist yet?
            if not os.path.isdir(mod_path):
                click.echo("    performing initial download")
                _extract_tarball(
                    ctx,
                    f"https://api.github.com/repos/{repo}/tarball/{mod['tag']}",
                    git_path,
                    mod_path,
                )
            else:
                click.echo("    skipping.. Already exists and no use_latest")
            conf["modules"].append(mod)
            continue

        # is there a newer version available?
        if (mod.get("tag") is not None) and (
            _tag_as_version(
                _get_repo_latest_tag(ctx, repo, conf["odoo_version"])[0],
                conf["odoo_version"],
            )
            <= _tag_as_version(mod["tag"], conf["odoo_version"])
        ):
            click.echo(f"    no newer tag in repo {repo}")
            conf["modules"].append(mod)
            continue
        new_tag, new_tar_url = _get_repo_latest_tag(ctx, repo, conf["odoo_version"])
        click.echo(f"    updating to {new_tag} from { mod.get('tag', 'no tag set')}")
        mod["tag"] = new_tag
        conf["modules"].append(mod)

        _extract_tarball(ctx, new_tar_url, git_path, mod_path)

    # clear the download cache
    _clear_download_cache()
    # write back to our config
    with open("vogon.yaml", "w", encoding="utf-8") as f:
        f.write(
            yaml.dump(
                conf,
                indent=2,
                sort_keys=False,
                Dumper=IndentDumper,
                allow_unicode=True,
            )
        )


repo_group.add_command(update_cmd)
