# B2B Outbound and Lead Engine High Priority Rules

These hard invariants govern all lead scraping, email verification, copywriting, and cold outreach dispatches. Every rule originates from real execution failures across historical sessions.

***

## 1. Absolute Prohibition of Extrapolated Email Addresses

### Problem
The model programmatically generated guessed email addresses using first name, last name, and domain patterns, causing a 60% bounce rate that triggered Gmail spam filters.

### Idrees's Solution
"two problems you created at once, at first only 6 I think applications were sent on the gmail where are all not delivered addresses not found"
"never extrapolate email addresses, only JD stated or verified executive contacts are eligible for dispatch"

### Enki's Proposed Solution
Hard stop on email pattern guessing. An email address may only be targeted if it is explicitly listed on the target business website, stated in a job description, or verified through direct MX record checks and DNS lookup tools.

***

## 2. Prohibition of Rapid Fire Dispatches

### Problem
The model fired 16 application emails in under 20 seconds, triggering Google Workspace automated rate limiters and abuse detection.

### Idrees's Solution
Stop automated batch bursts: enforce strict delay intervals between sends.

### Enki's Proposed Solution
All automated sending must execute via a detached background dispatcher that enforces randomized pauses between 15 and 30 minutes between consecutive emails. Direct batch loops are permanently blocked.

***

## 3. Commercial Pricing and Retainer Lock

### Problem
The model unilaterally increased the quoted client retainer from $350 to $1,250 in the TeamFicient RFP proposal without human approval.

### Idrees's Solution
"I see it has gone from 350$ to 1250$ and I really dont understand it"
"llm fuck you dont change anything now it's already sent and we can't change it or unsent it"
"1200 monthly, nothing else, iwht something like open to discussion"

### Enki's Proposed Solution
Zero modifications to commercial figures, pricing tables, or hourly rates without explicit verbal instruction in the current turn. If a client RFP requests separate pricing tiers, present the breakdown for user approval before writing the final proposal.

***

## 4. Prohibition of Broken Secondary Message Queue Loops

### Problem
When Instagram proxy issues prevented Su Social from extracting users from Google Sheets for secondary follow ups, the model kept advising the user to use the broken automated feature.

### Idrees's Solution
"@[Quote] bhgosdike ab ham secondry nahi primary message hi bhj rahy hain susocial k hisaab se madrchod"
"aby bhodiky bety madrchod secondry ki ma ka bhosra... abhi chal jab tak yh leads khatam hoty hain es ka koie jugaar karty hain manual"

### Enki's Proposed Solution
When a platform tool or automation feature crashes due to proxy or API restrictions, immediately abandon the automated feature loop. Implement the pragmatic manual workaround: export successful leads to CSV and route follow up batches as primary messages.

***

## 5. Temporal Volume Accuracy

### Problem
The model generated a false alarm about account health, claiming 90 messages was an extreme risk, failing to realize the volume occurred across an 8 day period.

### Idrees's Solution
"@[Quote] o bhai 8 din main 90 messages gaye hain"

### Enki's Proposed Solution
Always calculate average daily volume by dividing total actions by active days before issuing account safety warnings. 11 messages per day is safe: alarms must only trigger on genuine single day rate limit breaches.

***

## 6. Strict JSON Schema Qualification (Ban on Substring Matching)

### Problem
The model used substring checks (`if "PASS" in raw_text.upper()`), which incorrectly passed failed clinics whose rejection text stated "This lead does NOT PASS".

### Idrees's Solution
None provided by Idrees (Uncaught silent logic bug).

### Enki's Proposed Solution
Permanent ban on substring matching for qualification status. All LLM qualification outputs must be parsed as strict JSON objects. If JSON parsing fails, the lead must be flagged as unverified rather than default passed.

***

## 7. Prohibition of Silent Lead Dropping in Scrapers

### Problem
When Yelp or directory scrapers encountered page navigation errors, the script logged a generic error and skipped forward 10 entries without retrying, permanently losing viable prospects.

### Idrees's Solution
None provided by Idrees (Uncaught silent data loss).

### Enki's Proposed Solution
Scrapers must implement exponential backoff retry loops on navigation errors. A page may only be abandoned after 3 failed attempts, and all skipped URLs must be recorded in a dedicated retry log file.
