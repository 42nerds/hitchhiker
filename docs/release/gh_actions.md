# GitHub Actions example

<!-- FIXME: This example is incorrect as we have not yet figured out how hitchhiker will be installed&updated -->

## Example workflow

```yaml
name: Version

on:
  push:
    branches:
      - "master"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd tool
          python setup.py egg_info
          pip install `grep -v '^\[' *.egg-info/requires.txt`
          pip install -e .
      - name: run hitchhiker
        run: |
          git config --global user.name "actions"
          git config --global user.email "username@users.noreply.github.com"
          GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} hitchhiker release --workdir ./ version --push --ghrelease
```
