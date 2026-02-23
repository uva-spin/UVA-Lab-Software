#!/usr/bin/env python3
"""
Entry point for standalone data acquisition.
Run from daq/ directory:
    python run.py
    python run.py --verbose --terminal-log
"""
import asyncio
import sys
from pathlib import Path

# Ensure daq root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from acquisition.standalone import run_standalone

if __name__ == "__main__":
    asyncio.run(run_standalone())
