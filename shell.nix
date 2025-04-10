with import <nixpkgs> {};
let
in stdenv.mkDerivation {
  name = "hitchhiker";
  buildInputs = [
    python311
    python311Packages.setuptools
    python311Packages.pip

    python311Packages.pdoc

    python311Packages.pytest
    python311Packages.coverage

    python311Packages.mypy

    python311Packages.types-requests
    python311Packages.types-deprecated
    python311Packages.types-psycopg2

    python311Packages.click

    python311Packages.gitpython
    python311Packages.tomlkit
    python311Packages.dotty-dict
    python311Packages.PyGithub

    python311Packages.google-cloud-storage

    python311Packages.pylint
    python311Packages.flake8
    python311Packages.coverage

    gnumake
  ];
}
