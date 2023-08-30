"""tests for the Version class"""
import hitchhiker.release.version.semver as semver
import hitchhiker.release.enums as enums

expect = [
    {
        "input": "0.0.01-rc5", # invalid input
        "error": True,
        "bump": enums.VersionBump.PATCH,
        "bump_prerelease": False,
        "major": 0,
        "minor": 0,
        "patch": 1,
        "prerelease": None,
        "buildmeta": None,
        "str": "0.0.1",
        "repr": "0.0.1",
    },
    {
        "input": "1.153.16.25-rc.29+date2023-08-22abcdef-abc",
        "error": True,
        "bump": enums.VersionBump.NONE,
        "bump_prerelease": False,
        "major": 0,
        "minor": 0,
        "patch": 0,
        "prerelease": None,
        "buildmeta": None,
        "str": "0.0.0",
        "repr": "0.0.0",
    },
    {
        "input": "0.0.0",
        "error": False,
        "bump": enums.VersionBump.MAJOR,
        "bump_prerelease": False,
        "major": 1,
        "minor": 0,
        "patch": 0,
        "prerelease": None,
        "buildmeta": None,
        "str": "1.0.0",
        "repr": "1.0.0",
    },
    {
        "input": "153.16.3-rc.7",
        "error": False,
        "bump": enums.VersionBump.MINOR,
        "bump_prerelease": False,
        "major": 153,
        "minor": 16,
        "patch": 3,
        "prerelease": "rc.8",
        "buildmeta": None,
        "str": "153.16.3-rc.8",
        "repr": "153.16.3-rc.8",
    },
    {
        "input": "153.16.3+20230821-a---build-5",
        "error": False,
        "bump": enums.VersionBump.PATCH,
        "bump_prerelease": False,
        "major": 153,
        "minor": 16,
        "patch": 4,
        "prerelease": None,
        "buildmeta": "20230821-a---build-5",
        "str": "153.16.4",
        "repr": "153.16.4+20230821-a---build-5",
    },
    {
        "input": "153.16.25-rc.29+date2023-08-22abcdef-abc",
        "error": False,
        "bump": enums.VersionBump.NONE,
        "bump_prerelease": False,
        "major": 153,
        "minor": 16,
        "patch": 25,
        "prerelease": "rc.29",
        "buildmeta": "date2023-08-22abcdef-abc",
        "str": "153.16.25-rc.29",
        "repr": "153.16.25-rc.29+date2023-08-22abcdef-abc",
    },
]


def test_semver():
    """test for semver"""
    for ex in expect:
        print(f"INPUT: \"\"\"{ex['input']}\"\"\"")
        version = semver.Version().parse("0.0.0").bump(ex["bump"], ex["prerelease"])
        try:
            version = semver.Version().parse(ex["input"]).bump(ex["bump"], ex["prerelease"])
        except Exception as e:
            if not ex["error"]:
                raise e
        assert version.major == ex["major"]
        assert version.minor == ex["minor"]
        assert version.patch == ex["patch"]
        assert version.prerelease == ex["prerelease"]
        assert version.buildmeta == ex["buildmeta"]
        assert str(version) == ex["str"]
        assert repr(version) == ex["repr"]


def test_semver_cmp():
    """test semver comparison functions"""
    assert semver.Version().parse("1.0.0") < semver.Version().parse("1.0.1") < semver.Version(
    ).parse("1.1.0") < semver.Version().parse("1.1.1") < semver.Version().parse("2.1.1")

    assert not (semver.Version().parse("2.1.0") <
                semver.Version().parse("1.0.1"))
    assert not (semver.Version().parse("1.1.0") <
                semver.Version().parse("1.0.1"))
    assert not (semver.Version().parse("1.7.2") <
                semver.Version().parse("1.7.1"))

    assert semver.Version().parse("1.2.3-alpha") < semver.Version().parse(
        "1.2.3-beta") < semver.Version().parse("1.2.3-delta") < semver.Version().parse("1.2.3-gamma")

    assert semver.Version().parse("1.0.0-alpha") < semver.Version().parse("1.0.0-alpha.1") < semver.Version().parse("1.0.0-alpha.beta") < semver.Version().parse(
        "1.0.0-beta") < semver.Version().parse("1.0.0-beta.2") < semver.Version().parse("1.0.0-beta.11") < semver.Version().parse("1.0.0-rc.1") < semver.Version().parse("1.0.0")

    assert not (semver.Version().parse("1.0.0-alpha") <
                semver.Version().parse("1.0.0-alpha"))

    assert semver.Version().parse("1.0.0-alpha") == semver.Version().parse("1.0.0-alpha")
    assert semver.Version().parse("1.0.0-beta") != semver.Version().parse("1.0.0-alpha")
    assert semver.Version().parse(
        "1.0.0-beta") == semver.Version().parse("1.0.0-beta+buildmeta")

    assert semver.Version().parse("1.5.0-rc.197") < semver.Version().parse("1.5.0-rc.198")

def test_semver_prerelease():
    assert semver.Version().parse("1.0.0-rc.0").bump(enums.VersionBump.PATCH, True) == semver.Version().parse("1.0.0-rc.1")
    assert semver.Version().parse("1.0.0-rc.1").bump(enums.VersionBump.MINOR, True) == semver.Version().parse("1.0.0-rc.2")
    assert semver.Version().parse("1.0.0-rc.2").bump(enums.VersionBump.MAJOR, True) == semver.Version().parse("2.0.0-rc.1")
    assert semver.Version().parse("1.0.0-rc.0").bump(enums.VersionBump.PATCH, False) == semver.Version().parse("1.0.1")
    assert semver.Version().parse("1.0.0-rc.1").bump(enums.VersionBump.MINOR, False) == semver.Version().parse("1.1.0")
    assert semver.Version().parse("1.0.0-rc.2").bump(enums.VersionBump.MAJOR, False) == semver.Version().parse("2.0.0")

    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.NONE, True) == semver.Version().parse("1.0.0-rc.1578+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.PATCH, True) == semver.Version().parse("1.0.0-rc.1579+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.MINOR, True) == semver.Version().parse("1.0.0-rc.1579+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.MAJOR, True) == semver.Version().parse("2.0.0-rc.1+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.NONE, False) == semver.Version().parse("1.0.0+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.PATCH, False) == semver.Version().parse("1.0.1+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.MINOR, False) == semver.Version().parse("1.1.0+abc")
    assert semver.Version().parse("1.0.0-rc.1578+abc").bump(enums.VersionBump.MAJOR, False) == semver.Version().parse("2.0.0+abc")

    assert semver.Version().parse("1.0.0").bump(enums.VersionBump.MINOR, True) == semver.Version().parse("1.0.0-rc.1")

    assert semver.Version().parse("1.0.0-rc29").bump(enums.VersionBump.PATCH, True) == semver.Version().parse("1.0.0-rc.1")
