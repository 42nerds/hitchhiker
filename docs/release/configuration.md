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

Path to subproject (used for determining which commits belong to the subproject)

#### `prerelease (bool)`

`true` if the subproject should be versioned as prerelease

#### `prerelease_token (str)`

Prerelease token like "rc", "alpha" etc.

#### `branch_match (str)`

Regex to match active branch name, if it doesn't match this subproject will be ignored.

## Example TOML configuration

```
[project]
version = "0.0.1"

[tool.hitchhiker]
projects = ["someproject"]
version_toml = ["pyproject.toml:project.version"]

[tool.hitchhiker.project.someproject]
path = "someproject/"
version_variables = ["someproject/__init__.py:__version__"]
prerelease = false
branch_match = "(master|main)"
```
