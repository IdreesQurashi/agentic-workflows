---
name: b2b_lead_engine
description: Complete operational skill for high ticket B2B lead scraping, Instagram extraction, and Gemini AI ICP qualification for med spas, aesthetics, and cosmetic dental clinics.
---

# B2B Lead Engine and ICP Qualification Framework

## Core Objective
Scrape, verify, and qualify high ticket B2B prospects including Med Spas, Boutique Aesthetics, Independent Injectors, and High End Cosmetic Dentistry practices across target metropolitan hubs. Extract verified Instagram handles and pass them through strict AI qualification filters before export to SuSocial.

## Target Audience and Niche Criteria
* Target Niches: Boutique Medspas, Private Aesthetics Clinics, Independent Cosmetic Injectors, High End Cosmetic Dentistry and Veneer Studios.
* Geographic Hubs:
  * Saturated Cities (Master database coverage complete): New York, Miami, Los Angeles, Dallas, Austin, Scottsdale.
  * Active Target Cities (Unharvested priority queue): Charlotte NC, Nashville TN, Denver CO, Atlanta GA, Portland OR, San Diego CA, Phoenix AZ, Seattle WA.
* Exclusions: Multi unit mega chains (LaserAway, Ideal Image, Skin Laundry, Satori, Ever/Body, Peachy, etc.), closed referral only celebrity practices, and low ticket commoditized businesses (basic facials, standard massages).

## The Five Stage Operational Pipeline

### Stage 1: Directory Harvesting (Yelp and Google Maps)
* Engine: Headless Chromium driven by asynchronous Playwright (`async_playwright`).
* Stealth Protocol:
  * Non linear randomized delay jitter (15s to 30s between business profiles).
  * Human behavioral simulation (scroll down, pause 1.5s to 3.0s, scroll top).
  * Context recycling every 15 to 20 profiles with fresh user agent headers.
  * Search offset pagination (10 businesses per page up to offset 200).
* Chain Exclusion: Direct substring checks on business titles to bypass national franchises immediately.

### Stage 2: Direct Social Media Extraction
* Strategy: DOM anchor parsing directly on Yelp profile pages and target websites.
* Selector Pattern: `a[href*='instagram.com']`.
* Handle Extraction Regex: `instagram\.com/([^/?#]+)`.
* Blacklist: Discard non profile paths (`/p/`, `/reel/`, `explore`, `accounts`, `legal`, `help`, `about`, `sharer`).
* Routing: Unverified businesses lacking an Instagram handle are excluded from outreach and logged to `/home/idrees/northstars/leads/bullshit/unverified_leads.csv`.

### Stage 3: Master Deduplication Invariant
* Prior Database Protection: Never scrape or qualify a business that already exists in historical databases.
* Verification Rule: Check both website domain (normalized lower case) and company name against:
  * Master file: `/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv`
  * Historical shards: All `*.csv` files in `/home/idrees/northstars/leads/raw_databases/`
* Result: If a website or company name exists in the seen registry, the profile is skipped with zero AI token consumption.

### Stage 4: AI ICP Qualification (Gemini Pool)
* Architecture: External worker offloading targeting Gemini API with rotating keys.
* Strict Passing Requirements:
  1. Locations: The practice must have 2 or fewer physical locations. If they operate 3 or more locations, they FAIL. If unspecified, assume 1 and PASS.
  2. Business Model: They must actively market services to the public. If their website states they are purely referral only or an exclusive celebrity word of mouth closed practice, they FAIL.
  3. Core Offer: They must offer high margin procedures (lasers, body sculpting, injectables, Morpheus8, cosmetic surgery, veneers). If they only offer low ticket commodities, they FAIL.
* Output Schema: Strict JSON containing status (`PASS` or `FAIL`) and a concise reason.

### Stage 5: SuSocial Export and Account Segmentation
* Output Format: 13 column Contact tool schema for SuSocial.
* Schema Fields: `Company Name`, `First Name`, `Phone`, `Address`, `City`, `State`, `Website`, `Instagram Handle`, `Instagram Profile URL`, `Followers Count`, `Anchor Procedure`, `Outreach Message`, `Tags`.
* Account Partitioning: Split qualified leads into 4 distinct batches (`leads_part_1.csv` through `leads_part_4.csv`) loaded into 4 dedicated, sterile Instagram account contact tools.
* Daily Cap: Maximum 15 direct messages per day per account (60 messages per day total across the 4 accounts).

## Production Code Locations
* Yelp Harvester: `/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/yelp_lead_scraper.py`
* Google Maps Harvester: `/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/gmaps_lead_scraper.py`
* AI ICP Qualifier: `/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/gemini_icp_qualifier.py`
* SuSocial Partitioner: `/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/susocial_partitioner.py`
* Master Pipeline Orchestrator: `/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/orchestration/b2b_lead_pipeline.py`

## Autonomous Antigravity Execution Protocol
Whenever Idrees invokes `b2b_lead_engine` or prompts to scrape leads in Antigravity chat:
1. Step 1 (State Inspection): View `state/northstars.md` using `view_file` to review current lead counts and ensure the target city is not already saturated.
2. Step 2 (Directive Review): Inspect `directives/b2b_lead_scraping.md` to verify scraping parameters, chain filters, and anti bot pacing.
3. Step 3 (Orchestration Launch): Run `orchestration/b2b_lead_pipeline.py` via `run_command` targeting the requested city and lead count with `--partition` enabled.
4. Step 4 (State Update): Count new leads added to `Master_Qualified_Leads.csv` and update `state/northstars.md` with the new census numbers.
5. Step 5 (Deliverable Delivery): Present the verified summary, total qualified count, and paths to the generated SuSocial files directly to Idrees.

## CLI Execution Examples
Run complete city pipeline for Charlotte, NC:
```bash
/home/idrees/job_agent/.venv/bin/python3 "Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/orchestration/b2b_lead_pipeline.py" --city "Charlotte, NC" --target 25 --partition
```

Run Yelp scraper standalone for Nashville, TN:
```bash
/home/idrees/job_agent/.venv/bin/python3 "Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/yelp_lead_scraper.py" --city "Nashville, TN" --target 20
```

Partition qualified database into 4 SuSocial CSV batches:
```bash
/home/idrees/job_agent/.venv/bin/python3 "Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/execution/outbound/susocial_partitioner.py"
```

