---
doc: scope
status: draft
authorship: agent-authored technical planning draft
execution_authorization: direct user delegation to plan and prepare the competition project autonomously
human_plan_review: pending
---

# Evidence-finding prototype scope

This is a technical working description, not an entrant-selected project name or submission copy. The user explicitly delegated competition planning and preparation. The agent selected the bounded experiment below under that delegation; it does not establish participant authorship, individual contribution, or approval of these documents.

## The Unique Kernel

Show the difference between a passage that mentions a topic and evidence that supports the particular question. Every displayed result keeps the original passage, source, date and applicable conditions together. When this one guide does not establish the requested conclusion, the interface says so.

## Who It's For

Proposed demonstration user: someone reading an official cross-province medical-filing guide who wants to locate a described step without turning it into a personal eligibility or payment decision. This audience is an agent-selected test scenario, not a reported participant need or a validated user population.

## The Core Loop

Open the local page, inspect the guide's provenance, ask a narrow document question in English or Chinese, and inspect either a source-backed evidence card or an insufficient-evidence message. Follow the official link to check the original. Ask a question the guide cannot answer and observe that related words alone do not produce a positive conclusion.

## Inspiration & Identity

The only initial source is the NHSA guide published 2025-03-16: https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html . Its original Chinese title and publisher remain visible. An English interface and plainly labeled English explanations make the demonstration understandable without presenting translations as official policy wording. Visual choices are implementation decisions, not recorded learner preferences.

## Why This Matters to the Learner

No personal policy problem, motivation, learning outcome or division of labor has been established. The user's concrete instruction is to devise the competition plan and advance preparation autonomously. Participation, reflection and completed contributions will be recorded only when they actually occur.

## What "Working" Looks Like

A reviewer starts the documented local server and completes one journey: locate the guide's filing-progress passage, see its original wording and provenance, then ask for a guaranteed same-day approval or a personal reimbursement percentage and receive an insufficient-evidence result. Conditional claims retain regional and eligibility limits. Meaningful automated checks support the demonstration, while participant hands-on review remains separately pending.

## The POC Boundary

One official guide; one local browser page; Python standard-library server; buildless HTML/CSS/JavaScript; deterministic retrieval; a small source-derived evidence schema; conservative answerability rules; English interface; original Chinese quotations; source/cache failure handling; documented run instructions. No paid API or account is required for the prototype.

## Later

Additional policy documents, professionally reviewed translations, broader query understanding and optional deployment can be considered after the core demonstration works. None is required for this build.

## Explicitly Cut

- Personal eligibility decisions, reimbursement calculations and nationwide policy guarantees: the selected guide does not provide sufficient inputs or authority.
- PDF upload, user accounts, medical-record input and a multi-region platform: each adds work outside this single-document experiment.
- Generative answer composition and paid model calls: they add dependencies without being needed to prove traceable retrieval and abstention.
- AI-written entrant titles, narration, submission responses and survey reflections: those remain participant-authored work.

## Execution and Review

Implementation proceeds under the user's delegation while this file remains `draft`. Delegation is not recorded as a completed learner interview or document review. Public publishing, final entrant copy, participant trial and formal submission remain distinct remaining tasks.
