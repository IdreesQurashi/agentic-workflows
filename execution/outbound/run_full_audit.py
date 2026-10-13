#!/usr/bin/env python3
"""Batch Runner for Instagram Lead Audits (Parts 2, 3, 4)."""

import os
import sys
import subprocess
import csv

BASE_DIR = "/home/idrees/northstars/leads/susocial_ready_fresh_400"
PYTHON_BIN = "/home/idrees/job_agent/.venv/bin/python3"
SCRIPT_PATH = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/audit_instagram_leads.py"

def run_audits():
    parts = [2, 3, 4]
    for p in parts:
        in_file = os.path.join(BASE_DIR, f"fresh_400_part_{p}.csv")
        aud_file = os.path.join(BASE_DIR, f"fresh_400_part_{p}_audited.csv")
        rej_file = os.path.join(BASE_DIR, f"fresh_400_part_{p}_rejected.csv")
        
        print("\n" + "=" * 60)
        print(f"=== LAUNCHING INSTAGRAM AUDIT FOR PART {p} (100 LEADS) ===")
        print("=" * 60, flush=True)
        
        cmd = [
            PYTHON_BIN,
            SCRIPT_PATH,
            "--input", in_file,
            "--audited-output", aud_file,
            "--rejected-output", rej_file
        ]
        
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"[ERROR] Audit failed on part {p} with exit code {res.returncode}", file=sys.stderr)
            sys.exit(res.returncode)

    # Master aggregation across all 4 parts
    print("\n" + "=" * 60)
    print("=== AGGREGATING ALL 4 AUDITED BATCHES INTO MASTER DATASET ===")
    print("=" * 60)
    
    all_audited = []
    all_rejected = []
    
    for p in [1, 2, 3, 4]:
        aud_file = os.path.join(BASE_DIR, f"fresh_400_part_{p}_audited.csv")
        rej_file = os.path.join(BASE_DIR, f"fresh_400_part_{p}_rejected.csv")
        
        if os.path.exists(aud_file):
            with open(aud_file, "r", encoding="utf-8-sig", errors="ignore") as f:
                r = list(csv.DictReader(f))
                all_audited.extend(r)
                print(f"  Part {p} Audited: {len(r)} leads")
                
        if os.path.exists(rej_file):
            with open(rej_file, "r", encoding="utf-8-sig", errors="ignore") as f:
                r = list(csv.DictReader(f))
                all_rejected.extend(r)
                print(f"  Part {p} Rejected: {len(r)} leads")

    master_audited_file = os.path.join(BASE_DIR, "fresh_400_master_audited.csv")
    master_rejected_file = os.path.join(BASE_DIR, "fresh_400_master_rejected.csv")
    
    if all_audited:
        fieldnames = list(all_audited[0].keys())
        with open(master_audited_file, "w", newline="\r\n", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_audited)
            
    if all_rejected:
        fieldnames = list(all_rejected[0].keys())
        with open(master_rejected_file, "w", newline="\r\n", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rejected)

    print("\n" + "=" * 60)
    print("=== FINAL 400-LEAD AUDIT COMPLETE ===")
    print(f"  Total Master Approved Leads: {len(all_audited)}")
    print(f"  Total Master Rejected Leads: {len(all_rejected)}")
    print(f"  Master Approved Path: {master_audited_file}")
    print(f"  Master Rejected Path: {master_rejected_file}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_audits()
