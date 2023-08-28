with import <nixpkgs> {};
let
in stdenv.mkDerivation {
  name = "python-click-experiments";
  buildInputs = [
    python311
    python311Packages.setuptools
    python311Packages.pip

    python311Packages.pytest
    python311Packages.click
    python311Packages.gitpython
    python311Packages.tomlkit
    python311Packages.dotty-dict
    python311Packages.PyGithub
  ];
}
