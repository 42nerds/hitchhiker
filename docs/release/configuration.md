# Configuration

Release uses a TOML configuration, the configuration file can be specified with the --config option, the default is `pyproject.toml`.

## Environment variables

- `GITHUB_TOKEN` GitHub API token, used to create releases on GitHub. Can also be specified with argument.

## TOML config options

### `[tool.hitchhiker]`

#### `projects (List[str])`

List of subprojects.

#### `version_toml (List[str])`

version variable in TOML file - string like `filename:variable` example: `pyproject.toml:project.version`.

#### `version_variables (List[str])`

version variable in python file - string like `filename:variable` example: `__init__.py:__version__`. **This variable must be global!**

#### `version_odoo_manifest (List[str])`

version variable in odoo manifest file (python dictionary) - string like `filename:variable` example: `__manifest__.py:version`.

### `[tool.hitchhiker.project.subprojectname]`

Each subproject has the same version variable options as the main project - `version_toml (List[str])`, `version_variables (List[str])` and `version_odoo_manifest (List[str])`

#### `path (str)`

**Required**

Path to subproject (used for determining which commits belong to the subproject)

#### `prerelease (bool)`

Default: `false`

`true` if the subproject should be versioned as prerelease

#### `prerelease_token (str)`

Default: `rc`

Prerelease token like "rc", "alpha" etc.

#### `branch_match (str)`

Default: `(.+)`

Regex to match active branch name, if it doesn't match this subproject will be ignored.

#### `prepend_branch_to_tag (bool)`

Default: `false`

`true` if the branch should be prepended to the tag like master-v1.2.3

## Example TOML configuration

```
[project]
version = "0.0.1"

[tool.hitchhiker]
projects = ["someproject"]
version_toml = ["pyproject.toml:project.version"]
prepend_branch_to_tag = true

[tool.hitchhiker.project.someproject]
path = "someproject/"
version_variables = ["someproject/__init__.py:__version__"]
prerelease = false
branch_match = "(main|master)"
```

## Example setup.cfg configuration

If setup.cfg is used odoo modules will be automatically discovered.

```
[tool.hitchhiker]
project_version = 1.2.3
version_cfg = setup.cfg:tool.hitchhiker:project_version
prepend_branch_to_tag = true
branch_match = (main|master)
```
