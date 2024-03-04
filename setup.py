from setuptools import setup

_hitchhiker_version = "0.0.0"

# for backwards compatibility
setup(
    name="hitchhiker",
    version=_hitchhiker_version,
    packages="hitchhiker",
    package_data={
        "hitchhiker": ["py.typed"],
    },
    include_package_data=True,
)
