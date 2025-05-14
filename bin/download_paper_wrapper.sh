#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_DIR="$SCRIPT_DIR/python"
PYTHON="python3.12"

"$PYTHON" $PYTHON_DIR/cli.py --download
