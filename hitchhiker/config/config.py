import os
from pathlib import Path
import json


class ConfigManager:
    def _create_file_if_nonexistant(self, filepath):
        if not os.path.isfile(filepath):
            dirpath = Path(filepath).resolve().parent
            assert not os.path.isfile(dirpath)
            if not os.path.isdir(dirpath):
                os.mkdir(dirpath)
            open(filepath, "a").close()

    def _read_config(self):
        self._create_file_if_nonexistant(self._fpath)
        try:
            with open(self._fpath, "r") as f:
                return json.loads(f.read())
        except json.JSONDecodeError:
            with open(self._fpath, "w") as f:
                f.write(json.dumps(self._default_conf))
            return self._read_config()

    def _write_config(self):
        self._create_file_if_nonexistant(self._fpath)
        with open(self._fpath, "w") as f:
            f.write(json.dumps(self._confdict))

    def __init__(self, path, defaultconf):
        self._fpath = os.path.expanduser(path)
        self._default_conf = defaultconf
        self._confdict = self._read_config()

    def get_key(self, key):
        if key in self._confdict.keys():
            return self._confdict[key]
        if key in self._default_conf.keys():
            return self._default_conf[key]
        raise KeyError(key)

    def set_key(self, key, value):
        self._confdict[key] = value
        self._write_config()
