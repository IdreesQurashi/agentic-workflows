# Job Hunter and ATS Applications Operational Instructions

These standard operating procedures define the step by step process for role discovery, rubric scoring, resume tailoring, and ATS submission packaging under The Holy 30 pipeline. Every instruction addresses real world failure modes documented in historical job hunting sessions.

***

## 1. 11/10 Qualification Rubric Evaluation

### Problem
The model presented low quality roles, agency listings, and non remote positions to the user, wasting review time on jobs that failed basic candidate preferences.

### Idrees's Solution
"Zero Caveat Rule: If a role requires special exceptions or forced skills, it is discarded silently."

### Enki's Proposed Solution
Before surfacing any position, evaluate it against the 5 point 11/10 filter:
1. Remote Mandate: 100% remote with international contractor eligibility. Zero hybrid requirements.
2. Architecture Match: Requires LangGraph, n8n, autonomous agents, Python, or WebGL systems.
3. Decision Maker Access: Verifiable founder, CTO, or Head of Engineering contact available.
4. Competitive Compensation: Base pay of $2,000+ per month or market equivalent.
5. No Agency Reselling: Must be the direct hiring company, not a talent brokerage.
If any point scores 0, discard the listing immediately without presenting it.

***

## 2. Direct ATS URL and Token Decoding

### Problem
Aggregator links frequently pointed to dead redirects, expired job board listings, or spam reposts that failed on navigation.

### Idrees's Solution
"hardcoded the search query to remote and decoded the target employer ATS link directly from the application URL"

### Enki's Proposed Solution
Always resolve direct employer ATS endpoints:
* Ashby: `jobs.ashbyhq.com/{company}/{job_id}`
* Greenhouse: `boards.greenhouse.io/{company}/jobs/{job_id}`
* Lever: `jobs.lever.co/{company}/{job_id}`
Bypass middleman boards like Indeed or LinkedIn aggregators by extracting the canonical hiring board URL directly from page headers.

***

## 3. Resume Tailoring Alignment with Real Systems

### Problem
The model generated fictional project stories and hallucinated experience in tools the user never touched, creating severe vulnerability during technical deep dives.

### Idrees's Solution
"hubspot ki ma ka bhosra nikalo un gando cheezon koo jo ki ni hain baki sab b ata hy ni bad mein puchty log cv mai toh likh wa hy python engineer... sach likh ai ki us mai b jhoth bolen toh fer kya fyda"

### Enki's Proposed Solution
Tailor resumes strictly using proven codebase assets:
* Lead Generation: Reference the 6 key rotating Gemini scraper and Yelp automated extraction pipelines.
* AI Workflows: Reference 91 node n8n multi channel customer support workflows and LiteLLM proxy routers.
* Frontend 3D: Reference Three.js WebGL dark metallic shaders and FormSubmit AJAX handlers.
Every claim on the resume must point to a real script or verified repository in the user's workspace.

***

## 4. Screening Question Direct Response Copywriting

### Problem
Answers to ATS screening questions ("Why do you want to work here?", "Describe a difficult bug you solved") were written in stiff corporate prose packed with AI cliches.

### Idrees's Solution
"dont ever use these --- regenerate it"
"make it human written... 230 word human written response jo mission aur developer centric mindset ke sath 100% match karta hai"

### Enki's Proposed Solution
Draft all screening answers using direct response copywriting:
* Open immediately with the core technical contribution: "I build autonomous agentic architectures that eliminate manual workflow bottlenecks."
* Cite specific engineering metrics: "Processed 10,000+ leads across rotating proxy pools with zero dropped records."
* Eliminate corporate buzzwords. Never use phrases like "passionate about synergy" or "thrilled to apply".
* Strictly ban hyphens and dashes across all written answers.

***

## 5. Candidate Resume PDF Generation and Naming Standard

### Problem
Exported resume PDFs had messy titles containing internal prompt tags or version numbers that degraded professional presentation.

### Idrees's Solution
"tu ak bat bhul gya ha important rule tha k har resume ka nam idrees qurashi resume yh cv hoga"

### Enki's Proposed Solution
When generating resume PDFs:
1. Target `/home/idrees/Documents/Resumes/`.
2. Save files strictly as `Idrees_Qurashi_Resume.pdf` or `Idrees_Qurashi_CV.pdf`.
3. Verify that the generated PDF renders without visual clipping, font overlaps, or broken margins before presenting the link.
