from enum import IntEnum


class VersionBump(IntEnum):
    """enum for version bump types"""
    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3
