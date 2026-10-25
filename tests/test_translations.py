"""Exact display-translation binding and independence from source judgment.

Public tests use short synthetic text. The two real source bindings can also be
checked against EVIDENCE_TEST_SNAPSHOT; no complete source paragraphs or page
are embedded in this test file.
"""

from hashlib import sha256
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from evidence import parse_document, search_document
import translations


PROGRESS_HASH = "39416639dd4ea65157028b10a769f722f7d90670fffb8f39ddb354033a88f488"
UNDERTAKING_HASH = "2391d4a4372a172a3d3a71a6a7b5922d75f66526ea702b3d77c6f9b3b0879fdf"
FIXTURE = """<div id="zoom"><p>二、办理示例</p>
<p>第三步：提交备案材料</p>
<p>有些地区提供个人承诺选项；符合条件且无法提供认定材料的人，需要签名后提交。</p>
<p>第四步：查看备案进度</p>
<p>示例入口的备案记录可以查询进度。</p></div>"""


class TranslationTests(unittest.TestCase):
    def test_only_two_declared_display_annotations_with_clear_provenance(self):
        self.assertEqual(set(translations.DISPLAY_TRANSLATIONS), {PROGRESS_HASH, UNDERTAKING_HASH})
        for digest, annotation in translations.DISPLAY_TRANSLATIONS.items():
            with self.subTest(digest=digest):
                provenance = annotation["provenance"]
                self.assertEqual(provenance["source_paragraph_sha256"], digest)
                self.assertFalse(provenance["official_translation"])
                self.assertFalse(provenance["entrant_authored"])
                self.assertIn("display", provenance["kind"])
                self.assertIn("square brackets", provenance["note"])
                self.assertIn("not approval", provenance["note"])
        conditional = translations.DISPLAY_TRANSLATIONS[UNDERTAKING_HASH]["english_translation"]
        for qualifier in ("Some regions", "eligible", "unable to", "required supporting documentation for recognition", "filing application"):
            self.assertIn(qualifier, conditional)
        self.assertIn("not all application materials", translations.DISPLAY_TRANSLATIONS[UNDERTAKING_HASH]["provenance"]["note"])

    def test_unknown_paragraphs_have_no_translation(self):
        for text in ("An unrelated paragraph.", "备案记录", "个人承诺", "", None):
            with self.subTest(text=text):
                self.assertIsNone(translations.lookup_display_translation(text))

    def test_exact_matching_does_not_trim_normalize_or_fuzzy_match(self):
        original = "Synthetic paragraph; exact characters only."
        digest = sha256(original.encode("utf-8")).hexdigest()
        annotation = {"english_translation": "Display annotation.", "provenance": {"kind": "synthetic test"}}
        with patch.dict(translations.DISPLAY_TRANSLATIONS, {digest: annotation}, clear=True):
            self.assertEqual(translations.lookup_display_translation(original), annotation)
            for changed in (original + " ", " " + original, original.replace(";", ","), original.lower(), original + "."):
                with self.subTest(changed=changed):
                    self.assertIsNone(translations.lookup_display_translation(changed))

    def test_returned_annotation_cannot_mutate_registered_provenance(self):
        original = "A synthetic paragraph."
        digest = sha256(original.encode("utf-8")).hexdigest()
        annotation = {"english_translation": "Example.", "provenance": {"official_translation": False}}
        with patch.dict(translations.DISPLAY_TRANSLATIONS, {digest: annotation}, clear=True):
            returned = translations.lookup_display_translation(original)
            returned["provenance"]["official_translation"] = True
            self.assertFalse(translations.lookup_display_translation(original)["provenance"]["official_translation"])

    def test_support_status_and_original_evidence_do_not_depend_on_translations(self):
        document = parse_document(FIXTURE)
        annotations = {
            sha256(p["text"].encode("utf-8")).hexdigest(): {
                "english_translation": "Synthetic display translation, not policy data.",
                "provenance": {"kind": "synthetic test"},
            }
            for p in document["paragraphs"]
        }
        for question in (
            "备案进度在哪里查？",
            "个人承诺方式怎样申请？",
            "备案记录怎么删除？",
        ):
            with self.subTest(question=question):
                with patch.dict(translations.DISPLAY_TRANSLATIONS, annotations, clear=True):
                    with_annotation = search_document(document, question)
                with patch.dict(translations.DISPLAY_TRANSLATIONS, {}, clear=True):
                    without_annotation = search_document(document, question)
                self.assertTrue(any("english_translation" in p for p in with_annotation["evidence"]))
                self.assertTrue(all("english_translation" not in p for p in without_annotation["evidence"]))
                for key in ("status", "reason", "topic", "evidence_role"):
                    self.assertEqual(with_annotation[key], without_annotation[key])
                self.assertEqual(
                    [(p["id"], p["section"], p["text"]) for p in with_annotation["evidence"]],
                    [(p["id"], p["section"], p["text"]) for p in without_annotation["evidence"]],
                )

    @unittest.skipUnless(os.environ.get("EVIDENCE_TEST_SNAPSHOT"), "Internal source snapshot was not supplied.")
    def test_both_real_paragraph_hashes_match_and_any_text_change_loses_annotation(self):
        document = parse_document(Path(os.environ["EVIDENCE_TEST_SNAPSHOT"]).read_text(encoding="utf-8"))
        annotated = []
        for paragraph in document["paragraphs"]:
            text = paragraph["text"]
            annotation = translations.lookup_display_translation(text)
            if annotation is None:
                continue
            digest = sha256(text.encode("utf-8")).hexdigest()
            annotated.append(digest)
            self.assertEqual(annotation["provenance"]["source_paragraph_sha256"], digest)
            for changed in (text + " ", text[:-1], text.replace("，", ",", 1), text + "改"):
                with self.subTest(digest=digest, changed=changed):
                    self.assertNotEqual(changed, text)
                    self.assertIsNone(translations.lookup_display_translation(changed))
        self.assertCountEqual(annotated, [PROGRESS_HASH, UNDERTAKING_HASH])


if __name__ == "__main__":
    unittest.main()
