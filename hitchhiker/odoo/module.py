import os
from typing import Dict, Any, Optional
from pathlib import Path
import ast
import hitchhiker.release.version.semver as semver


class Module:
    _manifest_dict: Dict[str, Any] = {}
    _int_name = ""
    _valid = False

    def __init__(self, manifest_path: str):
        self._moduledir = os.path.dirname(manifest_path)
        self._int_name = Path(manifest_path).resolve().parent.name
        with open(manifest_path) as f:
            d = ast.literal_eval(f.read())
            if isinstance(d, dict):
                self._valid = True  # TODO: check types of objects in dict
                self._manifest_dict = d

    def is_valid(self) -> bool:
        return self._valid

    def get_dir(self) -> str:
        return self._moduledir

    def get_int_name(self) -> str:
        if not self.is_valid():
            return ""
        return self._int_name

    def get_readable_name(self) -> Optional[str]:
        if not self.is_valid() or "name" not in self._manifest_dict:
            return None
        assert isinstance(
            self._manifest_dict["name"], str
        ), "invalid Odoo module manifest"
        return self._manifest_dict["name"]

    def get_version(self) -> Optional[semver.Version]:
        if not self.is_valid() or "version" not in self._manifest_dict:
            return None
        return semver.Version().parse(self._manifest_dict["version"])


def discover_modules(files: list[str]) -> list[Module]:
    modules = []
    for fname in files:
        module = Module(fname)
        if not module.is_valid():
            continue
        modules.append(module)

    return modules
