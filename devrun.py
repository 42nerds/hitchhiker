import sys
from hitchhiker.cli import main
if __name__ == '__main__':
    sys.argv[0] = "hitchhiker"
    sys.exit(main())
