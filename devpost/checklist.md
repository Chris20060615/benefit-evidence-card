---
doc: checklist
status: draft
authorship: agent-authored technical planning draft
execution_authorization: direct user delegation to plan and prepare the competition project autonomously
human_plan_review: pending
---

# Build Checklist

Build mode: fast execution under the user's direct delegation. This is an agent-selected execution setting responding to the request for autonomous progress, not a completed learner mode-selection interview. Implementation may proceed while plan status remains draft. Check boxes below require actual evidence; planned work is not completed work.

Verification record: the post-review 2026-10-25 build session recorded 34 passing automated tests, including the optional internal official-source snapshot. This is a development test count, not a retrieval accuracy score or participant review. Actual Edge browser checks also passed; see `verification.json`. Only corresponding implementation and automated-check subitems are marked below. Whole slices remain open while participant requirements remain incomplete.

## Slices

- [ ] **1. A local page finds one exact passage with provenance**
  Becomes usable: A running local page accepts a progress-viewing question and displays an exact source passage with original title, publisher, publication date, retrieval time, section and official link.
  Why now: Proves the whole source-to-browser path immediately and exposes source availability/metadata errors before adding broader rules.
  PRD ref: `prd.md > The Core Journey` (steps 1-4), `prd.md > Source Provenance`, `prd.md > Evidence Cards`
  Spec ref: `spec.md > Source Loader and Parser`, `spec.md > Local HTTP API`, `spec.md > Browser Interface`
  Build: Scaffold the standard-library local server and buildless frontend, fetch/verify the fixed guide, add ignored in-project `.cache/` storage and provenance, and connect the query form to one bounded evidence path. Keep runtime independent from reference labels.
  - [x] Implementation: `server.py` loads and validates the fixed source and serves the form/API; `evidence.py` parses source paragraphs and the frontend renders provenance.
  - [x] Verify (automated): Parser/paragraph and provenance checks, cached-source identity/integrity checks, absent/invalid cache and HTTP unavailable-source tests passed in the recorded suite.
  - [x] Verify (browser/run): Started port 8768 in a separate process using verified cache. Edge displayed the exact original quote, title, date, section and official link. Optional source highlighting is a browser convenience, not a required correctness claim.
  Learner check: Pending participant trial: open the page, locate progress-viewing evidence and compare the passage with the official source. Agent verification does not complete this check.
  Local checkpoint: `679a2a1` (AI-agent identity, not participant attribution).

- [ ] **2. Unsupported conclusions abstain and conditions stay visible**
  Becomes usable: The same form handles the small supported topic set while clearly refusing unsupported personal, nationwide, guaranteed-timing and out-of-domain conclusions; conditional passages retain their source limits.
  Why now: Completes the distinctive evidence-versus-relevance behavior before visual polish or shipping work.
  PRD ref: `prd.md > Insufficient Evidence`, `prd.md > Evidence Cards`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Evidence Schema and Retrieval`, `spec.md > Data Model`, `spec.md > Important Failure Modes`
  Build: Add source-derived section/cue checks, deterministic English/Chinese intent rules, conservative unsupported-claim checks, and exact quotation plus qualifier rendering. No runtime loading of case labels or hardcoded question-to-answer responses. The current application does not use the historical lexical ranker.
  - [x] Implementation: Return `supported`, `conditional` or `insufficient`; keep related passages labeled as insufficient when they do not establish the requested claim.
  - [x] Verify (automated): Supported/conditional topics, personal rate and amount, universal claims, timing/approval guarantees, proxy/document checklists, unknown questions, English/Chinese paraphrases and mixed requests passed the recorded suite. Source-capability checks also reject matching words in unsupported section context.
  - [x] Verify (browser): Edge displayed conditional limits and related-passage labels; example and typed queries returned identical JSON. Review regression questions abstained. Participant trials remain separate.
  Learner check: Pending participant trial: try a supported question and a claim the guide cannot establish; report any misleading or missing condition. Continue independent implementation meanwhile.
  Local checkpoints: `679a2a1` implements the bounded rules; `d90495b` clarifies single-question abstention reasons.

- [ ] **3. A reviewer can run, inspect and demonstrate the prototype**
  Becomes usable: A clean one-page English interface is runnable from exact instructions, handles failures, keeps sensitive/internal files inaccessible, and supports the short demonstration journey.
  Why now: Turns the functioning kernel into a reproducible artifact and makes the remaining human shipping tasks concrete.
  PRD ref: `prd.md > Look and Feel`, `prd.md > Source and Request Errors`, `prd.md > What We're Building`
  Spec ref: `spec.md > Where It Runs and How Someone Tries It`, `spec.md > Local HTTP API`, `spec.md > Browser Interface`, `spec.md > File Structure`
  Build: Refine readable layout, keyboard focus and loading/error handling; enforce route allowlisting and request limits; add exact English setup/test instructions; preserve draft/authorship status and actual development evidence. Keep `.cache/` excluded from public commits and HTTP serving and preserve `.gitignore` protections.
  - [x] Implementation: English technical README documents actual CLI flags, API statuses, the single-guide boundary, source/cache rights and unfinished participant/submission work.
  - [x] Verify (automated): Blank/long/malformed questions, request byte limits, wrong content type, missing source, internal-file/traversal routes and untrusted Host/Origin requests passed the recorded suite. Parser checks include inline text and hidden content handling.
  - [x] Verify (browser/run): Edge checked 390px mobile layout without horizontal overflow, Enter/Shift+Enter, empty input, safe HTML-like input and delayed-request controls/query echo. No browser errors. Source-unavailable behavior is covered by API tests; no real participant trial is claimed.
  Learner check: Pending final participant exploration: run the documented steps, try awkward inputs, identify needed revisions, and state whether the prototype is ready for shipping preparation.
  Local checkpoint: `679a2a1`; final technical records are saved in the following documentation commit.

## Hands-on Checkpoints

- [ ] Early usable behavior explored by a participant. Await actual trial; do not substitute an agent browser test.
- [ ] Final kick-the-tires exploration and feedback completed by a participant.

Independent authorized implementation continues while these human checks remain pending. If feedback arrives before the build finishes, use it to revise the smallest affected slice.

## Final Review

- [ ] Any reported participant revision is implemented, mechanically verified and retried by that participant.
- [ ] Final review complete: participant explicitly confirms readiness. No such confirmation has yet been recorded.

## Code Tour and App Map

- [x] Generate `devpost/app-map.html` from actual files and symbols; provide it as a reference route. Offline rendering is checked separately; this does not mean a guided tour happened.
- [ ] Offer a short learning activity grounded in one real query path, source verification or abstention check; record actual participation separately from an agent explanation.
- [ ] Optional edit and transfer reflection addressed without inventing a personal response.

Activity and evidence: reference map prepared; no interactive participant activity performed. No learner mastery or reflection is inferred from implementation.
Reference route: `web/app.js:submitQuestion` → `server.py:Handler.do_POST` and `evidence.py:search_document` → `web/app.js:renderResult`. No completed participant tour is claimed.
Edit outcome: not attempted.
Reflection: not yet offered or answered.
Activity mode: to be recorded from actual interaction.

## Shipping Preparation Remaining

- [x] Review intended public files: independent audit of 42 tracked candidates found no private profile, names/accounts, credentials, absolute personal paths, full cache, recordings or unrelated files. The initial history uses only transparent AI-agent commits. No public publishing has occurred.
- [ ] Prepare a runnable public repository and verify its unauthenticated link once publishing is authorized.
- [ ] Participant supplies the official project name, description, form responses and exit-survey reflection; agent correction is limited to spelling/grammar under the toolkit.
- [ ] Participant supplies narration; record a working demo shorter than three minutes and verify its public video link.
- [ ] Confirm actual team/account state and remaining eligibility/form requirements without treating registration as team completion.
- [ ] Verify all required assets before an explicitly authorized formal submission; do not claim submission from preparation alone.

## Revisions

- 2026-10-25: Updated implementation details from a proposed outside-repository cache and lexical ranking to the actual ignored `.cache/` directory and source-capability/intent rules. Split mechanical implementation/test evidence from browser checks, participant checkpoints and commits. Recorded 26 automated tests without treating them as participant learning, broad accuracy, approved plans or finished slices.
- Local checkpoints use a transparent AI-agent commit identity; they do not credit participants with unverified work. Public repository/video links and formal submission remain pending.


- 2026-10-25 post-review: fixed unsupported action/location/eligibility claims, invalid cache metadata structures, and request/result mismatch. Reverified 34 automated tests and the actual browser journey. The initial 26-test record is superseded for the current revision.

- 2026-10-25 final mechanical record: 34 tests passed after clarifying single-question rejection reasons. Actual source-link click opened the official article and its body contained the exact quote; scroll position changed. Highlight appearance is not claimed. A silent technical video was recorded; participant narration and public video link remain pending.
