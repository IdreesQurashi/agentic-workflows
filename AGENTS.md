# Workspace Router

## Workstream State Protocol
* This workspace contains 5 workstreams: Northstars, MAK Shift, Job Hunter, Personal Brand, Core Engineering.
* On session start: identify the active workstream from user prompt keywords or explicit declaration. Read `state/<stream>.md` before proposing or executing tasks.
* On milestone completion or session end: update `state/<stream>.md` with completed items, new blockers, and next pickup point.
* Never load state files for inactive workstreams. Workstream specific operational rules live in their dedicated skills, loaded on demand only.
* Keyword routing: "northstars" or "leads" or "sdr" or "yelp" or "scrape" → state/northstars.md (Skill: b2b_lead_engine). "mak" or "shift" or "6121" or "kabani" → state/mak_shift.md. "job" or "holy 30" or "indeed" or "ashby" or "skill match" → state/job_hunter.md. "brand" or "portfolio" or "site" or "github.io" → state/personal_brand.md. "engineering" or "n8n" or "proxy" or "gemini pool" → state/core_engineering.md.
