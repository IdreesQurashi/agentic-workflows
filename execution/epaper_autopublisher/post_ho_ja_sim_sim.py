#!/usr/bin/env python3
"""
Direct trigger script for Antigravity E-Paper Auto Publisher.
Triggered immediately when Idrees says: "post ho ja sim sim"
"""
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from publisher import run_pipeline

if __name__ == "__main__":
    print("=== POST HO JA SIM SIM: Triggering Automated E-Paper Publishing ===")
    custom_date = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(dummy=False, dry_run=False, custom_date=custom_date)
