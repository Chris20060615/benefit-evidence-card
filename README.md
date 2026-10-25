# Local document evidence prototype

A small local webpage finds original Chinese passages in one selected NHSA guide. It uses explicit English/Chinese procedural rules and checks the loaded source before displaying evidence. It can return `supported`, `conditional`, or `insufficient`; a related passage is not automatically evidence for a claim.

This implementation and its technical documentation were generated with AI assistance under delegated execution. The planning documents in `devpost/` remain `status: draft`; participant plan review, hands-on checks, learning wrap-up, official submission text, public video, and formal competition submission are not completed by this code or by automated tests. This README is technical documentation, not participant-authored submission copy or a confirmed competition project name.

## Run locally

Requirements: Python 3.11 or newer and a modern browser. The application uses only the Python standard library. No package installation, model API key, database, or paid service is needed.

Run from this project directory:

```powershell
python -X utf8 server.py --port 8768
```

Open [http://127.0.0.1:8768/](http://127.0.0.1:8768/). Stop the server with `Ctrl+C`. The server binds to loopback; it is a local demonstration server.

On first use, the server downloads [the selected official guide](https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html), checks its title, publisher and publication date, and parses its article body. It stores the downloaded bytes and acquisition metadata in `.cache/`, which is excluded by `.gitignore`. Later starts reuse a cache only after checking its SHA-256 digest and source identity. A digest checks consistency with the saved manifest; it is not a digital signature or a guarantee that the guide remains current.

```powershell
# Require an existing verified cache; do not make a network request.
python -X utf8 server.py --port 8768 --offline

# Fetch and verify the official source again at startup.
python -X utf8 server.py --port 8768 --refresh-source

# Optional: select a different local cache directory.
python -X utf8 server.py --port 8768 --cache-dir .cache
```

Use `--offline` and `--refresh-source` separately. If no usable source is available, the page remains accessible, but source/search requests return HTTP 503 with `status: source_unavailable`; the app does not invent evidence. The program prints a source error in the terminal. Refresh happens on startup, not through a webpage button.

## Try the bounded behavior

Type a question or select an example; both use the same search endpoint.

- `在哪里查看备案进度？` asks for the guide's progress-viewing procedure.
- `个人承诺方式怎样申请？` should retain the guide's regional and eligibility conditions.
- `我能报销百分之多少？` asks for information this guide cannot establish.

Supported topics are limited to entry/authentication, filing settings, uploading materials, the conditional undertaking route, progress lookup, listed query services, and the guide's listed participant groups. An accepted result means that the passage describes that narrow topic. It does not establish personal eligibility, actual application status, approval timing, reimbursement amounts, or a current nationwide policy. Unknown phrasing may return insufficient evidence. The rules are inspectable heuristics, not a general language model or a measured accuracy guarantee.

Evidence cards retain original Chinese wording, section labels, publisher/date and an official link. English explanations are prototype summaries, not official translations. Source links include a browser text-fragment hint; if highlighting or scrolling is unavailable, use the section label and quoted phrase on the official page.

## Tests and interfaces

```powershell
python -X utf8 -m unittest discover -s tests -v
```

Tests cover the parser, procedural matching, abstention and retained conditions, cache integrity, request validation, unavailable-source responses and route boundaries. An optional real-snapshot test is skipped unless `EVIDENCE_TEST_SNAPSHOT` points to a locally acquired source HTML file. Automated checks are development evidence, not participant validation or a benchmark score.

- `GET /api/health`: server readiness and whether a source is loaded.
- `GET /api/source`: verified-source metadata and recognized source capabilities; HTTP 503 if unavailable.
- `POST /api/search`: JSON such as `{"question":"在哪里查看备案进度？"}`; questions are limited to 500 characters and request bodies to 16,384 bytes.

Search responses contain `question`, `status`, `reason`, `evidence`, `source`, and `topic`. `insufficient` can include a clearly labeled related passage that does not support the rejected claim. Source and question text is rendered with DOM text nodes. Only the frontend HTML, stylesheet, script, favicon and explicit API routes are served; project documents, source caches and arbitrary files are not exposed by the server. Questions are neither persisted nor sent to NHSA; ordinary network requests still reveal network metadata to the source host.

## Files and provenance

- `server.py`: fixed-source download/cache validation, loopback server and HTTP boundaries.
- `evidence.py`: article parsing, source-derived capability checks, intent rules and abstention.
- `web/`: buildless HTML, CSS and JavaScript interface.
- `tests/`: standard-library automated development tests.
- `sources/`: attributed metadata and historical preparation experiments; see [sources/README.md](sources/README.md).
- `devpost/`: draft scope, requirements, technical plan and factual build checklist. The learner profile is ignored by Git.
- `.agents/skills/`: the unchanged official Devpost Learn Skill Pack; provenance is recorded in [devpost/toolkit-source.md](devpost/toolkit-source.md).

The full NHSA article is downloaded only at runtime and is not intended for source-control publication. A public webpage does not by itself establish an open redistribution license. No project code license is asserted over the source article. Keep `.cache/`, credentials and private learning context out of publication, and review staged files and history before publishing; an ignore rule does not remove already tracked material.


The post-review check on 2026-10-25 passed 33 automated tests with the optional local source snapshot, plus an actual Edge browser journey at desktop and 390px mobile widths. See [verification.json](devpost/verification.json) for scope and limits and [the code reference](devpost/app-map.html) for the real query path. This is not participant validation. Project code and technical documentation use the [MIT license](LICENSE), subject to the source/toolkit exclusions stated there.
