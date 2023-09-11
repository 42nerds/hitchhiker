"""tests for the ConventionalCommitParser class"""
import hitchhiker.release.commitparser.conventional as conventional
import hitchhiker.release.enums as enums

expect = [
    {
        "input": "",
        "is_conventional": False,
        "type": None,
        "scope": None,
        "breaking": None,
        "get_raw_subject": "",
        "get_raw_body": "",
        "get_description": "",
        "get_body": "\n",
        "get_footers": [],
        "get_version_bump": enums.VersionBump.NONE,
    },
    {
        "input": "fix: this and that",
        "is_conventional": True,
        "type": "fix",
        "scope": None,
        "breaking": False,
        "get_raw_subject": "fix: this and that",
        "get_raw_body": "",
        "get_description": "this and that",
        "get_body": "\n",
        "get_footers": [],
        "get_version_bump": enums.VersionBump.PATCH,
    },
    {
        "input": "fix(somewhere): this and that\n",
        "is_conventional": True,
        "type": "fix",
        "scope": "somewhere",
        "breaking": False,
        "get_raw_subject": "fix(somewhere): this and that",
        "get_raw_body": "",
        "get_description": "this and that",
        "get_body": "\n",
        "get_footers": [],
        "get_version_bump": enums.VersionBump.PATCH,
    },
    {
        "input": "feat(fix): this and that\n",
        "is_conventional": True,
        "type": "feat",
        "scope": "fix",
        "breaking": False,
        "get_raw_subject": "feat(fix): this and that",
        "get_raw_body": "",
        "get_description": "this and that",
        "get_body": "\n",
        "get_footers": [],
        "get_version_bump": enums.VersionBump.MINOR,
    },
    {
        "input": "fix(somewhere): this and that\nthis is a commit body\n\nthis is another paragraph in the commit body",
        "is_conventional": True,
        "type": "fix",
        "scope": "somewhere",
        "breaking": False,
        "get_raw_subject": "fix(somewhere): this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body",
        "get_description": "this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [],
        "get_version_bump": enums.VersionBump.PATCH,
    },
    {
        "input": "feat(something)!: this and that\nthis is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "is_conventional": True,
        "type": "feat",
        "scope": "something",
        "breaking": True,
        "get_raw_subject": "feat(something)!: this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "get_description": "this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [
            ("fixes", "530", True),
            (
                "some-footer",
                "this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
                False,
            ),
        ],
        "get_version_bump": enums.VersionBump.MAJOR,
    },
    {
        "input": "feat(something)!: this and that\nthis is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog\nBREAKING-CHANGE: this is a multiline\nbreaking change",
        "is_conventional": True,
        "type": "feat",
        "scope": "something",
        "breaking": True,
        "get_raw_subject": "feat(something)!: this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog\nBREAKING-CHANGE: this is a multiline\nbreaking change",
        "get_description": "this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [
            ("fixes", "530", True),
            (
                "some-footer",
                "this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
                False,
            ),
            ("BREAKING-CHANGE", "this is a multiline\nbreaking change", False),
        ],
        "get_version_bump": enums.VersionBump.MAJOR,
    },
    {
        "input": "feat(something): this and that\nthis is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog\nBREAKING CHANGE: this is a multiline\nbreaking change",
        "is_conventional": True,
        "type": "feat",
        "scope": "something",
        "breaking": True,
        "get_raw_subject": "feat(something): this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome-footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog\nBREAKING CHANGE: this is a multiline\nbreaking change",
        "get_description": "this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [
            ("fixes", "530", True),
            (
                "some-footer",
                "this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
                False,
            ),
            ("BREAKING CHANGE", "this is a multiline\nbreaking change", False),
        ],
        "get_version_bump": enums.VersionBump.MAJOR,
    },
    {
        "input": "feat(something): this and that\nthis is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "is_conventional": True,
        "type": "feat",
        "scope": "something",
        "breaking": False,
        "get_raw_subject": "feat(something): this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "get_description": "this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [("fixes", "530", True)],
        "get_version_bump": enums.VersionBump.MINOR,
    },
    {
        "input": "not a conventional commit: this and that\nthis is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "is_conventional": False,
        "type": None,
        "scope": None,
        "breaking": None,
        "get_raw_subject": "not a conventional commit: this and that",
        "get_raw_body": "this is a commit body\n\nthis is another paragraph in the commit body\nfixes #530\nsome footer: this a very long footer \n it even has multiple lines\n the quick brown fox jumps over the lazy dog",
        "get_description": "not a conventional commit: this and that",
        "get_body": "this is a commit body\n\nthis is another paragraph in the commit body\n",
        "get_footers": [("fixes", "530", True)],
        "get_version_bump": enums.VersionBump.NONE,
    },
]


def test_conventional_commit_parser():
    """test for ConventionalCommitParser"""
    for ex in expect:
        print(f"INPUT: \"\"\"{ex['input']}\"\"\"")
        commit = conventional.ConventionalCommitParser(ex["input"])
        assert commit.is_conventional == ex["is_conventional"]
        assert commit.type == ex["type"]
        assert commit.scope == ex["scope"]
        assert commit.breaking == ex["breaking"]
        assert commit.get_raw_subject() == ex["get_raw_subject"]
        assert commit.get_raw_body() == ex["get_raw_body"]
        assert commit.get_description() == ex["get_description"]
        assert commit.get_body() == ex["get_body"]
        assert commit.get_footers() == ex["get_footers"]
        assert commit.get_version_bump() == ex["get_version_bump"]
