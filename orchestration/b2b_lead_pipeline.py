#!/usr/bin/env python3
"""Master B2B Lead Orchestrator and Pipeline Manager.

Coordinates multi source harvesting (Yelp, Google Maps), master deduplication,
Gemini AI ICP qualification, and automatic SuSocial 4 batch partitioning.
"""

import os
import sys

workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import argparse
import asyncio
import csv
from typing import Dict, Any, List

SATURATED_CITIES = [
    "Dallas, TX",
    "Miami, FL",
    "Los Angeles, CA",
    "Austin, TX",
    "Scottsdale, AZ",
    "New York, NY"
]

ACTIVE_TARGET_CITIES = [
    {"city": "Oklahoma City, OK", "short": "Oklahoma_City", "state": "OK"},
    {"city": "Richmond, VA", "short": "Richmond", "state": "VA"},
    {"city": "Baltimore, MD", "short": "Baltimore", "state": "MD"},
    {"city": "Louisville, KY", "short": "Louisville", "state": "KY"},
    {"city": "Memphis, TN", "short": "Memphis", "state": "TN"},
    {"city": "Providence, RI", "short": "Providence", "state": "RI"},
    {"city": "New Orleans, LA", "short": "New_Orleans", "state": "LA"},
    {"city": "Hartford, CT", "short": "Hartford", "state": "CT"},
    {"city": "Birmingham, AL", "short": "Birmingham", "state": "AL"}
]

MASTER_DB_PATH = "/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv"

def get_master_record_count() -> int:
    if not os.path.exists(MASTER_DB_PATH):
        return 0
    try:
        with open(MASTER_DB_PATH, "r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
            return max(0, len(rows) - 1)
    except Exception:
        return 0

def print_city_catalog():
    print("\n========================================================")
    print("=== B2B LEAD ENGINE: TARGET METROPOLITAN HUBS ===")
    print("========================================================")
    print("\n[SATURATED HUBS - DO NOT RE-HARVEST]")
    for sc in SATURATED_CITIES:
        print(f"  * {sc} (Exhausted / In Master Registry)")

    print("\n[ACTIVE UNHARVESTED TARGET QUEUE]")
    for ac in ACTIVE_TARGET_CITIES:
        print(f"  * {ac['city']} (Ready for harvest)")
    print("========================================================\n")

async def run_pipeline(
    source: str,
    city: str,
    target: int,
    auto_partition: bool
):
    print("\n" + "=" * 60)
    print(f"=== LAUNCHING B2B LEAD PIPELINE ===")
    print(f"  City:       {city}")
    print(f"  Source:     {source.upper()}")
    print(f"  Target:     {target} Qualified Leads")
    print(f"  Partition:  {'ENABLED' if auto_partition else 'DISABLED'}")
    print("=" * 60)

    initial_count = get_master_record_count()
    print(f"Baseline Master Registry Lead Count: {initial_count} leads\n")

    total_harvested = 0

    # Execute Yelp harvesting
    if source in ["yelp", "both"]:
        from execution.outbound.yelp_lead_scraper import harvest_yelp_city
        print(f"[STAGE 1] Running Yelp Harvester for {city}...")
        try:
            yelp_harvested = await harvest_yelp_city(
                city=city,
                target_qualified=target
            )
            total_harvested += yelp_harvested
        except Exception as e:
            print(f"[ERROR] Yelp Harvester encountered failure: {e}", file=sys.stderr)

    # Execute Google Maps harvesting
    if source in ["gmaps", "both"] and total_harvested < target:
        remaining = target - total_harvested
        from execution.outbound.gmaps_lead_scraper import harvest_gmaps_city
        print(f"\n[STAGE 2] Running Google Maps Harvester for {city} (Seeking {remaining} remaining)...")
        try:
            gmaps_harvested = await harvest_gmaps_city(
                city=city,
                target_qualified=remaining
            )
            total_harvested += gmaps_harvested
        except Exception as e:
            print(f"[ERROR] Google Maps Harvester encountered failure: {e}", file=sys.stderr)

    final_count = get_master_record_count()
    new_leads = final_count - initial_count

    print("\n" + "=" * 60)
    print("=== PIPELINE HARVEST RUN SUMMARY ===")
    print(f"  City:                {city}")
    print(f"  Target Leads:        {target}")
    print(f"  Harvested & Passed:  {total_harvested}")
    print(f"  New Master Records:  +{new_leads}")
    print(f"  Total Master DB:     {final_count}")
    print("=" * 60)

    # Execute partitioning
    if auto_partition:
        print("\n[STAGE 3] Partitioning master lead registry into 4 SuSocial batches...")
        from execution.outbound.susocial_partitioner import (
            load_and_standardize_leads,
            write_partitioned_batches,
            OUTPUT_DIRS
        )
        leads = load_and_standardize_leads(MASTER_DB_PATH)
        write_partitioned_batches(leads, OUTPUT_DIRS, num_batches=4)
        print("SuSocial 4 batch partitioning complete.")

async def run_queue_pipeline(
    source: str,
    total_target: int,
    per_city_target: int,
    auto_partition: bool
):
    print("\n" + "=" * 60)
    print("=== LAUNCHING MULTI CITY B2B LEAD QUEUE HARVEST ===")
    print(f"  Total Cumulative Target: {total_target} Qualified Leads")
    print(f"  Per City Target:         {per_city_target} Leads")
    print(f"  Source Engine:           {source.upper()}")
    print(f"  SuSocial Partition:      {'ENABLED' if auto_partition else 'DISABLED'}")
    print("=" * 60)

    initial_master_count = get_master_record_count()
    print(f"Baseline Master Registry Lead Count: {initial_master_count} leads\n")

    for idx, city_info in enumerate(ACTIVE_TARGET_CITIES):
        city_name = city_info["city"]
        current_master = get_master_record_count()
        leads_added = current_master - initial_master_count
        needed = total_target - leads_added
        if needed <= 0:
            print(f"\n[GOAL REACHED] Cumulative target of {total_target} qualified leads achieved!")
            break

        city_target = min(per_city_target, needed)
        print(f"\n>>> [QUEUE {idx+1}/{len(ACTIVE_TARGET_CITIES)}] Processing {city_name} (Target: {city_target} leads | Overall Progress: {leads_added}/{total_target})...")

        try:
            harvested = 0
            if source in ["yelp", "both"]:
                from execution.outbound.yelp_lead_scraper import harvest_yelp_city
                harvested = await harvest_yelp_city(city=city_name, target_qualified=city_target)

            if source in ["gmaps", "both"] or (harvested == 0 and city_target > 0):
                print(f"[FALLBACK] Engaging Google Maps harvester for {city_name}...")
                from execution.outbound.gmaps_lead_scraper import harvest_gmaps_city
                rem_needed = city_target - (harvested or 0)
                if rem_needed > 0:
                    await harvest_gmaps_city(city=city_name, target_qualified=rem_needed)
        except Exception as e:
            print(f"[ERROR] Harvest for {city_name} encountered an issue: {e}", file=sys.stderr)

    final_master_count = get_master_record_count()
    net_added = final_master_count - initial_master_count

    print("\n" + "=" * 60)
    print("=== MULTI CITY QUEUE HARVEST COMPLETE ===")
    print(f"  Initial Master Count: {initial_master_count}")
    print(f"  Final Master Count:   {final_master_count}")
    print(f"  Net Qualified Added:  +{net_added}")
    print("=" * 60)

    if auto_partition:
        print("\nPartitioning master lead registry into 4 SuSocial batches...")
        from execution.outbound.susocial_partitioner import (
            load_and_standardize_leads,
            write_partitioned_batches,
            OUTPUT_DIRS
        )
        leads = load_and_standardize_leads(MASTER_DB_PATH)
        write_partitioned_batches(leads, OUTPUT_DIRS, num_batches=4)
        print("SuSocial 4 batch partitioning complete.")

def main():
    parser = argparse.ArgumentParser(description="Master B2B Lead Orchestrator")
    parser.add_argument("--source", choices=["yelp", "gmaps", "both"], default="yelp",
                        help="Data source to scrape (default: yelp)")
    parser.add_argument("--city", default="Charlotte, NC",
                        help="Target metropolitan hub (e.g. 'Charlotte, NC')")
    parser.add_argument("--target", type=int, default=25,
                        help="Target number of qualified leads to harvest (default: 25)")
    parser.add_argument("--per-city", type=int, default=35,
                        help="Target qualified leads per city in queue mode (default: 35)")
    parser.add_argument("--queue", action="store_true",
                        help="Run automated queue across all active unharvested cities")
    parser.add_argument("--partition", action="store_true",
                        help="Auto partition leads into 4 SuSocial batches upon completion")
    parser.add_argument("--list-cities", action="store_true",
                        help="List saturated vs active queue cities")
    args = parser.parse_args()

    if args.list_cities:
        print_city_catalog()
        return

    if args.queue:
        asyncio.run(run_queue_pipeline(
            source=args.source,
            total_target=args.target,
            per_city_target=args.per_city,
            auto_partition=args.partition
        ))
    else:
        asyncio.run(run_pipeline(
            source=args.source,
            city=args.city,
            target=args.target,
            auto_partition=args.partition
        ))

if __name__ == "__main__":
    main()
