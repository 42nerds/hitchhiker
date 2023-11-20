#!/usr/bin/env sh
set -e
make coverage
make lint
make type-checking
