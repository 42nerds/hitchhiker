"""Tests for ConfigManager class"""
from hitchhiker.config.config import ConfigManager


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

    assert cfg2.get_key("testkey1") == "x"
    assert cfg2.get_key("testkey2") == ["x", "y"]
    assert cfg2.get_key("somekey") == ["this", "is", "a", "list"]

    cfg3 = ConfigManager(tmpf, {})

    assert cfg2.get_key("testkey1") == "x"
    assert cfg2.get_key("testkey2") == ["x", "y"]
    assert cfg2.get_key("testkey3") == "this is a long string"
    assert cfg2.get_key("somekey") == ["this", "is", "a", "list"]

    open(tmpf, "w").close()

    cfg4 = ConfigManager(tmpf, {"testkey1": "x", "testkey2": ["x", "y"]})

    assert cfg4.get_key("testkey1") == "x"
    assert cfg4.get_key("testkey2") == ["x", "y"]
    try:
        cfg4.get_key("somekey")
        assert False
    except KeyError:
        pass

    try:
        cfg4.get_key("testkey3")
        assert False
    except KeyError:
        pass
