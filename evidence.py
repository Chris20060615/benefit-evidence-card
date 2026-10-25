"""Bounded, source-grounded passage lookup for one public procedural guide.

This is a transparent intent/claim schema, not a semantic model. Questions are
mapped to a small procedural capability, and that capability must also be
present in the parsed document. Unsupported claims are checked before lookup.
No reference-case labels, prewritten answers, remote models, or API keys are
used. Results contain source passages as data, never generated policy advice.
"""

from __future__ import annotations

from html.parser import HTMLParser
import re
from typing import Any


OFFICIAL_SOURCE_URL = "https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html"
MAX_QUESTION_LENGTH = 500


class _GuideParser(HTMLParser):
    """Read visible paragraphs only inside the article's marked content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metadata: dict[str, str] = {}
        self.paragraphs: list[str] = []
        self._active = False
        self._main_div_depth = 0
        self._in_paragraph = False
        self._skip_depth = 0
        self._paragraph_hidden = False
        self._buffer: list[str] = []

    def _finish_paragraph(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buffer)).strip()
        if self._in_paragraph and text and not self._paragraph_hidden:
            self.paragraphs.append(text)
        self._in_paragraph = False
        self._paragraph_hidden = False
        self._buffer = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "meta":
            name = (attributes.get("name") or "").lower()
            content = attributes.get("content")
            if name and content:
                self.metadata[name] = content
            if name == "contentstart" and not self._active:
                self._active = True
            elif name == "contentend":
                self._finish_paragraph()
                self._active = False
            return
        if tag == "div":
            if attributes.get("id") == "zoom" and not self._active:
                self._active = True
                self._main_div_depth = 1
            elif self._active and self._main_div_depth:
                self._main_div_depth += 1
        if not self._active:
            return
        if tag in {"script", "style", "template", "noscript"}:
            self._skip_depth += 1
        if tag == "p" and not self._skip_depth:
            self._finish_paragraph()
            self._in_paragraph = True
            style = re.sub(r"\s+", "", attributes.get("style") or "").lower()
            self._paragraph_hidden = (
                "hidden" in attributes
                or attributes.get("aria-hidden") == "true"
                or "display:none" in style
                or "visibility:hidden" in style
            )
        elif tag == "br" and self._in_paragraph and not self._skip_depth:
            self._buffer.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self._active:
            return
        if tag in {"script", "style", "template", "noscript"}:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "p" and not self._skip_depth:
            self._finish_paragraph()
        elif tag == "div" and self._main_div_depth:
            self._main_div_depth -= 1
            if self._main_div_depth == 0:
                self._finish_paragraph()
                self._active = False

    def handle_data(self, data: str) -> None:
        if self._active and self._in_paragraph and not self._skip_depth:
            self._buffer.append(data)

    def close(self) -> None:
        super().close()
        self._finish_paragraph()


# Each capability needs a matching chapter AND factual cues in source text.
# Cues are source capability checks, not stored answers to example questions.
_CAPABILITY_SCHEMAS = {
    "filing_entry": (r"第一步|开始备案", ("公众号", "实名认证", "备案")),
    "filing_settings": (r"第二步|选择备案类型", ("参保地", "调整", "备案类型")),
    "materials_process": (r"第三步|提交备案材料", ("联系人", "上传", "提交")),
    "personal_undertaking": (r"第三步|提交备案材料", ("地区", "符合条件", "认定材料", "个人承诺", "签名")),
    "filing_progress": (r"第四步|查看备案进度", ("备案记录", "进度")),
    "query_services": (r"此外|查询服务", ("查询",)),
    "listed_groups": (r"哪些参保人员|适用", ("跨省", "人员")),
}

# These patterns express small, inspectable procedural intentions. They do not
# determine answerability alone: _passages() independently checks the source.
_INTENTS = (
    ("personal_undertaking", r"个人承诺|承诺书|认定材料.{0,8}(没有|缺|无法|不能)|(?:无法|没有|缺少|不能提供|提供不了).{0,6}(?:认定材料|证明)|personal (?:undertaking|declaration)|commitment|cannot.{0,20}(?:proof|recognition)|missing.{0,15}proof"),
    ("filing_progress", r"备案记录|filing records?|(?:备案|申请|办理|审核|处理).{0,6}(?:进度|情况|结果)|(?:进度|状态).{0,6}(?:查|看|哪里|如何)|办理到|办到哪|filing.{0,20}(?:status|progress)|(?:track|check|view|where|how).{0,35}(?:status|progress|filing records?)"),
    ("filing_settings", r"(?:参保地|就医地|备案类型|险种).{0,12}(?:改|调整|选择|默认|填)|(?:改|调整|选择|默认|填).{0,12}(?:参保地|就医地|备案类型|险种)|(?:change|edit|select|prefilled|default).{0,35}(?:insurance location|insured location|enrollment location|filing type|treatment location)"),
    ("materials_process", r"(?:材料|资料).{0,8}(?:怎么交|如何交|上传|怎么提交|如何提交)|(?:如何|怎么|怎样).{0,6}(?:上传|提交).{0,6}(?:材料|资料)|(?:upload|submit).{0,15}(?:documents|materials)"),
    ("query_services", r"(?:费用明细|慢特病资格|慢特病告知书|联网定点|定点医药机构|开通情况).{0,10}(?:哪里|怎么|如何|查询)|(?:哪里|怎么|如何|查询).{0,10}(?:费用明细|慢特病资格|慢特病告知书|联网定点|定点医药机构|开通情况)|where.{0,30}(?:expense details|chronic disease|designated facilities)"),
    ("listed_groups", r"哪些(?:参保)?(?:人员|人群|人)|哪类(?:人员|人群|人)|适用(?:人员|人群)|(?:which|what).{0,20}(?:groups|categories of people)|who.{0,20}(?:applies|is covered|can apply)"),
    ("filing_entry", r"(?:微信|公众号|小程序|线上|入口|渠道|实名|开始|发起).{0,20}(?:备案|申请|怎么|如何|哪)|(?:备案|申请).{0,12}(?:入口|渠道|实名|开始|发起|微信|公众号|线上)|(?:start|begin|access|authentication|wechat|official account).{0,35}(?:filing|registration|application)|(?:filing|registration|application).{0,30}(?:start|wechat|authentication|online)"),
)

# A topic match is only a candidate. These positive facets restrict what the
# passage can support; e.g. a record-lookup passage cannot support record deletion.
_SUPPORTED_FACETS = {
    "filing_entry": r"入口|渠道|哪里|哪儿|在哪|怎么|如何|怎样|开始|发起|实名|where|start|begin|access|authentication|verification|how",
    "filing_settings": r"改|调整|选择|默认|填|change|edit|select|prefilled|default",
    "materials_process": r"上传|提交|怎么交|如何交|upload|submit",
    "personal_undertaking": r"申请|办理|提交|签名|签署|使用|怎么用|如何用|条件|流程|认定材料|证明|apply|application|file|submit|sign|use|conditions?|requirements?|route|help|proof",
    "filing_progress": r"查|看|找|追踪|跟踪|哪里|哪儿|在哪|位置|入口|where|check|track|view|look up|find",
    "query_services": r"查|看|哪里|哪些|什么|where|what|which|queries|query|look up|check",
    "listed_groups": r"哪些|哪类|人群|人员|which|what|who|groups|categories",
}

_UNSUPPORTED_ACTIONS = r"删除|删掉|清除|移除|销毁|撤回|撤销|撤掉|取消|作废|注销|重置|恢复|导出|下载|打印|分享|转发|改名|重命名|delete|remove|erase|purge|wipe|cancel|revoke|withdraw|rescind|invalidate|undo|reset|restore|export|download|print|share|rename"
_UNSUPPORTED_FACETS = r"为什么|为何|原因|法律责任|法律效力|处罚|罚款|隐私|安全性|保存期限|保留多久|保存多久|留存多久|记录.{0,8}(?:留多久|存多久|保留几)|申诉|投诉|why|rejection reason|legal|penalt|privacy|retention|how long.{0,15}(?:keep|retain|store)"

# General undertaking questions may use these procedural/condition terms.
# Unrecognized content is rejected instead of guessing that an unfamiliar place
# name or personal detail is covered. This deliberately limits paraphrase recall.
_UNDERTAKING_GENERAL_CN = tuple(sorted({
    "个人承诺书", "个人承诺", "承诺书", "认定材料", "证明材料", "相关材料", "材料", "证明", "有些地区", "部分地区", "符合条件",
    "暂时", "拿不出", "提供不了", "无法", "不能", "没有", "缺少", "不齐", "不全", "缺", "提供", "提交", "上传", "申请", "备案", "办理",
    "怎样", "怎么", "如何", "是否", "可不可以", "能否", "能不能", "可以", "条件", "规定", "要求", "步骤", "流程", "路径", "签署", "签名", "签字", "签",
    "使用", "方式", "什么", "哪些", "允许", "人群", "人员", "参保人", "参保", "请问", "怎么办", "还有", "还能", "还可以", "我们", "我", "如果", "通过", "时候", "做", "填写", "填", "写", "说明", "说", "需要", "用", "走", "时", "后", "在", "先", "再", "的", "但", "就", "要", "该", "需", "吗", "呢", "能", "了", "着", "下", "一下",
}, key=len, reverse=True))
_UNDERTAKING_GENERAL_EN = frozenset("what which how do does can could may i we a an the personal undertaking declaration commitment help when cannot provide missing supporting proof recognition material materials documents application filing registration apply file submit sign use using conditions condition requirements requirement route option work for to of with without and not no have available eligible people some regions it this guide say says describe described".split())


def _matches(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def _passages(document: dict[str, Any], topic: str) -> list[dict[str, str]]:
    schema = _CAPABILITY_SCHEMAS.get(topic)
    if schema is None:
        return []
    section_pattern, required_cues = schema
    passages = []
    for paragraph in document.get("paragraphs", []):
        if not isinstance(paragraph, dict):
            continue
        section = paragraph.get("section", "")
        text = paragraph.get("text", "")
        if not isinstance(section, str) or not isinstance(text, str):
            continue
        if _matches(section_pattern, section) and all(cue in text for cue in required_cues):
            passages.append({"id": str(paragraph.get("id", "")), "section": section, "text": text})
    return passages[:2]


def parse_document(raw_html: str, source: dict[str, Any] | None = None) -> dict[str, Any]:
    """Parse the selected source; malformed or missing article content fails closed.

    ``source`` may add cache/provenance metadata supplied by the fetcher. The
    source URL is fixed to this module's one official guide; no HTML links or
    caller-provided alternate URLs become citation targets.
    """
    if not isinstance(raw_html, str) or not raw_html.strip():
        raise ValueError("No source HTML was provided.")
    if source is not None and not isinstance(source, dict):
        raise ValueError("Source metadata must be a dictionary.")
    if source and source.get("url", OFFICIAL_SOURCE_URL) != OFFICIAL_SOURCE_URL:
        raise ValueError("Only the selected official source URL is supported.")
    parser = _GuideParser()
    parser.feed(raw_html)
    parser.close()
    if not parser.paragraphs:
        raise ValueError("No readable paragraphs were found in the marked article content.")
    metadata: dict[str, Any] = {
        "title": parser.metadata.get("articletitle", ""),
        "publisher": parser.metadata.get("sitename", ""),
        "published_date": parser.metadata.get("pubdate", "")[:10],
    }
    metadata.update(source or {})
    metadata["url"] = OFFICIAL_SOURCE_URL
    paragraphs = []
    main_section = "Article introduction"
    sub_section = ""
    for text in parser.paragraphs:
        if _matches(r"^[一二三四五六七八九十]+[、.]", text):
            main_section, sub_section = text, ""
            continue
        if _matches(r"^第[一二三四五六七八九十\d]+步[：:]", text):
            sub_section = text
            continue
        if text.startswith("此外") and len(text) < 60:
            main_section, sub_section = text, ""
            continue
        paragraphs.append({
            "id": f"p{len(paragraphs) + 1:02d}",
            "section": " > ".join(part for part in (main_section, sub_section) if part),
            "text": text,
        })
    if not paragraphs:
        raise ValueError("The article contains headings but no evidence paragraphs.")
    document: dict[str, Any] = {"source": metadata, "paragraphs": paragraphs}
    document["capabilities"] = [topic for topic in _CAPABILITY_SCHEMAS if _passages(document, topic)]
    return document


def _requested_topic(question: str) -> str | None:
    # A services-overview question is bounded to the overview itself. Merely
    # mentioning "query services" must not endorse an arbitrary queried object.
    if _matches(r"^(?:除了(?:申请)?备案[，,]?)?(?:这个|该)?(?:小程序)?(?:里|中|内)?(?:还有|还能|还可以|可以|能|提供|支持|有)?(?:查询|查)?(?:什么|哪些)(?:查询)?(?:服务|功能|信息|内容|项目)?(?:可以|能)?(?:查询|查)?(?:呢|吗)?[?？。!！]*$", question):
        return "query_services"
    if _matches(r"^(?:(?:what|which) (?:other )?(?:query services|queries|services) (?:are available|can (?:i|users) use|does (?:this|the) (?:mini ?program|app) provide)|what else can (?:i|users) (?:query|look up|check)(?: in (?:this|the) (?:mini ?program|app))?)[\s?.!]*$", question):
        return "query_services"
    for topic, pattern in _INTENTS:
        if _matches(pattern, question):
            return topic
    return None


def _unsupported_facet(question: str, topic: str) -> str | None:
    """Require a supported action/facet, not just a matching document noun."""
    if _matches(_UNSUPPORTED_ACTIONS, question):
        return "The related passage does not document the requested record/declaration action. This guide supports only the stated application and lookup steps, not lifecycle operations such as deletion, cancellation, or export."
    if _matches(_UNSUPPORTED_FACETS, question):
        return "The question asks for an explanation, legal effect, retention rule, or other detail outside this guide's finite procedural support. The related passage does not establish it."
    if _matches(r"(?:修改|编辑|变更|改正|修正|change|edit|modify|amend|correct)", question) and topic != "filing_settings":
        return "The source permits a specific filing-setting adjustment; it does not document changes to records, declarations, or submitted applications."
    if not _matches(_SUPPORTED_FACETS.get(topic, r"(?!)"), question):
        return "A related topic was found, but the question's requested action or detail is not one of the narrow facets supported by this passage."
    if topic == "personal_undertaking":
        if _matches(r"(?:哪些|哪个|哪几|具体).{0,6}(?:地区|地方|省|市)|本地|当地|我这里|我这边|我所在|我省|我市|我区|which.{0,15}(?:regions?|provinces?|cities)|local|in my (?:region|province|city)", question):
            return "The guide says only that some regions offer this route. It does not identify participating regions or establish whether a particular locality accepts it."
        remaining = question
        for term in _UNDERTAKING_GENERAL_CN:
            remaining = remaining.replace(term, "")
        unknown_chinese = re.search(r"[\u3400-\u9fff]", remaining)
        unknown_english = set(re.findall(r"[a-z]+", remaining.lower())) - _UNDERTAKING_GENERAL_EN
        if unknown_chinese or unknown_english or re.search(r"\d", remaining):
            return "The question adds a specific locality, person, or other unrecognized detail. This generic conditional passage cannot establish that detail; ask about its general procedure or conditions only."
    return None


def _unsupported_claim(question: str) -> tuple[str, str | None] | None:
    """Reject unsupported conclusions even if procedural keywords also match."""
    if _matches(r"(?:确认|核实|确定|证明|判断|看出|查明|认定|验证).{0,18}(?:我|本人|个人).{0,8}(?:资格|符合|适用|待遇)|(?:我|本人|个人).{0,12}(?:资格|待遇|适用).{0,12}(?:确认|核实|确定|证明|判断|验证)|(?:confirm|prove|verify|determine|establish|validate).{0,30}(?:my|personal|individual).{0,20}(?:eligibility|qualif|entitlement)", question):
        return ("A lookup method cannot confirm individual eligibility or entitlement. This source does not perform the personal qualification check requested by the question.", "listed_groups")
    if _matches(r"报销.{0,12}(?:比例|百分|多少|几成|金额|额度|[一二三四五六七八九十\d]+成)|百分之|报销率|\d+\s*(?:%|％|percent)|reimbursement.{0,15}(?:rate|percentage|amount)|(?:how much|what percentage).{0,25}(?:reimburs|paid|cover)|多少钱|收费|免费", question):
        return ("This guide does not establish a personal reimbursement amount, rate, or charge. A related passage is not a calculation basis.", None)
    if _matches(r"代办|代申请|代替|代理|(?:帮|替|代).{0,8}(?:父母|父亲|母亲|爸爸|妈妈|家人|孩子|妻子|丈夫|爷爷|奶奶).{0,8}(?:办|申请)|proxy|on behalf|for my (?:parents?|mother|father|child|daughter|son|wife|husband|grandparents?|grandmother|grandfather|family)", question):
        return ("This guide does not specify proxy authorization or the documents required to file for another person.", "materials_process")
    if _matches(r"(?:全国|所有省|所有地区|每个省|各个地区|任何地区|所有地方|任何地方|各省|所有人|任何人|人人)|无论.{0,10}(?:省|地区|地方)|哪个省.{0,8}都|nationwide|everywhere|all (?:regions|provinces|hospitals)|every (?:region|province)|any region|everyone|anyone", question):
        return ("This guide does not establish the requested universal guarantee. Its conditional procedure cannot be generalized to every region or person.", "personal_undertaking")
    if _matches(r"(?:当天|今天|同一天|立刻|立即|马上|当场|24小时|几分钟|明早|很快).{0,10}(?:批|审核|审批|通过|生效)|(?:多久|几天|多长时间|几个工作日|什么时候|何时|几点|几小时).{0,12}(?:通过|办理|审核|审批|生效)|(?:通过|审批|审核|生效).{0,8}(?:多久|几天|多长|时限|几小时)|(?:\d+|[一二三四五六七八九十两半]+).{0,2}(?:小时|天|分钟|工作日).{0,10}(?:批|过|审批|生效)|有效期|有效多久|生效|same.?day|approved today|immediate approval|instantly approved|(?:how long|when).{0,30}(?:approv|take effect)|within.{0,15}(?:hours|days)", question):
        return ("The guide describes submission and progress lookup, but states no approval deadline, processing duration, or effective date.", "filing_progress")
    if _matches(r"(?:保证|一定|肯定|必然|百分之百|100%).{0,12}(?:报销|结算|通过|获批|审批|成功|能备案|能申请)|guarantee|definitely|always.{0,20}(?:approv|reimburs)|automatically approved", question):
        return ("A described application procedure is not a guarantee of approval, reimbursement, or successful settlement.", "filing_progress")
    if _matches(r"(?:哪些|什么|清单|几份|原件|复印件|必需|必须|需要).{0,6}(?:材料|资料|证件)|(?:材料|资料|证件).{0,8}(?:哪些|什么|清单|几份|原件|复印件)|要带什么|身份证|户口本|委托书|which documents|what (?:documents|materials)|list of documents|documents.{0,10}(?:required|need)", question):
        return ("The guide describes uploading relevant material but does not enumerate the requested document checklist.", "materials_process")
    if _matches(r"(?:不用交|不交|无需|免交|不用带|不带).{0,6}(?:任何)?(?:材料|资料|证明)|免材料|no (?:documents|materials)|without any.{0,12}(?:papers|documents|materials)", question):
        return ("The guide does not establish a blanket exemption from supporting material. Its undertaking option has stated limits.", "personal_undertaking")
    if _matches(r"跳过实名|绕过实名|不实名|无需实名|skip.{0,12}(?:authentication|verification)|without.{0,15}(?:authentication|verification)", question):
        return ("The documented entry path includes real-name authentication; this source does not provide an alternative that bypasses it.", "filing_entry")
    if _matches(r"(?:能否|能不能|是否可以|可以|能够|能).{0,8}(?:报销|享受待遇|直接结算)|can.{0,25}(?:reimburse|claim benefits|direct settlement)|计算|算出|预测|推测|推断|calculate|estimate|predict|infer", question):
        return ("This procedural guide does not establish the requested benefit outcome, calculation, prediction, or individual entitlement.", "listed_groups")
    if _matches(r"备案记录.{0,6}(?:还能|能|可以|会|是否).{0,4}(?:查|查询|显示|计算|判断)(?!.*(?:进度|备案|审批|申请|审核|处理))", question):
        return ("This source describes filing-progress lookup, not the different information requested from that record.", "filing_progress")
    method_question = _matches(r"怎么|如何|哪里|哪儿|在哪|怎样|where|how|check|track", question)
    if not method_question and _matches(r"(?:我|本人|这次).{0,16}(?:通过了吗|批准了吗|批下来|成功了吗|生效了吗|符合|有资格|能备案|能申请|享受待遇)|am i eligible|do i qualify|can i (?:file|apply|claim)|(?:has|is).{0,8}my.{0,20}(?:approved|successful)|my eligibility", question):
        return ("The article describes general groups and procedures; it cannot verify your personal eligibility or access your application outcome.", "listed_groups")
    if _matches(r"(?:我|本人|我的).{0,16}(?:资格|待遇|报销).{0,10}(?:能|符合|确认|是否|吗)|my.{0,20}(?:benefit|eligibility).{0,12}(?:is|confirm|qualify)", question) and not method_question:
        return ("This guide cannot determine personal eligibility or benefit entitlement from a question.", "listed_groups")
    return None


def search_document(document: dict[str, Any] | None, question: str) -> dict[str, Any]:
    """Return faithful passages and an explicit bounded answerability status.

    ``insufficient`` may contain a related candidate passage. That passage is
    explicitly not evidence for the rejected claim; the caller must preserve
    status and reason when rendering it. User text and source text are data.
    """
    question_text = question.strip() if isinstance(question, str) else ""
    source = dict(document.get("source", {})) if isinstance(document, dict) and isinstance(document.get("source"), dict) else {}
    source["url"] = OFFICIAL_SOURCE_URL
    result: dict[str, Any] = {
        "question": question_text,
        "status": "insufficient",
        "reason": "",
        "evidence": [],
        "source": source,
        "topic": None,
        "evidence_role": "none",
    }
    if not question_text:
        result["reason"] = "Enter a non-empty question."
        return result
    if len(question_text) > MAX_QUESTION_LENGTH:
        result["reason"] = f"Keep the question within {MAX_QUESTION_LENGTH} characters."
        return result
    if not isinstance(document, dict) or not document.get("paragraphs"):
        result["reason"] = "No usable source document is loaded. No answer can be supported."
        return result
    topic = _requested_topic(question_text)
    rejected = _unsupported_claim(question_text)
    if rejected:
        reason, related_topic = rejected
        result["reason"] = reason
        result["topic"] = related_topic or topic
        result["evidence"] = _passages(document, related_topic or topic or "")
        result["evidence_role"] = "related" if result["evidence"] else "none"
        return result
    # Reject additional unanswered requests rather than letting one recognized
    # procedural clause make a compound question look fully supported.
    clauses = re.split(r"[，,；;。!?？！\n]|另外|顺便|并且|同时还|\band\b|\balso\b", question_text, flags=re.IGNORECASE)
    if len(clauses) > 1:
        for clause in clauses:
            clause = clause.strip()
            if clause and _matches(r"怎么|如何|哪里|是否|能否|可否|可以|能不能|what|how|where|can|will", clause) and _requested_topic(clause) is None:
                result["reason"] = "The question includes an additional request outside this guide's bounded procedural capabilities. Ask one procedural question at a time."
                result["topic"] = topic
                result["evidence"] = _passages(document, topic or "")
                result["evidence_role"] = "related" if result["evidence"] else "none"
                return result
    if topic is None:
        result["reason"] = "This bounded lookup recognizes only specific filing procedures in this one guide; it does not establish an answer to this question."
        return result
    passages = _passages(document, topic)
    result["topic"] = topic
    if not passages:
        result["reason"] = "The requested procedural topic was recognized, but matching supporting content is absent from the loaded source."
        return result
    result["evidence"] = passages
    unsupported_facet = _unsupported_facet(question_text, topic)
    if unsupported_facet:
        result["reason"] = unsupported_facet
        result["evidence_role"] = "related"
        return result
    if topic == "personal_undertaking":
        result["status"] = "conditional"
        result["evidence_role"] = "conditional_basis"
        result["reason"] = "The source describes an option only for some regions and eligible people unable to provide the recognition material. Preserve every condition in the full passage; it does not confirm individual eligibility or approval."
    else:
        result["status"] = "supported"
        result["evidence_role"] = "supporting"
        result["reason"] = "The displayed passage directly describes this narrow procedural topic. It does not verify personal eligibility, application outcomes, or current interface behavior."
    return result
