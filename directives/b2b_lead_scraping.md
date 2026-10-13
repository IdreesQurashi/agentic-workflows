# B2B Lead Scraping and Qualification Master Directive

## Purpose and Scope
This directive establishes the operating procedure for harvesting, verifying, qualifying, and partitioning B2B leads for high ticket aesthetics clinics, med spas, boutique cosmetic practices, and cosmetic dentistry studios across target metropolitan markets in the United States.

## Target Geography and Market Segmentation
Targeting is structured across two distinct tiers to prevent wasted compute and duplicated outreach.

### Saturated Markets (Master Database Complete)
The following hubs have been exhaustively scraped and deduplicated. No new scraping passes may run on these cities without explicit authorization:
* Dallas, Texas
* Miami, Florida
* Los Angeles, California
* Austin, Texas
* Scottsdale, Arizona
* New York, New York

### Active Unharvested Target Queue
Scraping operations must prioritize the following virgin metropolitan areas:
* Charlotte, North Carolina
* Nashville, Tennessee
* Denver, Colorado
* Atlanta, Georgia
* Portland, Oregon
* San Diego, California
* Phoenix, Arizona
* Seattle, Washington

## Niche Whitelist and Blacklist Protocols

### Approved Niches
* Boutique Medical Spas
* Private Aesthetic Clinics
* Independent Certified Cosmetic Injectors
* High End Cosmetic Dentistry and Veneer Studios
* Specialized Body Contouring and Laser Centers

### Strict Chain Blacklist
The following national corporate chains and franchises are banned. If any substring matches the business title or domain, the record must be rejected immediately:
* LaserAway
* Ideal Image
* Satori Laser
* Skin Laundry
* Ever/Body
* Peachy
* Therapie Clinic
* OrangeTwist
* SEV Laser
* VIO Med Spa

### Model Exclusions
* Closed referral only practices catering exclusively to private celebrity clientele
* Low ticket commoditized businesses offering only basic facials, nail care, or standard therapeutic massages
* Sole practitioner mobile practitioners without an established commercial footprint

## Scraping and Anti Bot Stealth Architecture

### Headless Engine Standard
All web scraping must execute through asynchronous Playwright inside the dedicated virtual environment located at `/home/idrees/job_agent/.venv/bin/python3`. Direct interaction with personal desktop browser windows is prohibited.

### Pacing and Jitter Invariants
* Non linear delay jitter: Sleep between 15 and 30 seconds between individual business detail pages.
* Human behavioral emulation: Upon loading a page, scroll down 350 pixels, pause for 1.5 to 3.0 seconds, then scroll back to top.
* Context recycling: Terminate and recreate browser contexts every 15 to 20 profiles, rotating User Agent headers from modern desktop browser pools.
* Pagination velocity: Search page navigation must pause 5 to 10 seconds between 10 result offset increments.

## Social Handle and Instagram Extraction

### Verification Standard
Every prospect must possess a verified, direct Instagram profile. Outreach without a verified Instagram handle is banned.

### Extraction Hierarchy
1. DOM Anchor Search: Inspect profile page DOM anchors matching selector `a[href*='instagram.com']`.
2. Website Fallback: If no handle exists on the directory profile, navigate to the official website and parse DOM anchors.
3. Handle Extraction Regex: Extract username via pattern `instagram\.com/([^/?#]+)`.
4. Blacklist Filter: Exclude non profile system handles (`p`, `reel`, `reels`, `explore`, `accounts`, `legal`, `help`, `about`, `sharer`, `developer`, `stories`).
5. Rejection Logging: Records lacking a verified Instagram handle are logged to `/home/idrees/northstars/leads/bullshit/unverified_leads.csv`.

## Master Deduplication Invariant
Before any profile is evaluated by AI or added to an active queue, its website domain and company name must be checked against:
* Primary Master Database: `/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv`
* Historical Batch Files: All CSV files located in `/home/idrees/northstars/leads/raw_databases/`
* Normalization Rule: Lowercase, strip protocol schemes (`https://`, `http://`, `www.`), and remove trailing slashes.
* Enforcement: If a domain or company name matches any prior entry, skip immediately with zero Gemini API calls.

## Gemini ICP Qualification Protocol

### Worker Architecture
Evaluations are offloaded to external Gemini API calls utilizing the 8 key rotating pool. The target model is strictly `gemini-flash-lite-latest` to avoid free tier quota exhaustion.

### The Three Point Qualification Test
Each business website text (up to 12,000 characters) is evaluated against three non negotiable criteria:
1. Physical Locations: Must operate 2 or fewer physical clinic locations. Practices with 3 or more locations fail. Unspecified location count defaults to 1 and passes.
2. Market Accessibility: Must actively offer and market services to the public. Referral only or closed celebrity practices fail.
3. High Margin Offer: Must provide high margin treatments such as neuromodulators, dermal fillers, RF microneedling, Morpheus8, laser resurfacing, body sculpting, or porcelain veneers. Low ticket commoditized spas fail.

### Decision Schema
Responses must return strictly parseable JSON:
```json
{"status": "PASS", "reason": "Independent boutique clinic with single location offering Morpheus8 and injectables."}
```
Any response marked `FAIL` is logged and discarded.

## SuSocial Export and Partitioning Standard

### 13 Column Contact Tool Mapping
SuSocial on Windows Server 2022 uses an exact 13 column CSV structure. To bypass interface bugs and ensure proper message dispatch, the data must be mapped as follows:
* Column 1: Company Name
* Column 2: First Name (Stores the Instagram Username, mapped to UI NAME in SuSocial)
* Column 3: Phone
* Column 4: Address (Stores the Company Name, mapped to UI GROUP NAME in SuSocial)
* Column 5: City
* Column 6: State (Stores the Outreach Message, mapped to UI MESSAGE in SuSocial)
* Column 7: Website
* Column 8: Instagram Handle (Stores the Instagram Username, used for deduplication)
* Column 9: Instagram Profile URL (Stores the full profile URL)
* Column 10: Followers Count (Default placeholder 5000)
* Column 11: Anchor Procedure (Extracted high margin services)
* Column 12: Outreach Message (Full bespoke outreach text)
* Column 13: Tags (Campaign tags, e.g. Scrape_28, B2B_Cold)

### Encoding and Formatting Requirements
* Encoding: `utf-8-sig` (UTF 8 with Byte Order Mark for Windows Excel compatibility).
* Line Terminator: CRLF (`\r\n`).
* Partitioning: Qualified leads must be divided into 4 equal, sterile batch files (`leads_part_1.csv` through `leads_part_4.csv`) in `/home/idrees/northstars/leads/new folder/` and `/home/idrees/northstars/leads/susocial_ready/`.
* Operational Quota: Maximum 15 direct messages per day per account (60 messages per day total across all 4 operational proxies).
