# Commands

## `hitchhiker release`

### Options:

#### `--workdir`

Working directory path. A git repository is expected to be found here.

#### `--config`

Configuration file path (relative to working directory).

## `hitchhiker release version`

Figures out the next version, updates it in all files, creates a commit and tags the commit with the next version.

### Options:

#### `--show`

Prints current versions and exits.

#### `--prerelease`

Main version will be done as prerelease.

#### `--prerelease-token`

Main version prerelease token.

#### `--push`

Will push to origin.

#### `--ghrelease`

Creates a github release (--push is required for this).
