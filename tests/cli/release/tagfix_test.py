from hitchhiker.cli.release.tagfix import get_tag_without_branch, add_branch_to_tag


class _mockclass:
    active_branch = ""

    def __init__(self, branch):
        self.active_branch = branch


def test_get_tag_without_branch():
    """test for get_tag_without_branch"""
    conf = {"prepend_branch_to_tag": False, "repo": _mockclass("somebranch")}
    assert (
        get_tag_without_branch(conf, "tagfix-should-ignore_this")
        == "tagfix-should-ignore_this"
    )
    conf = {"prepend_branch_to_tag": True, "repo": _mockclass("somebranch")}
    assert get_tag_without_branch(conf, "somebranch-v1.2.3") == "v1.2.3"
    assert get_tag_without_branch(conf, "somebranch-v1.2.3-rc.1") == "v1.2.3-rc.1"
    assert get_tag_without_branch(conf, "somebranch-1.2.3-rc.1") == "1.2.3-rc.1"
    assert (
        get_tag_without_branch(conf, "somebranch-1.2.3-rc.1-abcd-hello-world")
        == "1.2.3-rc.1-abcd-hello-world"
    )
    assert (
        get_tag_without_branch(conf, "somebranch-v1.2.3-rc.1-abcd-hello-world")
        == "v1.2.3-rc.1-abcd-hello-world"
    )
    assert (
        get_tag_without_branch(conf, "somebranch-V1.2.3-rc.1-abcd-hello-world")
        == "V1.2.3-rc.1-abcd-hello-world"
    )


def test_add_branch_to_tag():
    conf = {"prepend_branch_to_tag": False, "repo": _mockclass("somebranch")}
    assert add_branch_to_tag(conf, "v1.2.3") == "v1.2.3"
    assert add_branch_to_tag(conf, "v1.2.3-rc.1") == "v1.2.3-rc.1"
    assert add_branch_to_tag(conf, "v1.2.3-rc.1-abc") == "v1.2.3-rc.1-abc"
    conf = {"prepend_branch_to_tag": True, "repo": _mockclass("somebranch")}
    assert add_branch_to_tag(conf, "v1.2.3") == "somebranch-v1.2.3"
    assert add_branch_to_tag(conf, "v1.2.3-rc.1") == "somebranch-v1.2.3-rc.1"
    assert add_branch_to_tag(conf, "v1.2.3-rc.1-abc") == "somebranch-v1.2.3-rc.1-abc"
    conf = {"prepend_branch_to_tag": True, "repo": _mockclass("branch")}
    assert add_branch_to_tag(conf, "v1.2.3") == "branch-v1.2.3"
    assert add_branch_to_tag(conf, "v1.2.3-rc.1") == "branch-v1.2.3-rc.1"
