import re
from typing import Optional, Self
import hitchhiker.release.enums as enums


# regex from https://semver.org/spec/v2.0.0.html (modified to allow versions with a v at the start)
_semver_parse = (
    r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class Version:
    """Class for parsing and bumping semantic versions"""

    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: Optional[str] = None
    buildmeta: Optional[str] = None

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.

        Description:
        This method initializes a new instance of the class. In this specific implementation,
        the method does not perform any actions and simply passes without any further operations.

        Example:
        ```
        instance = ClassName()
        ```

        """
        pass

    def __str__(self) -> str:
        """
        Returns a string representation of the version.

        Returns:
            str: The string representation of the version.

        Description:
        This method returns a string representation of the version in the format "major.minor.patch-prerelease"
        if there's a prerelease, or "major.minor.patch" if there's no prerelease.

        Example:
        ```
        version_str = str(version)
        ```

        """
        return f"{self.major}.{self.minor}.{self.patch}{'-' + self.prerelease if self.prerelease is not None else ''}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the version.

        Returns:
            str: The string representation of the version.

        Description:
        This method returns a string representation of the version in the format "major.minor.patch-prerelease+buildmeta"
        if both prerelease and buildmeta are present, "major.minor.patch-prerelease" if there's a prerelease only,
        "major.minor.patch+buildmeta" if there's a buildmeta only, or "major.minor.patch" if there are none.

        Example:
        ```
        version_repr = repr(version)
        ```

        """
        return (
            f"{self.major}.{self.minor}.{self.patch}{'-' + self.prerelease if self.prerelease is not None else ''}"
            f"{'+' + self.buildmeta if self.buildmeta is not None else ''}"
        )

    def __eq__(self, obj: object) -> bool:
        """
        Checks if this version is equal to another version.

        Parameters:
            obj (object): The object to compare with.

        Returns:
            bool: True if this version is equal to the specified version, False otherwise.

        Description:
        This method compares this version with another version to check if they are equal.
        Two versions are considered equal if their major, minor, patch, and prerelease components match.

        Example:
        ```
        is_equal = version1 == version2
        ```

        """
        if not isinstance(obj, Version):
            return NotImplemented
        return (
            self.major == obj.major
            and self.minor == obj.minor
            and self.patch == obj.patch
            and self.prerelease == obj.prerelease
        )

    def __ver_lt(self, obj: object) -> Optional[bool]:
        """
        Compares this version to another version to determine if it's less than.

        Parameters:
            obj (object): The object to compare with.

        Returns:
            bool: True if this version is less than the specified version, False if greater, None if equal.

        Description:
        This method compares this version with another version to determine if it's less than the specified version.
        A version is considered less than another if its major, minor, or patch components are lower.
        If the prerelease components are equal, a version with prerelease is considered less than one without.
        Returns None if the versions are equal.

        Example:
        ```
        is_less_than = version1.__ver_lt(version2)
        ```

        """
        if not isinstance(obj, Version):
            return NotImplemented
        if self.major < obj.major:
            return True
        elif self.major > obj.major:
            return False
        elif self.minor < obj.minor:
            return True
        elif self.minor > obj.minor:
            return False
        elif self.patch < obj.patch:
            return True
        elif self.patch > obj.patch:
            return False

        # if both prerelease strings are equal (or both none) the version is equal
        if self.prerelease == obj.prerelease:
            return False

        # a version that has a prerelease is lower than one without
        if self.prerelease is None or obj.prerelease is None:
            return self.prerelease is not None

        return None

    def __prerelease_lt(self, obj: object) -> bool:
        """
        Compares the prerelease component of this version to another version's prerelease component.

        Parameters:
            obj (object): The object to compare with.

        Returns:
            bool: True if this version's prerelease is less than the specified version's prerelease.

        Description:
        This method compares the prerelease component of this version to the prerelease component of another version.
        It follows the Semantic Versioning specification for comparing prerelease identifiers.

        Example:
        ```
        is_less_than_prerelease = version1.__prerelease_lt(version2)
        ```

        """
        if not isinstance(obj, Version):
            return NotImplemented
        assert self.prerelease is not None
        assert obj.prerelease is not None
        for selfid, objid in zip(self.prerelease.split("."), obj.prerelease.split(".")):
            if selfid == objid:
                continue
            # Identifiers consisting of only digits are compared numerically.
            if selfid.isnumeric() and objid.isnumeric():
                return int(selfid) < int(objid)

            # Numeric identifiers always have lower precedence than non-numeric identifiers.
            if (selfid.isnumeric() and (not objid.isnumeric())) or (
                objid.isnumeric() and (not selfid.isnumeric())
            ):
                return selfid.isnumeric()

            # Identifiers with letters or hyphens are compared lexically in ASCII sort order
            for selfl, objl in zip(selfid, objid):
                if selfl != objl:
                    return ord(selfl) < ord(objl)

        # A larger set of pre-release fields has a higher precedence than a smaller set, if all of the preceding identifiers are equal.
        if len(self.prerelease.split(".")) != len(obj.prerelease.split(".")):
            return len(self.prerelease.split(".")) < len(obj.prerelease.split("."))

        # it should be _impossible_ to get here!
        raise Exception("unreachable")

    def __lt__(self, obj: object) -> bool:
        """
        Checks if this version is less than another version.

        Parameters:
            obj (object): The object to compare with.

        Returns:
            bool: True if this version is less than the specified version, False otherwise.

        Description:
        This method checks if this version is less than another version.
        It first compares the major, minor, and patch components, and then the prerelease component if necessary.

        Example:
        ```
        is_less_than = version1.__lt__(version2)
        ```

        """
        if not isinstance(obj, Version):
            return NotImplemented
        ver_lt = self.__ver_lt(obj)
        if ver_lt is not None:
            return ver_lt

        return self.__prerelease_lt(obj)

    def parse(self, version: str) -> Self:
        """
        Parses a semantic version string and updates the Version object.

        Parameters:
            version (str): The semantic version string to parse.

        Returns:
            Self: The updated Version object after parsing.

        Description:
        This method parses a semantic version string in the format "major.minor.patch-prerelease+buildmeta"
        and updates the Version object with the parsed components.
        If the version string is invalid, it raises a RuntimeError and sets all components to 0 and None.

        Example:
        ```
        version = Version()
        version.parse("1.2.3-alpha+001")
        ```

        """
        match = re.match(_semver_parse, version)
        if match is None:
            self.major = 0
            self.minor = 0
            self.patch = 0
            self.prerelease = None
            self.buildmeta = None
            raise RuntimeError(f'error parsing version "{version}"')
        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.prerelease = match.group(4)
        self.buildmeta = match.group(5)
        return self

    def bump(
        self,
        bump: enums.VersionBump,
        prerelease: bool = False,
        prerelease_token: str = "rc",
    ) -> Self:
        """
        Bumps the version by the specified amount.

        Parameters:
            bump (enums.VersionBump): The type of bump to perform.
            prerelease (bool): Whether to perform a prerelease bump (default: False).
            prerelease_token (str): The prerelease token to use (default: "rc").

        Returns:
            Self: The updated Version object after the bump.

        Description:
        This method bumps the version by the specified amount according to the VersionBump enum.
        It can perform major, minor, or patch bumps. It can also perform prerelease bumps.
        If prerelease is True and the last version was not a prerelease, it bumps before making it a prerelease.
        If prerelease is False and the last version was a prerelease, it makes the next one a full release (unless bump is major).
        The prerelease_token is used for prerelease bumps.

        Example:
        ```
        version = Version()
        version.bump(enums.VersionBump.MINOR)
        ```

        """
        # if last version was not a prerelease bump it before making it one
        if (
            prerelease
            and bump != enums.VersionBump.NONE
            and bump != enums.VersionBump.MAJOR
            and self.prerelease is None
        ):
            self.bump(bump, False)
        # if the last version was a prerelease make the next one a full release (unless bump is major)
        if not prerelease and self.prerelease is not None:
            self.prerelease = None
            if bump != enums.VersionBump.MAJOR:
                return self
        if bump == enums.VersionBump.MAJOR:
            self.major += 1
            self.minor = self.patch = 0
            if prerelease:
                self.prerelease = f"{prerelease_token}.1"
        elif bump == enums.VersionBump.MINOR and not prerelease:
            self.minor += 1
            self.patch = 0
        elif bump == enums.VersionBump.PATCH and not prerelease:
            self.patch += 1
        elif prerelease and bump is not enums.VersionBump.NONE:
            if self.prerelease is None:
                self.prerelease = f"{prerelease_token}.1"
            else:
                match = re.match(rf"^{prerelease_token}\.(\d+)$", self.prerelease)
                if match is None:
                    self.prerelease = f"{prerelease_token}.1"
                else:
                    self.prerelease = f"{prerelease_token}.{int(match.group(1)) + 1}"
        return self
