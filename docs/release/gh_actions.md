# GitHub Actions example

## Example workflow

```yaml
name: Version

on:
  push:
    branches:
      - "main"
      - "master"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install hitchhiker
        run: |
          pip install "hitchhiker[release] @ git+https://github.com/42nerds/hitchhiker.git@main"
      - name: run hitchhiker
        run: |
          git config --global user.name "actions"
          git config --global user.email "username@users.noreply.github.com"
          GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} hitchhiker release --workdir ./ version --push --ghrelease
```
