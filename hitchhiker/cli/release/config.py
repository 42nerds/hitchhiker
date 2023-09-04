import re
import os
import git
from dotty_dict import Dotty
import tomlkit
import hitchhiker.release.version.semver as semver
import hitchhiker.release.regex as regex


def __get_version(config, ctx):
    versions = []
    for var in ctx["version_variables"]:
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8") as f:
            match = re.search(
                rf'^{var[1]} ?= ?("{regex.semver_group}")$', f.read(), re.MULTILINE)
            assert match is not None, f"could not parse file \"{var[0]}\""
            versions.append(semver.Version().parse(match.group(2)))
    for var in ctx["version_toml"]:
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8") as f:
            tomlconf = Dotty(tomlkit.parse(f.read()))
            versions.append(semver.Version().parse(tomlconf[var[1]]))
    for var in ctx["version_odoo_manifest"]:
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r", encoding="utf-8") as f:
            match = re.search(
                rf'^    "{var[1]}": ("{regex.semver_group}"),?$', f.read(), re.MULTILINE)
            assert match is not None, f"could not parse file \"{var[0]}\""
            versions.append(semver.Version().parse(match.group(2)))
    versions.sort(reverse=True)
    if len(versions) != 0:
        return versions[0]
    return semver.Version()

def set_version(config, ctx):
    changedfiles = []
    for var in ctx["version_variables"]:
        changedfiles.append(var[0])
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r+", encoding="utf-8") as f:
            contents = f.read()
            match = re.search(
                rf'^{var[1]} ?= ?("{regex.semver_group}")$', contents, re.MULTILINE)
            assert match is not None, f"could not parse file \"{var[0]}\""
            contents = contents[:match.span(
                1)[0]] + f"\"{str(ctx['version'])}\"" + contents[match.span(1)[1]:]
            f.seek(0)
            f.write(contents)
            f.truncate(f.tell())
    for var in ctx["version_toml"]:
        changedfiles.append(var[0])
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r+", encoding="utf-8") as f:
            tomlconf = Dotty(tomlkit.parse(f.read()))
            tomlconf[var[1]] = str(ctx['version'])
            f.seek(0)
            f.write(tomlkit.dumps(tomlconf))
            f.truncate(f.tell())
    for var in ctx["version_odoo_manifest"]:
        changedfiles.append(var[0])
        with open(os.path.join(config["repo"].working_tree_dir, var[0]), "r+", encoding="utf-8") as f:
            contents = f.read()
            match = re.search(
                rf'^    "{var[1]}": ("{regex.semver_group}"),?$', contents, re.MULTILINE)
            assert match is not None, f"could not parse file \"{var[0]}\""
            contents = contents[:match.span(
                    1)[0]] + f"\"{str(ctx['version'])}\"" + contents[match.span(1)[1]:]
            f.seek(0)
            f.write(contents)
            f.truncate(f.tell())
    return changedfiles

def __add_version_vars(conf, project_ctx):
    if "version_variables" in conf:
        for var in conf["version_variables"]:
            project_ctx["version_variables"].append(
            [var.split(":")[0], var.split(":")[1]])
    if "version_toml" in conf:
        for var in conf["version_toml"]:
            project_ctx["version_toml"].append(
            [var.split(":")[0], var.split(":")[1]])
    if "version_odoo_manifest" in conf:
        for var in conf["version_odoo_manifest"]:
            project_ctx["version_odoo_manifest"].append(
            [var.split(":")[0], var.split(":")[1]])

def create_context_from_raw_config(tomlcfg: str, repo: git.Repo):
    ctx = {"projects": [], "version": semver.Version(), "repo": repo, "version_variables": [], "version_toml": [], "version_odoo_manifest": []}
    with open(tomlcfg, "r", encoding="utf-8") as f:
        tomlconf = Dotty(tomlkit.parse(f.read()))
    __add_version_vars(tomlconf["tool.hitchhiker"], ctx)
    assert (len(ctx["version_variables"]) + len(ctx["version_toml"]) + len(ctx["version_odoo_manifest"])
            ) > 0,"no version store location defined for main project"
    ctx["version"] = __get_version(ctx, ctx)
    if "tool.hitchhiker.projects" in tomlconf:
        for project in tomlconf["tool.hitchhiker.projects"]:
            conf = tomlconf[f"tool.hitchhiker.project.{project}"]
            project_ctx = {"name": project, "path": conf["path"], "version": semver.Version(), "prerelease": (conf["prerelease"] if "prerelease" in conf else False), "prerelease_token": (conf["prerelease_token"] if "prerelease_token" in conf else "rc"), "version_variables": [], "version_toml": [], "version_odoo_manifest": []}
            __add_version_vars(conf, project_ctx)
            project_ctx["version"] = __get_version(ctx, project_ctx)
            assert (len(project_ctx["version_variables"]) + len(project_ctx["version_toml"]) + len(project_ctx["version_odoo_manifest"])) > 0, f"no version store location defined for project \"{project_ctx['name']}\""
            ctx["projects"].append(project_ctx)
    return ctx
