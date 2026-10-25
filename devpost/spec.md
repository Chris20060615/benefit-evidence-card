---
doc: spec
status: draft
authorship: agent-authored technical planning draft
execution_authorization: direct user delegation to plan and prepare the competition project autonomously
human_plan_review: pending
---

# Evidence-finding prototype technical specification

## How This Works, In Plain Language

A small Python program serves a webpage on the user's own computer. It fetches one official guide, verifies the page identity, and keeps a local `.cache/` directory inside the project, excluded from Git and HTTP serving. The user asks a question. Code checks a small set of explicit procedural rules against the loaded source. If the rule or source cannot support the conclusion, the webpage says evidence is insufficient. No model invents an answer.

This is a deliberately limited prototype. The chosen Python/browser architecture is an agent implementation decision under user-delegated execution, not an established learner preference.

## The Core Journey Through the System

Browser form → local `POST /api/search` → input validation → verified source/section data → deterministic intent, source-cue and answerability checks → JSON evidence result → browser rendering using text nodes → original-source link. `GET /api/source` exposes provenance/status, never the internal cache path. Implements `prd.md > The Core Journey`.

## Stack

- Python 3.11 or newer, standard library only. Use `http.server` for the loopback development server, `urllib.request` for the fixed source fetch, `html.parser` for extraction, and `unittest` for behavior checks. Documentation: https://docs.python.org/3/library/ . No package installer or API key is needed.
- Buildless HTML, CSS and JavaScript in a modern browser. Use the Fetch API for local JSON requests and `textContent`/DOM construction for source text. Documentation: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API and https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent .
- Bind to `127.0.0.1` by default. The standard-library HTTP server is a local demonstration mechanism, not a production hosting plan.

## Where It Runs and How Someone Tries It

Actual command from the project directory: `python -X utf8 server.py --port 8768`. Open `http://127.0.0.1:8768/`. `--host` defaults to `127.0.0.1` and accepts only `127.0.0.1` or `localhost`. Stop with `Ctrl+C`.

First use needs access to the fixed NHSA source. Subsequent runs reuse `.cache/nhsa-16010.html` and `.cache/nhsa-16010.json` only after verifying the saved digest, acquisition timestamp and article identity. `.cache/` is inside the repository directory but excluded by `.gitignore` and the HTTP route allowlist. `--cache-dir PATH` overrides its location. `--offline` requires an existing valid cache and makes no network request; `--refresh-source` skips cache reuse and fetches again at startup. Use these modes separately. Do not package the whole article in source control. The server stays accessible if loading fails, but source/search endpoints return HTTP 503. No paid account or external model key is required.

For demonstration, locate the guide's progress-viewing passage and then try a personal reimbursement percentage or guaranteed immediate approval. Required shipping assets remain a short public demo video and public source repository; a live deployment is optional and does not replace them.

## Look and Feel

Implement `prd.md > Look and Feel` using one small stylesheet, responsive single-column layout, readable text widths, visible keyboard focus and explicit text status. Retain readable original Chinese quotations. English explanations are app-authored summaries, not official translations or entrant-authored submission narration.

## Components

### Source Loader and Parser

`server.py` owns `SourceMetadata`, `SourceStore`, fixed-source downloading and cache validation. Fetch only `https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html`; reject an unexpected final host, limit the response to 1,000,000 bytes and use a 20-second fetch timeout. Verify expected title, publisher and publication-date markers. Record retrieval time and SHA-256 over downloaded bytes. On cache reload, verify integrity and identity before use. The digest is a consistency check against the manifest, not a publisher signature or freshness guarantee.

`evidence.py` owns `_GuideParser` and `parse_document`: extract visible article paragraphs, section context and supported source capabilities. Heading-only or missing article content fails closed. Fetch/cache/parser failures cannot create a supported answer. Implements `prd.md > Source Provenance` and `prd.md > Source and Request Errors`.

### Evidence Schema and Retrieval

The current source-derived schema covers entry/identity verification, filing settings, uploading materials, the conditional undertaking route, viewing progress, listed query services and listed participant groups. Each capability requires matching section context and factual cues in a loaded paragraph. Return at most two matching passages. Public code stores rules and compact annotations, not the complete article. Resolve quotation text from the acquired document.

Use explicit English/Chinese regular expressions for narrow procedural intentions, then source-section/cue checks for evidence. Reject recognized unsupported claims before accepting procedural matches; reject additional unrecognized requests in compound questions. Unsupported personal outcomes, universal/guaranteed claims and unknown intents abstain. Preserve all source conditions for the undertaking topic. There is no current lexical ranking score or model inference; the older ranking experiment in `sources/` is historical development evidence. These inspectable heuristics do not provide general natural-language understanding or exhaustive paraphrase coverage.

Runtime must not read `sources/reference-cases.json`, expected labels, case identifiers, gold paragraph arrays or evaluation reasons. Avoid exact-question-to-answer maps. Example prompts use the same endpoint and pipeline as typed input. Implements `prd.md > Evidence Cards` and `prd.md > Insufficient Evidence`.

### Local HTTP API

Serve only `/`, `/styles.css`, `/app.js`, `/favicon.svg`, `GET /api/health`, `GET /api/source` and `POST /api/search`. Other paths, including traversal and internal-file attempts, return 404. Restrict Host and any supplied Origin to the loopback server address. JSON requests are limited to 16,384 bytes and trimmed questions to 500 characters.

`GET /api/health` returns HTTP 200 with `server: ready` and `source_ready`. `GET /api/source` returns HTTP 200 with `status: ready`, source metadata and capabilities, or HTTP 503 with `status: source_unavailable`. Valid `POST /api/search` requests return HTTP 200 for all three evidence outcomes; an unavailable source returns HTTP 503. Invalid payload/empty/long question returns 400, invalid request size returns 413, wrong content type returns 415, and untrusted Host/Origin returns 403. Unexpected processing failures return 500 with no inferred evidence. Implements `prd.md > Question Input` and `prd.md > Source and Request Errors`.

### Browser Interface

Two demonstrated passages have AI English display translations in `translations.py`, keyed by the SHA-256 of each exact parsed source passage. Changed or unknown text has no stored translation. These annotations are added to presentation data only and are never read by intent, facet, or support rules. The browser labels the translations as AI-authored and nonofficial and retains the original Chinese quotation. Source title/publisher English display labels are also explanatory translations; original metadata stays intact.

Load provenance and submit typed/example questions to the same endpoint. Render successful API statuses `supported`, `conditional` and `insufficient`; for HTTP 503 `source_unavailable`, display a request/source error without inferring a result. An insufficient response may include a related passage explicitly labeled as not proving the claim. Render source/query text as text, not HTML. Clear stale results during a new request, prevent concurrent submissions, expose loading/errors and show conditions and source details. The official link includes a text-fragment hint; section labels and quoted text remain the fallback if browser highlighting fails. Implements `prd.md > Screens and Layout` and all result-state requirements.

## Data Model

- Source metadata: `source_id`, original title/publisher, `published_date`, `retrieved_at`, official `url`, `snapshot_sha256`, and cache/fetch state.
- Runtime passage: stable section locator plus exact text from the verified source, internal paragraph identifier and source identifier.
- Evidence schema entry: topic identifier, section regular expression and required factual cues. This is domain annotation, not test expectations.
- Search request: one bounded `question` string. Do not persist requests or personal data.
- Search response: `question`, `status` (`supported`, `conditional`, `insufficient`), English `reason`, `evidence` array (`id`, `section`, `text`), `source` metadata and `topic`. Related evidence in an insufficient result never changes its rejected status. No confidence or accuracy score is returned.
- Cache: downloaded bytes and acquisition metadata in ignored `.cache/` by default. It is local runtime storage, not a published source artifact. Catalog metadata and a short attributed quotation may remain public; a code license does not license the underlying article.

## File Structure

```text
project/
  server.py                 # download/cache loader, local HTTP entry point and routes
  evidence.py               # article parser, capability/intent rules and abstention
  translations.py           # exact-source-bound English presentation annotations
  web/
    index.html              # one English interface
    styles.css              # readable responsive layout
    app.js                  # form, fetch and safe rendering
  tests/
    test_evidence.py        # behavior, source failure and abstention checks
    test_server.py          # request limits and route/file boundaries
    test_translations.py    # exact binding and evidence-decision independence
  sources/
    catalog.json            # source metadata and short attributed excerpt
    reference-cases.json    # development evaluation only; never a runtime dependency
    retrieval-feasibility.json
    README.md
  devpost/
    scope.md
    prd.md
    spec.md
    checklist.md
    app-map.html            # generated reference route through actual code
  README.md                 # exact start/test commands and limitations
  .gitignore                # private profile, credentials, generated cache exclusions
  .cache/                   # runtime download/manifest; ignored, never HTTP-served
```

The implementation files and `devpost/app-map.html` exist. The map is a reference route; no completed participant tour or learning activity is claimed. Keep the map and public run instructions aligned with actual files.

## External Services and Dependencies

Only the fixed official guide is fetched using an ordinary HTTPS GET; no user query is sent to the source website. No model, database, payment, analytics or hosting service is used. No source-site availability guarantee or reuse license is inferred. Official source: https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html .

## Important Failure Modes

- Official page unavailable, identity changed, or cache invalid: show source unavailable; never fabricate a passage.
- Relevant vocabulary but unsupported conclusion: return insufficient evidence; relevance does not establish support.
- Conditions lost in a conditional result: treat as a failed acceptance check and fix before calling that behavior complete.
- Unrecognized paraphrase: abstain transparently; do not claim broad query coverage.

## What Was Simplified and Why

One guide avoids document selection and conflicting jurisdiction/version logic. Explicit source-derived rules avoid model/API calls and generated policy answers. Local execution avoids deployment work while keeping the entire demonstration observable. Conservative abstention sacrifices recall; heuristic gaps remain possible and require review. No general accuracy or complete policy coverage is established.

## Decisions and Open Issues

The user delegated autonomous planning and preparation; the agent chose these implementation details. The documents remain drafts, and participant plan/prototype review has not happened. No personal learning uncertainty is established. The genuine technical uncertainty is whether bounded English/Chinese rules can distinguish supported questions from related but unsupported conclusions; record independent paraphrase and mixed-question checks during the build. A prior lexical-only experiment exposed that relevance alone was insufficient; it is development evidence, not acceptance or user validation.

Before shipping: verify actual run commands and public links, perform participant hands-on review, record actual contributions, and obtain participant-authored identity/submission responses. No existing draft is silently relabeled learner-approved.

## Implementation Corrections

- 2026-10-25: Aligned this draft with actual port 8768, ignored in-project `.cache/` storage, source loading in `server.py`, parsing/rules in `evidence.py`, three evidence statuses and HTTP 503 source failures. Replaced the earlier proposed ranking description with the implemented source-capability rules. These are factual technical corrections, not participant approval or completed learning.
