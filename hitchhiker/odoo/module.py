import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import hitchhiker.release.version.semver as semver


class Module:
    _manifest_dict: Dict[str, Any] = {}
    _int_name = ""
    _valid = False

    def __init__(self, manifest_path: str):
        """
        Initializes an Odoo module instance based on the provided manifest file.

        Parameters:
            manifest_path (str): The path to the manifest file.

        Returns:
            None

        Description:
        This method initializes an Odoo module instance by reading the manifest file located at the provided path.
        It sets the module directory, internal name, and manifest dictionary based on the contents of the manifest file.

        Example:
        ```
        module = Module(manifest_path)
        ```

        """
        self._moduledir = os.path.dirname(manifest_path)
        self._int_name = Path(manifest_path).resolve().parent.name
        with open(manifest_path) as f:
            d = ast.literal_eval(f.read())
            if isinstance(d, dict):
                self._valid = True  # TODO: check types of objects in dict
                self._manifest_dict = d

    def is_valid(self) -> bool:
        """
        Checks whether the Odoo module instance is valid.

        Returns:
            bool: True if the module is valid, False otherwise.

        Description:
        This method checks whether the Odoo module instance is valid by examining the internal state of the module.
        If the module was successfully initialized and has a valid manifest, it is considered valid.

        Example:
        ```
        is_valid = module.is_valid()
        ```

        """
        return self._valid

    def get_dir(self) -> str:
        """
        Gets the directory path of the Odoo module.

        Returns:
            str: The directory path of the module.

        Description:
        This method retrieves the directory path of the Odoo module.

        Example:
        ```
        module_dir = module.get_dir()
        ```

        """
        return self._moduledir

    def get_int_name(self) -> str:
        """
        Gets the internal name of the Odoo module.

        Returns:
            str: The internal name of the module.

        Description:
        This method retrieves the internal name of the Odoo module.
        If the module is not valid, an empty string is returned.

        Example:
        ```
        internal_name = module.get_int_name()
        ```

        """
        if not self.is_valid():
            return ""
        return self._int_name

    def get_readable_name(self) -> Optional[str]:
        """
        Gets the human-readable name of the Odoo module.

        Returns:
            Optional[str]: The human-readable name of the module, or None if not available.

        Description:
        This method retrieves the human-readable name of the Odoo module from its manifest.
        If the module is not valid or the manifest does not contain a name, it returns None.

        Example:
        ```
        readable_name = module.get_readable_name()
        ```

        """
        if not self.is_valid() or "name" not in self._manifest_dict:
            return None
        assert isinstance(
            self._manifest_dict["name"], str
        ), "invalid Odoo module manifest"
        return self._manifest_dict["name"]

    def get_version(self) -> Optional[semver.Version]:
        """
        Gets the semantic version of the Odoo module.

        Returns:
            Optional[semver.Version]: The semantic version of the module, or None if not available.

        Description:
        This method retrieves the semantic version of the Odoo module from its manifest.
        If the module is not valid or the manifest does not contain a version, it returns None.

        Example:
        ```
        module_version = module.get_version()
        ```

        """
        if not self.is_valid() or "version" not in self._manifest_dict:
            return None
        match = re.match(
            r"^v?(?:\d+\.\d+\.)?v?(\d+\.\d+\.\d+)$", self._manifest_dict["version"]
        )
        if match is None:
            return None
        return semver.Version().parse(match.group(1))


def discover_modules(files: list[str]) -> list[Module]:
    """
    Discovers Odoo modules from the specified list of file paths.

    Args:
        files (list[str]): A list of file paths to search for module manifest files.

    Returns:
        list[Module]: List of discovered Odoo modules.

    Description:
    This function searches for module manifest files in the specified list of file paths and creates a list of Odoo modules.
    It returns a list of valid Odoo module instances.

    Example:
    ```
    modules = discover_modules(["path/to/modules/module1/__manifest__.py", "path/to/modules/module2/__manifest__.py"])
    ```

    """
    modules = []
    for fname in files:
        if "vendor/" in fname:
            continue
        module = Module(fname)
        if not module.is_valid():
            continue
        modules.append(module)

    return modules
