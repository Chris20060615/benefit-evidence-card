---
doc: prd
status: draft
authorship: agent-authored technical planning draft
execution_authorization: direct user delegation to plan and prepare the competition project autonomously
human_plan_review: pending
---

# Evidence-finding prototype product requirements

This defines the agent-selected implementation experiment under delegated execution. It is not an entrant-approved identity or entrant-authored submission description. Source: `scope.md > The Unique Kernel` and `scope.md > Execution and Review`.

## The Core Journey

1. Open the local page and see the official guide's original title, publisher, publication date, retrieval time and source link.
2. Read the single-document boundary and enter an English or Chinese question. Example buttons may fill the field but use the same search path as typed questions.
3. Submit the question. If the document supports a recognized narrow information request, inspect an evidence card with original Chinese text, a labeled English explanation, the section locator and conditions.
4. Open the official source and compare the passage. The application makes no claim to reproduce the source website's current interface.
5. Ask for a conclusion the source does not establish. See an insufficient-evidence result; related passages, if exposed, must be labeled as related material rather than an answer.

Success is the visible distinction in steps 3 and 5, not a broad promise of medical-policy advice. Source: `scope.md > What "Working" Looks Like`.

## Screens and Layout

One page has a compact source panel, a question form, a result region and a small explanation of the document boundary. Put original wording and qualifications next to the result, not behind an optional disclaimer. Keep the source link reachable before and after searching. No account, upload, dashboard or chat-history screen is needed.

## Look and Feel

Agent-selected starting direction: a calm document-reading interface, restrained dark text on a light background, one accent color, generous line spacing, and readable Chinese and Latin system fonts. Use explicit status text and semantic labels rather than color alone. These are reversible implementation choices; no learner design preference is inferred.

## Features and Behavior

### Source Provenance

Show the guide's metadata from verified source acquisition: original title and publisher, publication date, official URL, retrieval time and local snapshot identifier. Distinguish the publication date from retrieval time. A cached source must be visibly identified as cached and must retain its acquisition timestamp.

Acceptance: the displayed title/date/link correspond to the acquired official page; cached and freshly fetched states are distinguishable. Source: `scope.md > The Core Loop`.

### Question Input

Accept ordinary English and Chinese text, trim whitespace, enforce a documented maximum length, and submit using the button or Enter. Blank input receives an inline request for a question. Example prompts are conveniences rather than a separate hardcoded answer route.

Acceptance: typed and example-filled copies of the same question produce the same response; blank/oversized input does not trigger a successful search.

### Evidence Cards

A source-backed result includes a narrow topic label, the exact original passage, a clearly identified English explanation, its section locator and provenance. Preserve regional and eligibility conditions with any conditional undertaking passage. Do not change "application submitted" or "view progress" into "application approved."

Acceptance: the quotation can be found in the acquired source; every shown condition derives from the same source; no result invents an outcome or amount. Source: `scope.md > The Unique Kernel`.

### Insufficient Evidence

Unknown questions, unsupported personal determinations, universal promises, approval-time guarantees and reimbursement amounts receive an insufficient-evidence status. A lexical match alone cannot elevate them into a supported answer. Explain that this guide does not establish the requested conclusion; do not assert that the conclusion is universally false.

Acceptance: personal reimbursement-rate, nationwide unconditional-undertaking, guaranteed same-day approval, proxy-material and out-of-domain questions abstain. Paraphrases and questions mixing supported and unsupported requests must also be checked. Source: `scope.md > Explicitly Cut`.

### Source and Request Errors

While searching, expose a loading state and prevent accidental duplicate submission. On malformed input, network/source errors or unexpected server failures, show an actionable message. If no verified source is available, do not fabricate evidence or quietly substitute another page.

Acceptance: unavailable source, invalid JSON and oversized input follow their documented paths; an old evidence card is not left looking like the answer to a failed new search.

## States and Boundaries

- Initial: provenance and query form are visible; the page does not imply a search has run.
- Evidence found: original text and conditions are inseparable from the result.
- Insufficient evidence: the requested conclusion is not established by this guide.
- Source unavailable: the evidence path is unavailable; a cached snapshot, if used, is labeled with its actual date.
- No personal query history or medical information is persisted by the application.
- The single source is a 2025 guide. Its presence does not certify current personal eligibility or application screens.

## Product Decisions

The human delegated planning and preparation. The agent chose the one-document experiment, bounded deterministic behavior, English interface, local execution and initially conservative visual treatment. No participant-specific motivation, design preference, role allocation, title or completed review is inferred.

## What We're Building

The single journey above, a working local server, tested provenance and abstention behavior, an English run guide, and truthful technical planning/build records. Public video and repository preparation are subsequent shipping work.

## Deferred From the POC

Multiple documents, policy updates, arbitrary uploaded content, accounts, cloud inference and deployment: none is needed to demonstrate the kernel. Source: `scope.md > The POC Boundary` and `scope.md > Later`.

## Open Questions

Before formal submission, participants still need to review the running prototype and provide their own project identity, submission wording and reflection. Their actual contributions and team/account state must be recorded accurately. These remaining human tasks do not block the locally authorized implementation.
