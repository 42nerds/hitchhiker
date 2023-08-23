import re
import hitchhiker_module_control.enums as enums
import hitchhiker_module_control.regex as regex

class Version():
    """Class for parsing and bumping semantic versions"""
    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str = None
    buildmeta: str = None

    def __init__(self):
        pass

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}{'-' + self.prerelease if self.prerelease is not None else ''}"

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}{'-' + self.prerelease if self.prerelease is not None else ''}{'+' + self.buildmeta if self.buildmeta is not None else ''}"

    def __eq__(self, obj):
        return self.major == obj.major and self.minor == obj.minor and self.patch == obj.patch and self.prerelease == obj.prerelease

    # TODO: fix this cursed mess
    def __lt__(self, obj):
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

        for selfid, objid in zip(self.prerelease.split("."), obj.prerelease.split(".")):
            if selfid == objid:
                continue
            # Identifiers consisting of only digits are compared numerically.
            if selfid.isnumeric() and objid.isnumeric():
                return int(selfid) < int(objid)

            # Numeric identifiers always have lower precedence than non-numeric identifiers.
            if (selfid.isnumeric() and (not objid.isnumeric())) or (objid.isnumeric() and (not selfid.isnumeric())):
                return selfid.isnumeric()

            # Identifiers with letters or hyphens are compared lexically in ASCII sort order
            for selfl, objl in zip(selfid, objid):
                if selfl != objl:
                    return ord(selfl) < ord(objl)

        # A larger set of pre-release fields has a higher precedence than a smaller set, if all of the preceding identifiers are equal.
        if len(self.prerelease.split(".")) != len(obj.prerelease.split(".")):
            return len(self.prerelease.split(".")) < len(obj.prerelease.split("."))

        # it should be _impossible_ to get here!

    def parse(self, version: str):
        """Parses semantic version string"""
        # regex from https://semver.org/spec/v2.0.0.html (modified to allow versions with a v at the start)
        match = re.match(regex.semver_parse, version)
        if match is None:
            self.major = 0
            self.minor = 0
            self.patch = 0
            self.prerelease = None
            self.buildmeta = None
            return self
        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.prerelease = match.group(4)
        self.buildmeta = match.group(5)
        return self

    def bump(self, bump: enums.VersionBump):
        """Bumps version by amount specified in VersionBump enum"""
        if bump == enums.VersionBump.MAJOR:
            self.major += 1
            self.minor = self.patch = 0
        elif bump == enums.VersionBump.MINOR:
            self.minor += 1
            self.patch = 0
        elif bump == enums.VersionBump.PATCH:
            self.patch += 1
        return self

    def bump_prerelease(self):
        if self.prerelease is None:
            self.prerelease = "rc.0"
        else:
            match = re.match(r"^rc\.(\d+)$", self.prerelease)
            if match is None:
                self.prerelease = "rc.0"
            else:
                print(match.group(1))
                self.prerelease = f"rc.{int(match.group(1)) + 1}"
        return self

    def remove_prerelease_and_buildmeta(self):
        self.buildmeta = None
        self.prerelease = None
        return self
