import sys
from hitchhiker.cli.cli import cli

if __name__ == "__main__":
    sys.argv[0] = "hitchhiker"
    sys.exit(cli())
