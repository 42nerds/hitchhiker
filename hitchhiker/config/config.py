import os
from typing import Dict, Any
from pathlib import Path
import json


class ConfigManager:
    def _create_file_if_nonexistant(self, filepath: str) -> None:
        if not os.path.isfile(filepath):
            dirpath = Path(filepath).resolve().parent
            assert not os.path.isfile(dirpath)
            if not os.path.isdir(dirpath):
                os.mkdir(dirpath)
            open(filepath, "a").close()

    def _read_config(self) -> Dict[str, Any]:
        self._create_file_if_nonexistant(self._fpath)
        try:
            with open(self._fpath, "r") as f:
                read = json.loads(f.read())
                assert isinstance(read, Dict)
                return read
        except json.JSONDecodeError:
            with open(self._fpath, "w") as f:
                f.write(json.dumps(self._default_conf))
            return self._read_config()

    def _write_config(self) -> None:
        self._create_file_if_nonexistant(self._fpath)
        with open(self._fpath, "w") as f:
            f.write(json.dumps(self._confdict))

    def __init__(self, path: str, defaultconf: Dict[str, Any]):
        self._fpath = os.path.expanduser(path)
        self._default_conf = defaultconf
        self._confdict = self._read_config()

        # append new default config keys to config
        for key in self._default_conf.keys():
            if key not in self._confdict.keys():
                self.set_key(key, self._default_conf[key])

    def get_key(self, key: str) -> Any:
        if key in self._confdict.keys():
            return self._confdict[key]
        raise KeyError(key)

    def set_key(self, key: str, value: Any) -> None:
        self._confdict[key] = value
        self._write_config()

    def has_key(self, key: str) -> bool:
        return key in self._confdict.keys()
