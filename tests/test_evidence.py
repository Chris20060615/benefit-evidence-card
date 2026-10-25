"""Meaningful source-boundary checks using an explicitly synthetic guide.

No complete official page is redistributed. An optional internal snapshot check
uses EVIDENCE_TEST_SNAPSHOT when supplied by the developer.
"""

import os
from pathlib import Path
import unittest

from evidence import OFFICIAL_SOURCE_URL, parse_document, search_document


FIXTURE = """<!doctype html><html><head>
<meta name="ArticleTitle" content="Synthetic procedural fixture">
<meta name="SiteName" content="Synthetic publisher">
<meta name="PubDate" content="2025-01-02 12:00">
</head><body><p>Navigation: no evidence belongs here.</p><div id="zoom">
<p>一、哪些参保人员适用？</p>
<p>本文列举跨省长期居住人员，以及跨省临时就医人员。</p>
<p>二、备案操作</p><p>第一步：开始备案</p>
<p>在示例公众号找到申请入口，完成<strong>实名认证</strong>后发起备案。</p>
<p>第二步：选择备案类型</p>
<p>默认参保地允许调整；随后选择就医地及备案类型。</p>
<p>第三步：提交备案材料</p>
<p>填写联系人等信息，上传材料，检查后提交。</p>
<p>有些地区提供个人承诺选项；符合条件但无法提交认定材料者可使用，需先签名再申请。</p>
<p>第四步：查看备案进度</p>
<p>打开首页的【备案记录】可查询进度；这里不展示审批结论。</p>
<p>此外，还有哪些查询服务？</p>
<p>其他查询包括联网机构及开通情况。</p>
<p>还可查询费用明细及慢特病资格信息。</p>
<p hidden>Hidden material should not be evidence.</p>
<script>evilSourceScript()</script>
</div><p>Footer: not article evidence.</p></body></html>"""


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.document = parse_document(FIXTURE, {"url": OFFICIAL_SOURCE_URL, "cache_state": "fixture"})

    def search(self, question):
        return search_document(self.document, question)

    def test_parser_decodes_inline_text_and_preserves_provenance(self):
        doc = parse_document(FIXTURE.replace("示例公众号", "示例&amp;公众号"), {"retrieved_at": "fixture-time"})
        entry = next(p for p in doc["paragraphs"] if "实名认证" in p["text"])
        self.assertIn("示例&公众号", entry["text"])
        self.assertNotIn("<strong>", entry["text"])
        self.assertIn("第一步", entry["section"])
        self.assertEqual(doc["source"]["published_date"], "2025-01-02")
        self.assertEqual(doc["source"]["retrieved_at"], "fixture-time")
        text = " ".join(p["text"] for p in doc["paragraphs"])
        self.assertNotIn("Navigation", text)
        self.assertNotIn("Footer", text)
        self.assertNotIn("Hidden material", text)
        self.assertNotIn("evilSourceScript", text)

    def test_unmarked_or_heading_only_source_is_rejected(self):
        for html in ("", "<p>Random unrelated content</p>", '<div id="zoom"><p>第一步：开始备案</p></div>'):
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_document(html)

    def test_alternate_source_cannot_be_misattributed(self):
        with self.assertRaises(ValueError):
            parse_document(FIXTURE, {"url": "https://other.example/document"})

    def test_progress_paraphrases_chinese_and_english(self):
        for question in (
            "刚才申请完，去什么位置能看办理进度？",
            "我想看看备案记录在哪儿。",
            "Where do I track the status of my out-of-province filing?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "supported")
                self.assertEqual(result["topic"], "filing_progress")
                self.assertIn("备案记录", result["evidence"][0]["text"])
                self.assertIn("第四步", result["evidence"][0]["section"])

    def test_settings_paraphrases(self):
        for question in ("系统填好的参保地填错了，能修改吗？", "May I change the prefilled insurance location?"):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "supported")
                self.assertEqual(result["topic"], "filing_settings")

    def test_entry_and_upload_are_separate_procedural_capabilities(self):
        for question, expected in (
            ("Where can I start the filing in WeChat?", "filing_entry"),
            ("怎么在公众号发起备案？", "filing_entry"),
            ("材料如何提交？", "materials_process"),
            ("How do I upload documents?", "materials_process"),
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "supported")
                self.assertEqual(result["topic"], expected)

    def test_conditional_passage_retains_all_limits(self):
        for question in (
            "暂时提供不了认定材料，是否可以走个人承诺？",
            "Can a personal declaration help when I cannot provide supporting proof?",
            "What conditions apply to the personal undertaking route?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "conditional")
                text = result["evidence"][0]["text"]
                for condition in ("有些地区", "符合条件", "无法提交认定材料", "签名"):
                    self.assertIn(condition, text)

    def test_record_lifecycle_actions_are_not_lookup_support(self):
        for question in (
            "备案记录怎么删除？",
            "How do I delete my filing records?",
            "怎样把备案记录清除掉？",
            "备案记录在哪里导出？",
            "Can I download and print my filing records?",
            "查看备案进度后怎么撤销申请？",
            "How do I edit my filing records?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence_role"], "related")
                self.assertTrue(result["evidence"])

    def test_undertaking_lifecycle_and_legal_facets_are_not_generic_conditions(self):
        for question in (
            "个人承诺书可以撤回吗？",
            "How do I cancel a personal undertaking?",
            "个人承诺申请如何作废？",
            "怎么修改已签的个人承诺书？",
            "Can I revoke the personal declaration after submission?",
            "个人承诺的法律责任是什么？",
            "Why can I use a personal undertaking?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence_role"], "related")
                self.assertTrue(result["evidence"])

    def test_undertaking_does_not_resolve_named_or_unspecified_localities(self):
        for question in (
            "北京支持个人承诺吗？",
            "上海如何申请个人承诺？",
            "佛山个人承诺怎么用？",
            "在兰州提供不了认定材料，能使用个人承诺吗？",
            "哪些地区允许个人承诺？",
            "个人承诺在我所在地区能用吗？",
            "How do I apply using a personal undertaking in Hangzhou?",
            "What conditions apply to the personal undertaking route in my city?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence_role"], "related")
                self.assertTrue(result["evidence"])

    def test_lookup_words_cannot_override_personal_qualification_claim(self):
        for question in (
            "在哪里看备案进度就能确认我的资格？",
            "怎么查询备案记录来核实本人资格？",
            "查看备案结果能证明我的待遇吗？",
            "Where can I check filing status to confirm my eligibility?",
            "How do filing records prove my entitlement?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertIn("individual eligibility", result["reason"])
                self.assertEqual(result["evidence_role"], "related")

    def test_unknown_requested_facets_fail_closed_with_related_passages(self):
        for question in ("备案记录的保留多久？", "个人承诺的编号编码规则是什么？", "How do personal declarations expire?"):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence_role"], "related")

    def test_supported_actions_still_work_after_facet_checks(self):
        for question, status in (
            ("备案进度在哪里查？", "supported"),
            ("参保地可不可以调整？", "supported"),
            ("个人承诺方式怎样申请？", "conditional"),
            ("What conditions apply to the personal undertaking route?", "conditional"),
        ):
            with self.subTest(question=question):
                self.assertEqual(self.search(question)["status"], status)

    def test_unknown_questions_do_not_become_supported(self):
        for question in ("头痛应该吃啥药？", "请推荐明天去哪里吃饭", "What is the weather tomorrow?", "查询服务能查养老金吗？", "What query services can I use for pension payments?"):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence"], [])

    def test_query_overview_does_not_authorize_arbitrary_query_objects(self):
        for question in ("还有哪些查询服务呢？", "除了备案还能查什么？", "What other query services are available?"):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "supported")
                self.assertEqual(result["topic"], "query_services")
        self.assertEqual(self.search("备案记录里能查询养老金吗？")["status"], "insufficient")

    def test_procedural_clause_cannot_cover_an_unrelated_second_request(self):
        result = self.search("备案进度怎么看，明天北京天气如何？")
        self.assertEqual(result["status"], "insufficient")
        self.assertIn("additional request", result["reason"])

    def test_personal_rate_and_amount_never_inferred_from_topic(self):
        for question in (
            "看完备案记录能知道我这次报销几成吗？",
            "Where can I find my exact reimbursement percentage?",
            "今天申请后医保能给我报销多少钱？",
            "备案记录怎么查，报销八成对吧？",
            "Will the filing cover 80 percent of my bill?",
        ):
            with self.subTest(question=question):
                result = self.search(question)
                self.assertEqual(result["status"], "insufficient")
                self.assertIn("amount, rate", result["reason"])

    def test_universal_claim_does_not_get_a_conditional_yes(self):
        result = self.search("无论在哪个省，我都能仅靠承诺书申请吗？")
        self.assertEqual(result["status"], "insufficient")
        self.assertIn("universal", result["reason"])
        self.assertIn("有些地区", result["evidence"][0]["text"])

    def test_turnaround_guarantees_and_compound_queries_fail_closed(self):
        for question in (
            "怎么查备案进度，另外能保证明早批准吗？",
            "Will my filing be automatically approved today?",
            "个人承诺书提交多久生效？",
            "备案后肯定能直接结算成功吗？",
            "个人承诺什么时候审批通过？",
            "承诺书提交两小时内能批下来吗？",
        ):
            with self.subTest(question=question):
                self.assertEqual(self.search(question)["status"], "insufficient")

    def test_entry_keywords_do_not_prove_benefit_outcomes(self):
        result = self.search("公众号完成备案后就可以报销吗？")
        self.assertEqual(result["status"], "insufficient")

    def test_proxy_and_exact_material_checklists_are_not_invented(self):
        for question in (
            "帮我妈妈办理备案，需要哪些纸质文件？",
            "Which documents are required for filing?",
            "Can I submit on behalf of my father?",
            "不带任何证明就能成功备案吗？",
        ):
            with self.subTest(question=question):
                self.assertEqual(self.search(question)["status"], "insufficient")

    def test_personal_eligibility_and_actual_status_are_not_verified(self):
        for question in (
            "我是自由职业者，这份指南能确认我符合备案资格吗？",
            "查下我刚提交的备案有没有批下来。",
            "Am I eligible to apply for filing?",
        ):
            with self.subTest(question=question):
                self.assertEqual(self.search(question)["status"], "insufficient")

    def test_absent_source_capability_overrides_recognized_question(self):
        altered = FIXTURE.replace("打开首页的【备案记录】可查询进度；这里不展示审批结论。", "这段没有进度查询方法。")
        document = parse_document(altered)
        # An externally supplied capabilities list is not an answerability bypass.
        document["capabilities"] = ["filing_progress"]
        result = search_document(document, "Where do I check my filing status?")
        self.assertEqual(result["status"], "insufficient")
        self.assertEqual(result["evidence"], [])

    def test_matching_words_in_wrong_section_are_not_support(self):
        document = parse_document('<div id="zoom"><p>闲聊中提到备案记录和进度。</p></div>')
        self.assertEqual(search_document(document, "备案进度怎么查？")["status"], "insufficient")

    def test_blank_long_invalid_and_missing_source_inputs(self):
        for question in ("", "   ", None, "备" * 501):
            with self.subTest(question=question):
                result = search_document(self.document, question)
                self.assertEqual(result["status"], "insufficient")
                self.assertEqual(result["evidence"], [])
        self.assertEqual(search_document(None, "备案进度怎么查？")["status"], "insufficient")

    @unittest.skipUnless(os.environ.get("EVIDENCE_TEST_SNAPSHOT"), "Internal source snapshot was not supplied.")
    def test_optional_internal_official_snapshot(self):
        document = parse_document(Path(os.environ["EVIDENCE_TEST_SNAPSHOT"]).read_text(encoding="utf-8"))
        for question, status in (
            ("在哪里查看备案进度？", "supported"),
            ("个人承诺方式怎样申请？", "conditional"),
            ("我能报销百分之多少？", "insufficient"),
        ):
            with self.subTest(question=question):
                result = search_document(document, question)
                self.assertEqual(result["status"], status)
                for paragraph in result["evidence"]:
                    self.assertTrue(any(paragraph["text"] == p["text"] for p in document["paragraphs"]))


if __name__ == "__main__":
    unittest.main()
