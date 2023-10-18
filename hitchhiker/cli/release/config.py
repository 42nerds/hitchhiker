import re
import os
import glob as pyglob
from pathlib import Path
from typing import Dict, Any
import configparser
import git
from dotty_dict import Dotty  # type: ignore[import]
import tomlkit
import hitchhiker.release.version.semver as semver
import hitchhiker.odoo.module as odoo_mod


# regex from https://semver.org/spec/v2.0.0.html (modified to allow versions with a v at the start) and modified to only have a single capture group
_semver_group = (
    r"((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:(?:0|[1-9]\d*|\d*[a-zA-Z-]"
    r"[0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?:[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)"
)

# FIXME: Odoo manifest regex should be improved


def __get_version(config: Dict[str, Any], ctx: Dict[str, Any]) -> semver.Version:
    versions = []
    for var in ctx["version_variables"]:
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8"
        ) as f:
            match = re.search(
                rf'^{var[1]} ?= ?("{_semver_group}")$', f.read(), re.MULTILINE
            )
            assert match is not None, f'could not parse file "{var[0]}"'
            versions.append(semver.Version().parse(match.group(2)))
    for var in ctx["version_toml"]:
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8"
        ) as f:
            tomlconf = Dotty(tomlkit.parse(f.read()))
            versions.append(semver.Version().parse(tomlconf[var[1]]))
    for var in ctx["version_odoo_manifest"]:
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8"
        ) as f:
            match = re.search(
                rf'^ *"{var[1]}": ("{_semver_group}"),?$', f.read(), re.MULTILINE
            )
            assert match is not None, f'could not parse file "{var[0]}"'
            versions.append(semver.Version().parse(match.group(2)))
    for var in ctx["version_cfg"]:
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(config["repo"].working_tree_dir, var[0]))
        versions.append(semver.Version().parse(cfg[var[1]][var[2]]))
    versions.sort(reverse=True)
    if len(versions) != 0:
        return versions[0]
    return semver.Version()


def set_version(config: Dict[str, Any], ctx: Dict[str, Any]) -> list[str]:
    changedfiles = []
    for var in ctx["version_variables"]:
        changedfiles.append(var[0])
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]),
            "r+",
            encoding="utf-8",
        ) as f:
            contents = f.read()
            match = re.search(
                rf'^{var[1]} ?= ?("{_semver_group}")$', contents, re.MULTILINE
            )
            assert match is not None, f'could not parse file "{var[0]}"'
            contents = (
                contents[: match.span(1)[0]]
                + f"\"{str(ctx['version'])}\""
                + contents[match.span(1)[1] :]
            )
            f.seek(0)
            f.write(contents)
            f.truncate(f.tell())
    for var in ctx["version_toml"]:
        changedfiles.append(var[0])
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]),
            "r+",
            encoding="utf-8",
        ) as f:
            tomlconf = Dotty(tomlkit.parse(f.read()))
            tomlconf[var[1]] = str(ctx["version"])
            f.seek(0)
            f.write(tomlkit.dumps(tomlconf))
            f.truncate(f.tell())
    for var in ctx["version_odoo_manifest"]:
        changedfiles.append(var[0])
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]),
            "r+",
            encoding="utf-8",
        ) as f:
            contents = f.read()
            match = re.search(
                rf'^ *"{var[1]}": ("{_semver_group}"),?$', contents, re.MULTILINE
            )
            assert match is not None, f'could not parse file "{var[0]}"'
            contents = (
                contents[: match.span(1)[0]]
                + f"\"{str(ctx['version'])}\""
                + contents[match.span(1)[1] :]
            )
            f.seek(0)
            f.write(contents)
            f.truncate(f.tell())
    for var in ctx["version_cfg"]:
        changedfiles.append(var[0])
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(config["repo"].working_tree_dir, var[0]))
        with open(
            os.path.join(config["repo"].working_tree_dir, var[0]),
            "r+",
            encoding="utf-8",
        ) as f:
            cfg[var[1]][var[2]] = str(ctx["version"])
            cfg.write(f)
    return changedfiles


def __add_version_vars(
    conf: Dict[str, Any] | configparser.SectionProxy, project_ctx: Dict[str, Any]
) -> None:
    if "version_variables" in conf:
        for var in conf["version_variables"]:
            project_ctx["version_variables"].append(
                [var.split(":")[0], var.split(":")[1]]
            )
    if "version_toml" in conf:
        for var in conf["version_toml"]:
            project_ctx["version_toml"].append([var.split(":")[0], var.split(":")[1]])
    if "version_odoo_manifest" in conf:
        for var in conf["version_odoo_manifest"]:
            project_ctx["version_odoo_manifest"].append(
                [var.split(":")[0], var.split(":")[1]]
            )
    if "version_cfg" in conf:
        project_ctx["version_cfg"].append(conf["version_cfg"].split(":"))


def create_context_from_raw_config(
    tomlcfg: str, repo: git.repo.base.Repo, is_odoo: bool = False
) -> Dict[str, Any]:
    assert repo.working_tree_dir is not None
    ctx: Dict[str, Any] = {
        "projects": [],
        "version": semver.Version(),
        "repo": repo,
        "version_variables": [],
        "version_toml": [],
        "version_odoo_manifest": [],
        "version_cfg": [],
    }
    if not is_odoo:
        with open(tomlcfg, "r", encoding="utf-8") as f:
            tomlconf = Dotty(tomlkit.parse(f.read()))
        __add_version_vars(tomlconf["tool.hitchhiker"], ctx)
        assert (
            len(ctx["version_variables"])
            + len(ctx["version_toml"])
            + len(ctx["version_odoo_manifest"])
            + len(ctx["version_cfg"])
        ) > 0, "no version store location defined for main project"
        ctx["version"] = __get_version(ctx, ctx)
        if "tool.hitchhiker.projects" in tomlconf:
            for project in tomlconf["tool.hitchhiker.projects"]:
                conf = tomlconf[f"tool.hitchhiker.project.{project}"]
                project_ctx = {
                    "name": project,
                    "path": conf["path"],
                    "version": semver.Version(),
                    "prerelease": (
                        conf["prerelease"] if "prerelease" in conf else False
                    ),
                    "prerelease_token": (
                        conf["prerelease_token"] if "prerelease_token" in conf else "rc"
                    ),
                    "branch_match": (
                        conf["branch_match"]
                        if "branch_match" in conf
                        else "(main|master)"
                    ),
                    "version_variables": [],
                    "version_toml": [],
                    "version_odoo_manifest": [],
                    "version_cfg": [],
                }
                __add_version_vars(conf, project_ctx)
                project_ctx["version"] = __get_version(ctx, project_ctx)
                assert (
                    len(project_ctx["version_variables"])
                    + len(project_ctx["version_toml"])
                    + len(project_ctx["version_odoo_manifest"])
                    + len(project_ctx["version_cfg"])
                ) > 0, f"no version store location defined for project \"{project_ctx['name']}\""
                ctx["projects"].append(project_ctx)
    else:
        with open(tomlcfg, "r", encoding="utf-8") as f:
            cfg = configparser.ConfigParser()
            cfg.read(tomlcfg)
            __add_version_vars(cfg["tool.hitchhiker"], ctx)
            assert (
                len(ctx["version_variables"])
                + len(ctx["version_toml"])
                + len(ctx["version_odoo_manifest"])
                + len(ctx["version_cfg"])
            ) > 0, "no version store location defined for main project"
            ctx["version"] = __get_version(ctx, ctx)
            modules = odoo_mod.discover_modules(
                list(
                    filter(
                        lambda n: Path(n).name == "__manifest__.py",
                        pyglob.glob(
                            os.path.abspath(repo.working_tree_dir)
                            + "/*/__manifest__.py",
                            recursive=True,
                        ),
                    )
                )
            )
            for module in modules:
                project_ctx = {
                    "name": module.get_int_name(),
                    "path": os.path.join(
                        os.path.relpath(module.get_dir(), repo.working_tree_dir)
                    ),
                    "version": semver.Version(),
                    "prerelease": False,
                    "prerelease_token": "rc",
                    "branch_match": "(main|master)",
                    "version_variables": [],
                    "version_toml": [],
                    "version_odoo_manifest": [
                        [
                            os.path.join(
                                os.path.relpath(
                                    module.get_dir(), repo.working_tree_dir
                                ),
                                "__manifest__.py",
                            ),
                            "version",
                        ]
                    ],
                    "version_cfg": [],
                }
                project_ctx["version"] = __get_version(ctx, project_ctx)
                ctx["projects"].append(project_ctx)
            ctx["projects"] = sorted(ctx["projects"], key=lambda x: x["name"])
    return ctx
