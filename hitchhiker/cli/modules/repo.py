from __future__ import annotations

import os
import os.path
import json
import shutil
import tarfile
import tempfile
import hashlib
import copy
from typing import Any, Optional

import click
import requests
import yaml  # type: ignore[import]

# pylint: disable=R0901
# pylint: disable=R0801


def _get_github_token(ctx: click.Context) -> str:
    if "GITHUB_TOKEN" not in os.environ and not ctx.obj["CONF"].has_key("GITHUB_TOKEN"):
        raise click.UsageError(
            "GitHub token not found, set the GITHUB_TOKEN environment variable or config option"
        )
    return os.environ.get(
        "GITHUB_TOKEN",
        str(ctx.obj["CONF"].get_key("GITHUB_TOKEN")),
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
        req.raise_for_status()
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


@click.group("repo")
@click.pass_context
def repo_group(ctx: click.Context) -> None:
    """
    Commands related to Customer repos
    """
    ctx.ensure_object(dict)


@repo_group.command(name="create", short_help="Create sample vogon.yaml")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="overwrite the vogon.yaml even if it already exists",
)
@click.pass_context
def create_cmd(_ctx: click.Context, overwrite: bool) -> None:
    """
    Creates vogon.yaml and populates it with modules found in the current working directory

    Parameters:
        --overwrite (bool): allows overwriting the vogon.yaml

    """
    if not overwrite and os.path.isfile("vogon.yaml"):
        click.echo("vogon.yaml already exists and --overwrite is not set")
        return
    click.echo("Creating vogon.yaml")
    with open("vogon.yaml", "w", encoding="utf-8") as f:
        f.write(
            """## EXAMPLE:
# # for specifying entire repos of modules to pull, just a
# # shorthand instead of specifying a bunch of similar moudles entries
# module_groups:
#     - module_type: internal
#       modules:
#         configurator: {}
#         configurator_sale: {}
#         configurator_website_sale:
#           # the common attrs can be overridden here
#           path: ./module_shop_configurator/renamed_module_configurator_website_sale
#       common_attrs:
#         repo: module_shop_configurator
#         tag: 16.0-v0.14.4
# modules:
#   # internal is the quick and easy-to-read format for 42 N.E.R.D.S. style repos
#   # This basically just resolves into a modules entry with a bunch of default values that make sense for 42 N.E.R.D.S.
#   internal:
#     warranty_claims:
#       repo: module_warranty_claims
#       # currently, a commit or tag must be specified, it is impossible to specify just a branch
#       tag: 16.0-v0.5.0
#       # path: ./module_warranty_claims/warranty_claims # the default value is always repo name + / + name of module
#     warranty_claims_portal:
#       repo: module_warranty_claims
#       commit: a661f86bd1d9440d999bb407cfbf9d1e55466056
#     voip_placetel_enterprise:
#       repo: module_voip
#       commit: 5d4e56d64d51b50624e3b1fa0d7010110c6a976d
#       path: ./custom_path/voip_placetel_enterprise # we want to put this one in a path that is not the repo name

#   # in case you want to add e.g. a OCA module you must use this, longer, format for that one module.
#   external:
#     voip_placetel_standalone:
#       path: ./module_voip/voip_placetel_standalone
#       #source_path: test_abc # the default value for source_path is always the module name
#       source:
#         type: github_tarball
#         repo: 42nerds/module_voip
#         tag: 17.0-v0.4.0
#     sale_workflow_full:
#       path: ./thirdparty_modules/full_oca_sale_workflow
#       source_path: . # We want to pull all modules from this repo at once
#       source:
#         type: github_tarball
#         repo: OCA/sale-workflow
#         commit: 33436df12bb75f5fe2f6fbf090529871f4fb8928
#     partner_sale_pivot:
#       path: ./thirdparty/oca/partner_sale_pivot
#       source:
#         type: github_tarball
#         repo: OCA/sale-workflow
#         commit: b69ea9154864d5aa132f880a4ec33aa3f279fa20
"""
        )


def _extract_tarball_subdir(ctx: click.Context, url: str, path: str, tgt_path: str) -> None:
    print(url)
    # extract the tar file to a temporary directory, then copy what we need and delete it again
    with tarfile.open(_do_cached_download(ctx, url)) as tar:
        # https://stackoverflow.com/a/43094365
        def remove_top_dir(tf: Any) -> Any:
            top = (
                os.path.commonprefix(tf.getnames()) + "/"
            )
            for member in tf.getmembers():
                if member.path.startswith(top):
                    member.path = member.path[len(top):]
                    yield member

        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(path=tmpdir, members=remove_top_dir(tar))
            if os.path.isdir(tgt_path):
                shutil.rmtree(tgt_path)
            shutil.copytree(tmpdir + "/" + path, tgt_path)


def _get_vogon_yaml() -> dict[Any, Any]:
    # pylint: disable=too-many-branches
    def _parse_vogon_yaml(vogon: dict[Any, Any]) -> dict[Any, Any]:
        def merge_dicts_recursive(a: dict[Any, Any], b: dict[Any, Any]) -> dict[Any, Any]:
            # b overrides a
            for key, value in b.items():
                if key in a and isinstance(a[key], dict) and isinstance(value, dict):
                    a[key] = merge_dicts_recursive(a[key], value)
                else:
                    a[key] = value
            return a
        # add required keys and their default values
        # global
        for key, value in [("modules", {}), ("module_groups", [])]:  # type: ignore[var-annotated]
            if key not in vogon:
                vogon[key] = value
        # modules
        for key, value in [("external", {}), ("internal", {})]:
            if key not in vogon["modules"]:
                vogon["modules"][key] = value

        # resolve module_groups
        for group in vogon["module_groups"]:
            for mname, mattrs in group["modules"].items():
                if mname in vogon["modules"][group["module_type"]]:
                    raise RuntimeError("module from module_groups is already in modules")
                vogon["modules"][group["module_type"]][mname] = merge_dicts_recursive(
                    copy.deepcopy(group["common_attrs"]),
                    mattrs,
                )

        # convert repos specified in the internal shorthand format to the external format
        if "internal" in vogon["modules"]:
            for k, v in vogon["modules"]["internal"].items():
                if k in vogon["modules"]["external"]:
                    raise RuntimeError("duplicate module key")
                version_key = next((k for k in ('tag', 'branch', 'commit') if k in v))
                vogon["modules"]["external"][k] = {
                    "path": (v["repo"] + "/" + k) if "path" not in v else v["path"],
                    "source": {
                        "type": "github_tarball",
                        "repo": f"42nerds/{v['repo']}",
                        version_key: v[version_key],
                    },
                }
            del vogon["modules"]["internal"]

        # check if sources are valid
        for mod in vogon["modules"]["external"].values():
            if mod["source"]["type"] == "github_tarball":
                if "branch" in mod["source"]:
                    raise NotImplementedError("can't pull from branches, need a specific tag or commit")
                if "commit" in mod['source'] and "tag" in mod['source']:
                    raise RuntimeError("both commit and tag specified in source")
            else:
                raise NotImplementedError("unknown source type")

        # Insert default values for source_path
        for k, mod in dict(vogon["modules"]["external"]).items():
            if "source_path" not in mod:
                # the default value for source_path is always the module name
                vogon["modules"]["external"][k]["source_path"] = f"{k}"

        return vogon
    if not os.path.isfile("vogon.yaml"):
        raise RuntimeError("no vogon.yaml found")
    with open("vogon.yaml", "r", encoding="utf-8") as f:
        vogon = _parse_vogon_yaml(yaml.safe_load(f))
    return vogon


def _lockfile_set(module: str, key: str, value: str) -> None:
    if os.path.isfile("vogon-lock.json"):
        with open("vogon-lock.json", "r", encoding="utf-8") as f:
            lockfile = json.loads(f.read())
    else:
        lockfile = {}

    if "modules" not in lockfile:
        lockfile["modules"] = {}
    if module not in lockfile["modules"]:
        lockfile["modules"][module] = {}
    lockfile["modules"][module][key] = value

    with open("vogon-lock.json", "w", encoding="utf-8") as f:
        f.write(
            json.dumps(lockfile, indent=4, sort_keys=True)
        )


def _lockfile_get(module: str, key: str) -> Optional[Any]:
    if os.path.isfile("vogon-lock.json"):
        with open("vogon-lock.json", "r", encoding="utf-8") as f:
            lockfile = json.loads(f.read())
    else:
        return None

    if "modules" not in lockfile or module not in lockfile["modules"]:
        return None
    return lockfile["modules"][module].get(key, None)


def _hash_module_definition(name: str, mdef: dict[str, Any]) -> str:
    return hashlib.sha256(repr({"name": name, "mdef": mdef}).encode("utf-8")).hexdigest()


def _pretty_source_version(source: dict[str, Any]) -> str:
    if source["type"] != "github_tarball":
        raise NotImplementedError("unknown source type")
    return f"{source['repo']} version {source.get('tag') or source.get('commit')}"


@repo_group.command(name="sync", short_help="synchronize modules")
@click.option(
    "--module",
    is_flag=False,
    default=None,
    help="synchronizes only one module",
)
@click.pass_context
def sync(ctx: click.Context, module: str) -> None:
    """
    Synchronize.

    Looks at all (or one specified) module(s) in vogon.yaml, downloads their tarballs
    in their respective version and extracts them in the correct directory.

    The lockfile will also be updated.

    Parameters:
        --module (str): Sync only a single module

    """
    vogon = _get_vogon_yaml()
    if module is None:
        modules = vogon["modules"]["external"]
    else:
        modules = {module: vogon["modules"]["external"][module]}

    for name, mdef in modules.items():
        # currently only concrete versions are supported, so there
        # is no way the module definiton would be different for two different versions

        # We hash the whole module definition to include things like the paths, module name etc.
        # since if that changes we need to pull the module again anyway
        installed_hash = _lockfile_get(name, "installed_def_hash")
        to_be_installed_hash = _hash_module_definition(name, mdef)
        if installed_hash == to_be_installed_hash:
            print(f"{name}: up to date")
            continue
        print(f"{name}: updating")

        print(f"Downloading {_pretty_source_version(mdef['source'])}")

        if mdef['source']['type'] != "github_tarball":
            raise NotImplementedError("unknown source type")

        if mdef['source'].get('tag'):
            url = f"https://github.com/{mdef['source']['repo']}/archive/refs/tags/{mdef['source']['tag']}.tar.gz"
        else:
            url = f"https://github.com/{mdef['source']['repo']}/archive/{mdef['source']['commit']}.tar.gz"

        _extract_tarball_subdir(ctx, url, mdef["source_path"], mdef["path"])

        _lockfile_set(name, "installed_def_hash", to_be_installed_hash)

    _clear_download_cache()
