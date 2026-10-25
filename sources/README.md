# Source provenance and development evidence

The current project contains a runnable local application in `server.py`, `evidence.py` and `web/`. This directory records its selected source and earlier technical investigations. These notes are AI-assisted technical documentation, not participant-authored submission copy, approved planning, a clinical or policy review, or proof of participant learning.

## Selected source and runtime use

The only runtime source is the National Healthcare Security Administration's [guide published on 2025-03-16](https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html). At startup, `server.py` downloads the article if no valid cache exists, or checks the saved bytes, title, publisher, publication date and retrieval timestamp before reusing the cache. `evidence.py` parses the loaded article and checks explicit procedural capabilities. The runtime does not read the development questions, labels, gold paragraphs, expected statuses or historical ranking report.

Full article bytes acquired by the application remain in ignored `.cache/` by default; earlier preparation snapshots remain in the task's internal `work/` directory. Neither location is intended for public repository inclusion. `.gitignore` is an exclusion mechanism, not a license or a way to remove already tracked history. A public webpage does not establish an open redistribution license, and a project code license does not license the source article. No permission to redistribute the full article is asserted here.

`--offline` requires an existing verified cache. `--refresh-source` fetches again at startup. Source checks establish consistency with the selected article metadata and saved manifest, not current personal eligibility, a publisher-signed snapshot, unchanged official app behavior or present policy applicability. The frontend shows original Chinese evidence and separately labeled English prototype explanations.

## Files in this directory

- `catalog.json`: preparation-time source URL, title, publisher, publication date, retrieval time, downloaded-byte digest and one exact short excerpt. Its timestamp/digest describe that preparation snapshot, not a guarantee that every later runtime download is identical. Its original candidate/review labels are retained as historical provenance.
- `reference-cases.json`: eight AI-reviewed development reference questions: three directly supported, one conditional and four insufficiently supported. These are not participant validation or application acceptance results.
- `retrieval-feasibility.json`: the saved historical lexical-ranking experiment, predating the current application. It is not the current search algorithm or a new application score.
- `answerability-recommendation.md`: the AI's development recommendation after that experiment, not an approved participant decision or evidence that it alone solves every language case.
- `locator-check.json`: earlier static checks of excerpt encoding and a source anchor. It does not certify current browser scrolling/highlighting; the application retains section labels and quoted text as a fallback.
- `hands-on-check-procedure.md`: proposed checks for participants to perform. A written procedure is not evidence that anyone has performed it.

## Historical lexical experiment

The bounded 2026-10-25 experiment retrieved the expected top paragraph for two of three directly supported development questions. Progress-lookup case R02 retrieved a wrong paragraph; two insufficiently supported questions crossed the candidate-display threshold: R05 (nationwide guarantee) and R07 (same-day approval). A separate AI reviewer reproduced that saved report and checked that labels were not ranker inputs. The threshold was fixed for that one experiment, without tuning runs.

These observations explain why the current prototype separates source capability and answerability checks from merely related wording. The current implementation uses explicit section/cue and English/Chinese intent rules; it does not run that lexical ranker. The old observations are preserved without recasting them as current application failures, a new benchmark, or general accuracy. Automated parser/rule/HTTP tests are development checks and do not establish untested paraphrase coverage.

A related passage still may fail to support a personal reimbursement amount, a universal rule, guaranteed approval timing or proxy-document requirements. Conditional evidence must retain its limits. No participant has yet completed the recorded hands-on review or professional source validation, and these files do not assign personal contributions.
