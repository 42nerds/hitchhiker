import hitchhiker.enums as enums

class CommitParser():
    def __init__(self, msg: str):
        pass

    def parse(self, msg: str):
        """initializes this class with the commit message passed in msg"""

    def get_version_bump(self):
        """returns how this commit should bump the version"""
        return enums.VersionBump.NONE
