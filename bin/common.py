#!/usr/bin/env python3
"""Run one shared hook unless a repo in this session already runs its own copy.

  common.py <marker> <command...>
stdin is passed through; exit code and output are the hook's own.
Missing interpreter or missing file = silent skip, never a broken session.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repos  # noqa: E402

marker, cmd = sys.argv[1], sys.argv[2:]
if repos.has_own(marker) or not shutil.which(cmd[0]) or not all(
        os.path.exists(a) for a in cmd[1:2]):
    sys.exit(0)
data = sys.stdin.buffer.read()
r = subprocess.run(cmd, input=data)
sys.exit(r.returncode)
