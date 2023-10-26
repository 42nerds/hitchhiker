"""Tests for ConfigManager class"""
from hitchhiker.config.config import ConfigManager


def test_configmanager_deepdir(tmp_path_factory):
    tmpf = (
        tmp_path_factory.mktemp("conf")
        / "subdir"
        / "another subdir"
        / "one more subdir"
        / "config.json"
    )

    cfg1 = ConfigManager(tmpf, {"testkey1": "x", "testkey2": ["x", "y"]})
    cfg1.set_key("somekey", ["this", "is", "a", "list"])

    assert cfg1.get_key("testkey1") == "x"
    assert cfg1.get_key("testkey2") == ["x", "y"]
    assert cfg1.get_key("somekey") == ["this", "is", "a", "list"]

    cfg2 = ConfigManager(
        tmpf,
        {
            "testkey3": "this is a long string",
        },
    )
    cfg2.set_key("testkey1", ["this", "is", "another", "list"])

    assert cfg2.get_key("testkey1") == ["this", "is", "another", "list"]
    assert cfg2.get_key("testkey2") == ["x", "y"]
    assert cfg2.get_key("somekey") == ["this", "is", "a", "list"]


def test_configmanager(tmp_path_factory):
    tmpf = tmp_path_factory.mktemp("conf") / "config.json"
    cfg1 = ConfigManager(tmpf, {"testkey1": "x", "testkey2": ["x", "y"]})
    cfg1.set_key("somekey", ["this", "is", "a", "list"])

    assert cfg1.get_key("testkey1") == "x"
    assert cfg1.get_key("testkey2") == ["x", "y"]
    assert cfg1.get_key("somekey") == ["this", "is", "a", "list"]

    cfg2 = ConfigManager(
        tmpf,
        {
            "testkey3": "this is a long string",
        },
    )
    cfg2.set_key("testkey1", ["this", "is", "another", "list"])

    assert cfg2.get_key("testkey1") == ["this", "is", "another", "list"]
    assert cfg2.get_key("testkey2") == ["x", "y"]
    assert cfg2.get_key("somekey") == ["this", "is", "a", "list"]

    cfg3 = ConfigManager(tmpf, {"testkey5": "z"})

    assert cfg3.get_key("testkey1") == ["this", "is", "another", "list"]
    assert cfg3.get_key("testkey2") == ["x", "y"]
    assert cfg3.get_key("testkey3") == "this is a long string"
    assert cfg3.get_key("somekey") == ["this", "is", "a", "list"]
    assert cfg3.get_key("testkey5") == "z"

    cfg4 = ConfigManager(tmpf, {"testkey1": "x", "testkey2": ["x", "y"]})

    assert cfg4.get_key("testkey1") == ["this", "is", "another", "list"]
    assert cfg4.get_key("testkey2") == ["x", "y"]
    assert cfg4.get_key("testkey3") == "this is a long string"
    assert cfg4.get_key("somekey") == ["this", "is", "a", "list"]
    assert cfg4.get_key("testkey5") == "z"

    open(tmpf, "w").close()

    cfg5 = ConfigManager(tmpf, {"testkey1": "x", "testkey2": ["x", "y"]})

    assert cfg5.get_key("testkey1") == "x"
    assert cfg5.get_key("testkey2") == ["x", "y"]
    try:
        cfg5.get_key("somekey")
        assert False
    except KeyError:
        pass

    try:
        cfg5.get_key("testkey3")
        assert False
    except KeyError:
        pass
