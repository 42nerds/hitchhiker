import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    def _create_file_if_nonexistant(self, filepath: str) -> None:
        """
        Create a file if it doesn't already exist at the specified filepath.
        Also create all directories in the path.

        Parameters:
            filepath (str): The path to the file to be created.

        Returns:
            None
        """
        if not os.path.isfile(filepath):
            dirpath = Path(filepath).resolve().parent
            Path(dirpath).mkdir(parents=True, exist_ok=True)
            Path(filepath).touch()

    def _read_config(self) -> Dict[str, Any]:
        """
        Read the configuration from a file and return it as a dictionary.
        If the file doesn't exist or is not valid JSON, create a new file with default configuration.

        Returns:
            dict: The configuration as a dictionary.
        """
        self._create_file_if_nonexistant(self._fpath)
        try:
            with open(self._fpath, "r", encoding="utf-8") as f:
                read = json.loads(f.read())
                assert isinstance(read, Dict)
                return read
        except json.JSONDecodeError:
            with open(self._fpath, "w", encoding="utf-8") as f:
                f.write(json.dumps(self._default_conf))
            return self._read_config()

    def _write_config(self) -> None:
        """
        Write the configuration dictionary to a file in JSON format.

        Returns:
            None
        """
        self._create_file_if_nonexistant(self._fpath)
        with open(self._fpath, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._confdict))

    def __init__(self, path: str, defaultconf: Dict[str, Any]):
        """
        Initialize a ConfigManager instance with the specified file path and default configuration.

        Parameters:
            path (str): The path to the configuration file.
            defaultconf (dict): The default configuration as a dictionary.

        Returns:
            None
        """
        self._fpath = os.path.expanduser(path)
        self._default_conf = defaultconf
        self._confdict = self._read_config()

        # append new default config keys to config
        for key in self._default_conf.keys():
            if key not in self._confdict.keys():
                self.set_key(key, self._default_conf[key])

    def get_key(self, key: str) -> Any:
        """
        Retrieve the value associated with the specified key from the configuration.

        Parameters:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the specified key.

        Raises:
            KeyError: If the key does not exist in the configuration.
        """
        if key in self._confdict.keys():
            return self._confdict[key]
        raise KeyError(key)

    def set_key(self, key: str, value: Any) -> None:
        """
        Set the specified key to the provided value in the configuration and write to the file.

        Parameters:
            key (str): The key to set the value for.
            value (Any): The value to associate with the key.

        Returns:
            None
        """
        self._confdict[key] = value
        self._write_config()

    def has_key(self, key: str) -> bool:
        """
        Check if the specified key exists in the configuration.

        Parameters:
            key (str): The key to check for existence.

        Returns:
            bool: True if the key exists in the configuration, False otherwise.
        """
        return key in self._confdict.keys()
