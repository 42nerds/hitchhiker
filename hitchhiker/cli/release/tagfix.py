import re
from typing import Dict, Any


def get_tag_without_branch(config: Dict[str, Any], tag: str) -> str:
    if not config["prepend_branch_to_tag"]:
        return tag
    match = re.match(rf"([^-]+)-(.+)", tag)
    return match.group(2) if match is not None else tag


def add_branch_to_tag(config: Dict[str, Any], version: str) -> str:
    if not config["prepend_branch_to_tag"]:
        return version
    branch = str(config["repo"].active_branch)
    return f"{branch}-{version}"
