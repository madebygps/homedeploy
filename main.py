#!/usr/bin/env python3
"""
HomeDeploy - NAS-to-Local deployment tool with natural language configs
"""
import sys
from homedeploy.cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())