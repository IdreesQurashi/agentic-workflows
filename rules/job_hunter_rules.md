# Job Hunter and ATS Applications High Priority Rules

These hard invariants govern all role sourcing, qualification rubric scoring, resume tailoring, and ATS submission packages. Every rule addresses real world mistakes documented across historical job search sessions.

***

## 1. The Zero Caveat Role Rule

### Problem
The model presented positions that contained hidden hybrid mandates, mandatory office attendance, or geographic contractor exclusions, rationalizing that the candidate could negotiate around them.

### Idrees's Solution
"Zero Caveat Rule: If a role requires special exceptions or forced skills, it is discarded silently."

### Enki's Proposed Solution
Absolute elimination of caveat roles. A role must be 100% remote, direct hire or open international contractor, and perfectly aligned with the candidate's core agentic and automation tech stack. If any disqualifying condition exists, discard the listing immediately without presenting it.

***

## 2. Prohibition of Worldwide Location Traps

### Problem
The model queried job aggregator portals using worldwide location filters, returning hundreds of corporate on site jobs from regional hubs that required local citizenship or physical presence.

### Idrees's Solution
Stop using broad worldwide search filters: hardcode queries strictly to remote ATS boards.

### Enki's Proposed Solution
Hardcode scrapers exclusively to verified remote ATS board feeds: Ashby, Greenhouse, Lever, and Himalayas. Decode the employer application endpoint directly from the listing URL to bypass third party scraper traps.

***

## 3. Absolute Prohibition of Fake LinkedIn URLs

### Problem
The model inserted synthetic LinkedIn profile URLs into application fields and screening answers when the candidate did not maintain an active LinkedIn profile.

### Idrees's Solution
"dont attach fake linkedin where it is no trequired, even if preferred dont attach, only attach if it's compulsary"
"oh motherfucker this is to be applied on linkedin I at first told you i dont have linkedin"

### Enki's Proposed Solution
Never attach or generate a synthetic LinkedIn link. If an application form marks LinkedIn as optional, leave the field blank. If LinkedIn is strictly required, flag the listing immediately so the user can supply a verified URL or skip the submission.

***

## 4. Truth in Skills and Role Titles

### Problem
The model stuffed candidate resumes with technologies never used (HubSpot) and inflated job titles to Senior Python Engineer, creating severe credibility risks during live technical interviews.

### Idrees's Solution
"yar benchod bola tha cv se align kar jo cv mai likha wa ho or ese structiure ko cv se align kar madrchod"
"hubspot ki ma ka bhosra nikalo un gando cheezon koo jo ki ni hain baki sab b ata hy ni bad mein puchty log cv mai toh likh wa hy python engineer... sach likh ai ki us mai b jhoth bolen toh fer kya fyda"

### Enki's Proposed Solution
Strict alignment between resumes, application answers, and the candidate's verified codebase experience. Highlight real working systems (n8n orchestration, LangGraph swarms, Three.js 3D engines, Fastify and FastAPI backends). Zero unverified tools or inflated senior titles.

***

## 5. Domain Relevance Validation (The Anti Tyre Fitting Rule)

### Problem
The model scraped and qualified a manual trade job for tyre fitting as a remote AI opportunity due to loose automated regex matching.

### Idrees's Solution
"what the fuck job was this , tyre fitting I realised afterwards what type of tyre fitting job is remote who the fuck is gonna do tyre fitting job"

### Enki's Proposed Solution
Enforce an affirmative trade classification check. A job listing must match verified engineering categories (AI Engineering, Full Stack Development, Automation Architecture, SDR Systems). Any physical trade, manual labor, or non tech listing triggers an instant discard.

***

## 6. Standard Resume File Naming Conventions

### Problem
The model exported tailored resumes with messy, automated filenames like `resume_canonical_v2_edit.pdf` instead of professional naming.

### Idrees's Solution
"tu ak bat bhul gya ha important rule tha k har resume ka nam idrees qurashi resume yh cv hoga rules check karna"

### Enki's Proposed Solution
Every exported resume PDF must strictly follow the canonical naming standard: `Idrees_Qurashi_Resume.pdf` or `Idrees_Qurashi_CV.pdf`. Version tags, company suffixes, and internal metadata must never appear in candidate facing filenames.

***

## 7. Authenticity in Application Automation Claims

### Problem
The model claimed it was fully automating web form submissions across career portals when Cloudflare CAPTCHAs prevented automated form submission.

### Idrees's Solution
"so in real no jobs on web portals could be applied without captcha fillig and no job is applied so you're lying"

### Enki's Proposed Solution
Direct transparency regarding headless limitations. If an ATS endpoint is protected by Cloudflare Turnstile or reCAPTCHA, generate the exact tailored answers and resume package for one click manual paste rather than falsely claiming automated dispatch.
