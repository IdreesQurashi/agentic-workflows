# Northstars Lab: State Ledger

## Last Updated
2026-10-03 23:07 PKT

## Operational Status and Architecture Pivot
* Track 1 (SuSocial Automated Bots): RETIRED. Accounts Sandra and Nancy permanently action blocked on Direct Messages by Meta. VPS tools halted to prevent wasted server cycles. No renewal planned.
* Track 2 (Triple Touch ABM Pipeline): ACTIVE. Operating a manual three pronged touchpoint on 15 to 25 elite US clinics daily:
  * Official Domain Email: 3 to 5 hyper personalized observation notes from idrees@northstarsmb.com on verified MX addresses.
  * Clinic Website Consultation Forms: 10 to 15 direct inquiries to practice managers with zero domain risk.
  * Instagram Story Pings: 10 direct mobile notifications to clinic owners on active procedure stories.
* Automated Script Lockdown: execution/outbound/dispatch_clinic_emails.py permanently disabled. Background automated sending banned per directives/autonomous_outbound_pipeline.md Section 2 Line 10 (which mandates 900 to 1800 second pacing). All future dispatches remain strictly human.

## VPS and Proxy Infrastructure Reference
* Host: Contabo Cloud VPS 4 running Windows Server 2022
* Server IP: 13.140.38.183
* Credentials: Administrator / Northstars2026!
* Proxy Architecture: 4 Premium USA IPv4 Proxies routing through gateway IP 109.204.36.9 to 4 distinct USA exit IPs via unique port and user authentication. All verified Valid in SuSocial Proxy Manager.
* Proxy Gateway Technical Finding: Debunked SuSocial Support's claim that proxies require a Windows 11 gateway. Proxies route via blind TCP CONNECT tunnels. 117 page log audit proves proxies delivered hundreds of clean browser operations. Real API bottleneck was HTTP 429 rate limiting on emulated mobile endpoints, which is bypassed completely by running in Embedded Browser mode.

## SuSocial 13 Column Contact Tool Field Mapping
* Column 1: Company Name
* Column 2: First Name (Stores Instagram Username, mapped to UI NAME in SuSocial)
* Column 3: Phone
* Column 4: Address (Stores Company Name, mapped to UI GROUP NAME in SuSocial)
* Column 5: City
* Column 6: State (Stores Outreach Message, mapped to UI MESSAGE in SuSocial)
* Column 7: Website
* Column 8: Instagram Handle (Stores Instagram Username, used for deduplication)
* Column 9: Instagram Profile URL (Stores full Instagram profile URL)
* Column 10: Followers Count (Default placeholder 5000)
* Column 11: Anchor Procedure (Extracted high margin services)
* Column 12: Outreach Message (Full bespoke outreach text)
* Column 13: Tags (Campaign tags, e.g. Scrape_28, B2B_Cold)

## Antigravity Lead Engine Infrastructure
* Yelp Scraper: `execution/outbound/yelp_lead_scraper.py`
* Google Maps Scraper: `execution/outbound/gmaps_lead_scraper.py`
* Instagram Audit Engine: `execution/outbound/audit_instagram_leads.py`
* ICP AI Qualification: `execution/outbound/gemini_icp_qualifier.py` (powered by external Gemini Flash Lite pool)
* Master Orchestrator: `orchestration/b2b_lead_pipeline.py`
* Dedicated Python Environment: `/home/idrees/job_agent/.venv/bin/python3`
* Execution Rule: All directory harvesting, Instagram handle parsing, and SuSocial batch partitioning operate entirely inside Antigravity. Zero external Claude dependencies.
