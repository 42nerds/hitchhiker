from setuptools import find_namespace_packages, setup

_hitchhiker_version = "0.7.0"

# this is for backwards compatibility
# NOTE: if you edit dependencies here edit them in pyproject.toml too!
setup(
    name="hitchhiker",
    version=_hitchhiker_version,
    description="",
    python_requires=">=3.7",
    install_requires=[
        "click>=8,<9",
        "tomlkit>=0.12.3,<1",
        "dotty-dict>=1.3.1,<2",
        "typing-extensions",
        "requests",
        "jinja2",
    ],
    extras_require={
        "release": ["gitpython>=3.1.40,<4", "PyGithub>=2.1.1,<3"],
        "odoo": ["click-odoo>=1.6,<2"],
        "test": [
            "pytest>=7,<8",
            "mypy",
            "types-requests",
            "pylint",
            "flake8",
        ],
        "docs": [
            "pdoc",
        ],
        "copier": [
            "copier>=8.0.0,<10",
        ],
    },
    entry_points={
        "console_scripts": [
            "hitchhiker = hitchhiker.cli.cli:cli",
        ]
    },
    packages=find_namespace_packages(where=".", include=["hitchhiker*"]),
    package_data={
        "hitchhiker": ["py.typed"],
    },
    include_package_data=True,
)
