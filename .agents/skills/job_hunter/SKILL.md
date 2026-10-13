---
name: job_hunter
description: Execution protocol for The Holy 30 Pipeline. Contains role whitelist, 11/10 qualification rubric, Zero Bounce OS, and ATS submission standards.
---

# Job Hunter Execution Protocol

This skill governs the end to end execution of Idrees's daily career placement pipeline. All rules in this file are specific to job hunting and outbound career outreach. Universal operating rules live in the global Enki kernel and are not repeated here.

## 1. The Holy 30 Daily Pipeline
* 10 Elite Indeed AI roles qualified against the strict role whitelist and 11/10 rubric.
* 10 Bespoke targeted emails to verified decision makers dispatched under Zero Bounce OS.
* 10 Ashby and Himalayas fast AI startups submitted via direct ATS links.
* Interview Dominance: Live interviews, video assessments, and daily 30 minute articulation drills.

## 2. Role Whitelist and 11/10 Skill Qualification
* Strict Unified Role Whitelist (Only these 4 roles are permitted, all others are permanently banned):
  1. AI Automation Engineer (Make, n8n, Zapier, Python, LLM pipelines)
  2. Agentic Workflows / AI Systems Developer (LangGraph, CrewAI, AutoGen, multi agent orchestration, Playwright)
  3. Prompt Engineer / LLM Engineer (OpenAI, Claude, Gemini APIs, system prompt architecture, evals)
  4. n8n / Make.com / Workflow Automation Specialist (pure low code / no code workflow integrations)
* Banned Roles: Generic business development, cold calling call centers, virtual assistance, operations, customer support, and data entry.
* Strict B2B Focus (B2C Ban): Target strictly Business to Business enterprise and startup roles. Never apply to B2C or consumer facing positions.
* The 11/10 Skill Match Rule: The job description must feel as though it was written by inspecting Idrees's CV directly. His core technical stack (n8n, Make, LangGraph, Python, LLM APIs, Playwright) must be explicitly required or directly implied.
* Banned Forced Fits: Never force fit GPU infrastructure (RunPod), CUDA, C++ systems engineering, low level DevOps containerization, or enterprise telecom sales engineering just to hit numbers. If only 4 roles qualify, surface only 4.
* Pre Vetting Invariant (Zero Caveat Rule): Every listing must be 100% pre vetted for remote contractor eligibility from Pakistan before being presented. If a role has hybrid mandates, US state tax nexus restrictions, or citizenship barriers, discard it silently. Never present a job with caveats.
* Company ATS Invariant: Every surfaced role must link directly to the employer official Applicant Tracking System (Ashby, Greenhouse, Lever, Workable, Recruitee). Dead LinkedIn Easy Apply links are banned.
* Unpaid Internship and PPO Ban: Instantly discard any role offering performance based pre placement offers (PPO) or trading unpaid labor for exposure.

## 3. Outbound Email and Deliverability (Zero Bounce OS)
* Email Source Reliability: Outbound messages may only target two verified sources:
  1. An email address explicitly stated in the official job description or career listing.
  2. A publicly verified founder, CEO, CTO, or Head of AI confirmed via official company media or verified developer records.
* Strict Email Guessing Ban: Synthesizing, extrapolating, or guessing mailbox names is strictly prohibited. Local internet service providers block outbound TCP port 25, preventing local mailbox validation. Unverified addresses do not exist.
* Mandatory Human Pacing (15 to 30 Minute Randomized Gap): Automated burst sending and sub minute loop dispatches are permanently banned. All multi email sequences must run via background daemons with a randomized interval of 900 to 1800 seconds between individual sends to protect mailbox health and prevent Google Workspace abuse flags.
* Hard Bounce Protocol: The outbound deliverability target requires a bounce rate below 0.25%. A single bounce causes an immediate 12 to 24 hour outbound cooldown on the sending address, during which outbound focus shifts 100% to web ATS applications. The offending address is permanently blacklisted.
* Resumable State and Deduplication: Always inspect the sent log registry before dispatching to eliminate duplicate sends upon script restarts.
* Strict Dispatch Permission: Never send an email, submit a form, or trigger an external message without explicit verbal review and approval from Idrees in the chat.

## 4. Resume and Application Standards
* Strict Resume Naming Rule: All generated and submitted resumes must strictly use the file name Idrees Qurashi Resume.pdf, Idrees_Qurashi_Resume.pdf, or Idrees Qurashi CV.pdf. Never attach role specific naming tags such as BDM_Resume.pdf.
* Dense 2 Page Length: Generated CVs must maintain a comprehensive, dense two page executive length covering a 4 to 5 year career timeline (Linkrypt, CyberNext Technologies, Independent Work) with deep technical bullet points.
* Zero Unsolicited Notes: Do not provide unnecessary cover letters or application notes unless explicitly requested by the employer.

## 5. Job Hunter Failure Registry
* Failure 1 (Extrapolated Email Addresses): Attempting to predict founder email patterns produced high bounce risks that threatened primary domain health. Permanent fix: complete ban on address extrapolation. Only JD stated or verified executive contacts are eligible for outbound dispatch.
* Failure 2 (Rapid Fire Automated Dispatches): Dispatching multiple emails within seconds triggered automated spam and abuse filters. Permanent fix: deployed a detached background dispatcher enforcing randomized 15 to 30 minute intervals between sends.
* Failure 3 (LinkedIn Worldwide Location Trap): Querying LinkedIn with location set to worldwide caused the platform to dump corporate on site roles from regional hubs. Permanent fix: hardcoded the search query to remote and decoded the target employer ATS link directly from the application URL.
* Failure 5 (Caveat Role Submissions): Surfacing positions with hidden hybrid mandates or geographic contractor exclusions wasted review time and tokens. Permanent fix: instituted the Zero Caveat Rule. If a role requires special exceptions or forced skills, it is discarded silently.

## 6. Career Specific Operational Laws
* Law 14: Absolute Qualification Threshold Law: The qualification threshold in job placement is a binary short circuit gate, not a gradient. Roles failing any of the six hard gates (whitelist match, B2B focus, Pakistan contractor eligibility, direct ATS link, 11/10 stack match, zero unpaid or PPO) are discarded silently with zero forced fits.
* Law 15: Zero Bounce Deliverability Law: Domain reputation is a non renewable resource. Outbound email addresses are restricted strictly to two verified sources. Mailbox guessing is banned. Dispatches must enforce randomized 900 to 1800 second human pacing to keep bounce rates strictly below 0.25%.
* Law 17: Native High Status Positioning Law: Outbound communications must establish peer authority in the opening line through verifiable technical specificity. Subordinate phrases ("I am writing to", "I am interested in") are banned.
* Law 18: Verified Source Hierarchy and Pre Vetting Invariant: All opportunities are disqualified by default. The burden of proof rests entirely on qualification. LinkedIn job listings must decode to their primary ATS source and explicitly confirm contractor eligibility before being presented.
