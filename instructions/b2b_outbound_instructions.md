# B2B Outbound and Lead Engine Operational Instructions

These standard operating procedures define the step by step process for high ticket B2B lead scraping, Instagram handle extraction, Gemini ICP qualification, and cold email copywriting. Every procedure addresses real world bottlenecks documented in historical outbound sessions.

***

## 1. Directory Scraping Pagination and Anti Bot Backoff

### Problem
Directory scrapers crashed on anti bot verification or network latency, logging an error and advancing pagination indices by 10, resulting in silent data loss.

### Idrees's Solution
None provided by Idrees (Identified during code audit of `yelp_lead_scraper.py`).

### Enki's Proposed Solution
Structure scraper pagination loops with exponential backoff:
1. Wrap page navigation in a 3 tier retry block with jitter delays between 4.0 and 8.0 seconds.
2. If a page returns an HTTP 403 or Cloudflare challenge, log a warning and pause the process for 30 seconds before retry.
3. Advance the pagination offset only after the current page successfully yields business cards or confirms an empty result set.

***

## 2. Multi Layer Instagram Handle Extraction

### Problem
Scrapers checked only a single CSS selector for Instagram links, returning empty strings and marking active med spas as having zero social presence when links were nested in footers or schema tags.

### Idrees's Solution
None provided by Idrees (Identified during code audit of `yelp_lead_scraper.py`).

### Enki's Proposed Solution
Implement a 3 tier extraction waterfall for social handles:
* Tier 1: Direct DOM query targeting `a[href*="instagram.com/"]`.
* Tier 2: Regex scan of raw HTML text for `instagram.com/[a-zA-Z0-9_.]+`.
* Tier 3: Parse embedded `application/ld+json` schema tags for `sameAs` arrays.
Only record an empty handle if all three extraction tiers return negative.

***

## 3. Worker Pool Model Routing Protocol

### Problem
Batch qualification scripts targeted standard flash aliases (`gemini-flash-latest`), exhausting the 20 request daily free quota in minutes.

### Idrees's Solution
"target `gemini-flash-lite-latest` for worker pools"
"Universal Failure Registry: Failure 4 (Gemini Flash Quota Exhaustion)."

### Enki's Proposed Solution
All external qualification scripts must target `gemini-flash-lite-latest` through the 6 key rotating pool (`gemini_worker.py`). Rotate keys on every request to ensure zero workspace token burn and zero quota exhaustion.

***

## 4. A/B Testing Variant Separation vs Sequential Follow Ups

### Problem
When the user provided three subject lines and hooks to test, the model threw them into Follow Up slots in a sequential drip campaign.

### Idrees's Solution
"follow ups are not that much long, also I think I had given you different versions of first copy only but you have thrown them into the follow up section... I want you to give them three copies as we test different copies"

### Enki's Proposed Solution
When generating cold outreach sequences, clearly separate horizontal split test variants from vertical follow up steps:
* Step 1: Initial Hook (Provide Variant A, Variant B, Variant C for split testing).
* Step 2: Follow Up 1 (A short, 2 line bump sent 72 hours later).
* Step 3: Follow Up 2 (A value add case study or technical proof sent 96 hours later).
* Step 4: Breakup (A clean, low friction withdrawal sent 5 days later).

***

## 5. Pragmatic Instagram Manual Follow Up Execution

### Problem
Su Social proxy errors prevented automatic extraction of users for secondary messages, stalling outbound campaigns while attempting to fix broken software features.

### Idrees's Solution
"aby bhodiky bety madrchod secondry ki ma ka bhosra... CSV uthao, Column B mein apna Follow up 1 text daal do... Send Messages mein daal"

### Enki's Proposed Solution
When automated secondary queues stall:
1. Export the successful primary send list from the platform to CSV.
2. Filter leads where the initial send date is older than 72 hours.
3. Append Follow Up 1 copy into the message column.
4. Import the enriched CSV into the primary send queue with safe volume limits (15 to 20 messages per account per day).

***

## 6. Client Facing Proposal Asset Formatting

### Problem
Saving technical proposals as raw unrendered markdown files in the user's Documents directory created confusion when non technical clients opened them.

### Idrees's Solution
"now save this in documents folder of pc, give a name that doesnt looks creepy"
"what the fuck this look like"

### Enki's Proposed Solution
When generating client facing proposals, offer clean formatted outputs. Deliver a clean, styled HTML report alongside the Markdown source so it can be viewed directly in any web browser or printed to PDF with executive grade styling.
