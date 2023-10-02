import os
from pathlib import Path
import glob as pyglob
import ast
import hitchhiker.release.version.semver as semver


def discover_modules(glob: str):
    modules = []
    modulefiles = list(
        filter(
            lambda n: Path(n).name == "__manifest__.py",
            pyglob.glob(glob, recursive=True),
        )
    )
    for fname in modulefiles:
        module = Module(fname)
        if not module.is_valid():
            continue
        modules.append(module)

    return modules


class Module:
    _manifest_dict = {}
    _int_name = ""
    _valid = False

    def __init__(self, manifest_path):
        self._moduledir = os.path.dirname(manifest_path)
        self._int_name = Path(manifest_path).resolve().parent.name
        with open(manifest_path) as f:
            d = ast.literal_eval(f.read())
            if isinstance(d, dict):
                self._valid = True
                self._manifest_dict = d

    def is_valid(self):
        return self._valid

    def get_dir(self):
        return self._moduledir

    def get_int_name(self):
        if not self.is_valid():
            return None
        return self._int_name

    def get_readable_name(self):
        if not self.is_valid() or "name" not in self._manifest_dict:
            return None
        return self._manifest_dict["name"]

    def get_version(self):
        if not self.is_valid() or "version" not in self._manifest_dict:
            return None
        return semver.Version().parse(self._manifest_dict["version"])
