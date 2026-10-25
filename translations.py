"""Two exact-paragraph English display annotations, not policy-answer data.

Only SHA-256 digests and translations are stored here, not the Chinese source
paragraphs. Digests bind the exact UTF-8 paragraph text emitted by the article
parser. Lookup performs no trimming, normalization, semantic matching, or API
call. Unknown or changed paragraph text receives no annotation.

These AI-produced display translations are neither official translations nor
entrant-authored submission copy. They must never be used to decide source
capabilities, requested topics, or answerability.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any


_SOURCE_URL = "https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html"
_SNAPSHOT_SHA256 = "f584f02914efae9ba3761fc9afb21e89ada7e391f77881c5c3141aa12098504a"


def _provenance(paragraph_sha256: str) -> dict[str, Any]:
    return {
        "language": "en",
        "kind": "AI-generated display annotation",
        "translator": "AI assistant",
        "official_translation": False,
        "entrant_authored": False,
        "source_url": _SOURCE_URL,
        "source_snapshot_sha256": _SNAPSHOT_SHA256,
        "source_paragraph_sha256": paragraph_sha256,
        "binding": "Exact UTF-8 parsed paragraph text; no normalization during lookup",
        "note": (
            "Labels in square brackets are illustrative English translations of "
            "Chinese interface labels. Completing an application is not approval. "
            "In the conditional passage, supporting documentation means the "
            "source's specific recognition documents, not all application materials. "
            "This annotation is for display only and is not used for answerability."
        ),
    }


DISPLAY_TRANSLATIONS: dict[str, dict[str, Any]] = {
    "39416639dd4ea65157028b10a769f722f7d90670fffb8f39ddb354033a88f488": {
        "english_translation": (
            "Select [Filing records] on the home page to open the out-of-area "
            "medical treatment filing records page and view filing progress in "
            "real time."
        ),
        "provenance": _provenance("39416639dd4ea65157028b10a769f722f7d90670fffb8f39ddb354033a88f488"),
    },
    "2391d4a4372a172a3d3a71a6a7b5922d75f66526ea702b3d77c6f9b3b0879fdf": {
        "english_translation": (
            "Some regions allow insured people to apply for filing through a "
            "personal undertaking. When eligible insured people are unable to "
            "provide the required supporting documentation for recognition, they can select "
            "[Personal undertaking], sign as required, and then select "
            "[Submit filing] to complete the filing application."
        ),
        "provenance": _provenance("2391d4a4372a172a3d3a71a6a7b5922d75f66526ea702b3d77c6f9b3b0879fdf"),
    },
}


def lookup_display_translation(text: str) -> dict[str, Any] | None:
    """Return an independent annotation only for an exact registered paragraph."""
    if not isinstance(text, str):
        return None
    annotation = DISPLAY_TRANSLATIONS.get(sha256(text.encode("utf-8")).hexdigest())
    return deepcopy(annotation) if annotation is not None else None
