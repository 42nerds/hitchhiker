"""tests for the Version class"""
import hitchhiker_module_control.version.semver as semver
import hitchhiker_module_control.enums as enums

expect = [
    {
        "input": "0.0.0",
        "bump": enums.VersionBump.MAJOR,
        "major": 1,
        "minor": 0,
        "patch": 0,
        "prerelease": None,
        "buildmeta": None,
        "str": "1.0.0",
    },
    {
        "input": "153.16.3-rc.7",
        "bump": enums.VersionBump.MINOR,
        "major": 153,
        "minor": 17,
        "patch": 0,
        "prerelease": "rc.7",
        "buildmeta": None,
        "str": "153.17.0-rc.7",
    },
    {
        "input": "153.16.3+20230821-a---build-5",
        "bump": enums.VersionBump.PATCH,
        "major": 153,
        "minor": 16,
        "patch": 4,
        "prerelease": None,
        "buildmeta": "20230821-a---build-5",
        "str": "153.16.4+20230821-a---build-5",
    },
    {
        "input": "153.16.25-rc29+date2023-08-22abcdef-abc",
        "bump": enums.VersionBump.NONE,
        "major": 153,
        "minor": 16,
        "patch": 25,
        "prerelease": "rc29",
        "buildmeta": "date2023-08-22abcdef-abc",
        "str": "153.16.25-rc29+date2023-08-22abcdef-abc",
    },
]


def test_version():
    """test for Version"""
    for ex in expect:
        print(f"INPUT: \"\"\"{ex['input']}\"\"\"")
        version = semver.Version().parse(ex["input"]).bump(ex["bump"])
        assert version.major == ex["major"]
        assert version.minor == ex["minor"]
        assert version.patch == ex["patch"]
        assert version.prerelease == ex["prerelease"]
        assert version.buildmeta == ex["buildmeta"]
        assert str(version) == ex["str"]


def test_version_cmp():
    """test Version comparison functions"""
    assert semver.Version().parse("1.0.0") < semver.Version().parse("1.0.1") < semver.Version(
    ).parse("1.1.0") < semver.Version().parse("1.1.1") < semver.Version().parse("2.1.1")

    assert not (semver.Version().parse("1.1.0") <
                semver.Version().parse("1.0.1"))

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

def test_version_prerelease():
    assert semver.Version().parse("1.0.0-rc.0").bump_prerelease() == semver.Version().parse("1.0.0-rc.1")
    assert semver.Version().parse("1.0.0-rc.1578").bump_prerelease() == semver.Version().parse("1.0.0-rc.1579")

    assert semver.Version().parse("1.0.0").bump_prerelease() == semver.Version().parse("1.0.0-rc.0")

    assert semver.Version().parse("1.0.0-rc29").bump_prerelease() == semver.Version().parse("1.0.0-rc.0")
