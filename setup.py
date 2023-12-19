from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=["tests"]),
    package_data={
        "hitchhiker": ["py.typed"],
    },
    include_package_data=True,
)
