# Separating relevant text from a supported conclusion

Status: technical recommendation for review, based on the 2026-10-25 development experiment. This is not an approved product specification or a completed implementation.

The candidate should preserve a visible distinction between a related passage and evidence that answers the requested conclusion. A ranking score should select possible passages, not certify an answer.

## R02: progress lookup ranked incorrectly

The query asks where to view progress. The lexical experiment ranked a materials paragraph above the progress paragraph. Generic words about application and submission can outweigh the specific action being requested.

A small proposed investigation is to include the source section heading with each paragraph and retain the requested action when ranking. The explicit progress section should be examined before presenting a result for a progress question. This recommendation has not been implemented or tested; heading context is not proof that arbitrary questions will be understood.

## R05: a limited path cannot support a nationwide guarantee

The source's personal-commitment route is limited to some regions, eligible participants and inability to provide the relevant recognition materials. A query about every region asks for a stronger conclusion. A related paragraph may be shown as context, but the guide provides insufficient evidence for the nationwide claim.

Any future supported response must preserve all relevant conditions in its evidence span. It must not turn an example route into a personal eligibility decision.

## R07: progress lookup cannot establish same-day approval

The source describes submitting an application and checking progress. It does not state an approval deadline. Those operations cannot support a same-day guarantee.

An implementation needs evidence about the requested outcome or timing before making that claim. Additional overlap with application-related words does not provide it.

## Small recommended boundary

For the candidate's initial experiment, return an attributed evidence passage when it supports the narrow document question. Where the requested conclusion is not stated or requires missing personal inputs, report insufficient evidence and identify the document being checked. Related context can remain available for inspection with its limits visible.

The tradeoff is conservative coverage: some useful questions may remain unresolved. It keeps the demonstration small and checkable, without claiming a general policy adviser. Actual automatic answerability remains an implementation risk; this note does not solve or measure it.

The one-page product boundary and its exact behavior still require participant choice under the official learning workflow. Do not tune the threshold repeatedly against these eight seen questions or treat them as unseen evaluation.
