from __future__ import annotations

import io
import json
import random
import re
import zipfile
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape


PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
SLIDE_CX = 12192000
SLIDE_CY = 6858000
LAYOUTS = {"hero", "split", "metrics", "timeline", "cards", "closing"}
PITCH_DECK_TEMPLATES = (
    "classic_left_rail",
    "executive_header",
    "corner_focus",
    "ledger_grid",
)

CREATIVE_DECK_SYSTEM_PROMPT = """You design evidence-rich grant pitch decks for Malaysian SMEs.
Return compact JSON only:
{"slides":[{"title":"","subtitle":"","layout":"hero|split|metrics|timeline|cards|closing","accent_color":"0087A5","bullets":[""],"metrics":[{"label":"","value":""}],"grant_alignment":"","speaker_notes":""}]}
Rules: 8 slides max, 4-5 specific bullets per slide, 3 metrics max per slide, no Markdown, no external assets, professional government-grant style. Use available facts, funding figures, eligibility evidence, use of funds, timeline, KPIs, risks, and closing request. Do not invent traction or partners."""


def build_pitch_deck_slides(
    sme_profile: Mapping[str, Any],
    grant_context: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    grant_context = grant_context or {}
    company = _text(sme_profile, "company_name", "SME Company")
    sector = _text(sme_profile, "sector", "industry", "the target sector")
    grant_name = _text(grant_context, "grant_name", "title", "Target Grant")
    provider = _text(grant_context, "provider_name", "provider", "Grant Provider")
    employees = _text(sme_profile, "full_time_employees", "employee_count", "not specified")
    age = _text(sme_profile, "age_in_months", "not specified")
    ownership = _text(sme_profile, "ownership_majority", "nationality", "not specified")
    project_cost_value = _value(sme_profile, "total_project_cost_rm", "project_cost_rm")
    funding_value = _value(sme_profile, "requested_funding_rm", "target_grant_amount")
    outsourced_value = _value(sme_profile, "outsourced_cost_rm")
    project_cost = _money(project_cost_value)
    funding = _money(funding_value)
    outsourced = _money(outsourced_value)
    grant_cap = _money(_value(grant_context, "amount_max", "max_funding_rm"))
    funding_share = _percentage(funding_value, project_cost_value)
    outsourcing_share = _percentage(outsourced_value, project_cost_value)
    partner = "Confirmed" if bool(_value(sme_profile, "has_end_user_partner")) else "To be confirmed"
    summary = _text(sme_profile, "summary", "Local SME seeking growth funding.")
    deadline = _text(grant_context, "application_deadline", "to be confirmed")
    grant_description = _text(
        grant_context,
        "description",
        "Grant support for eligible Malaysian SME growth, capability-building, or commercialisation projects.",
    )
    eligibility = _text(
        grant_context,
        "eligibility_notes",
        "Eligibility should be confirmed against the latest provider criteria before submission.",
    )
    mandatory_documents = _list_text(_value(grant_context, "mandatory_documents", "documents_required"))
    profile_documents = _list_text(_value(sme_profile, "documents_provided"))
    documents = mandatory_documents or profile_documents
    document_count = len(documents)
    document_summary = _clip(", ".join(documents[:4]) + ("..." if len(documents) > 4 else ""), 118) or "Required documents to be confirmed"

    return [
        {
            "title": f"{company}",
            "subtitle": f"{grant_name} application pitch deck",
            "layout": "hero",
            "accent_color": "0087A5",
            "bullets": [
                f"Prepared for {provider} with a focused funding request of {funding}.",
                f"Total project cost is {project_cost}; requested support represents {funding_share} of the project.",
                f"Sector focus: {sector}; submission deadline: {deadline}.",
                "Deck narrative is aligned to the proposal, application checklist, and supporting evidence.",
            ],
            "metrics": [
                {"label": "Funding Request", "value": funding},
                {"label": "Project Cost", "value": project_cost},
                {"label": "Grant Cap", "value": grant_cap},
            ],
            "grant_alignment": f"Frames the applicant and funding ask for {grant_name}.",
            "speaker_notes": f"Open by naming {company}, the target grant, the requested amount, and why the project is ready for assessment.",
        },
        {
            "title": "Company Snapshot",
            "subtitle": "Eligibility and operating profile",
            "layout": "split",
            "accent_color": "494BD6",
            "bullets": [
                _clip(summary, 130),
                f"{company} operates in {sector} with {employees} full-time employee(s).",
                f"Operating history is {age} months with ownership or nationality recorded as {ownership}.",
                f"End-user partner status: {partner}; use this as a readiness signal during review.",
                f"Key application documents: {document_summary}.",
            ],
            "metrics": [
                {"label": "Operating History", "value": f"{age} months"},
                {"label": "Ownership / Nationality", "value": ownership},
                {"label": "Team Size", "value": str(employees)},
            ],
            "grant_alignment": "Shows the reviewer the company facts needed for first-pass eligibility screening.",
            "speaker_notes": "Use this slide to establish credibility before discussing the project. Keep the profile factual and point reviewers to stored documents.",
        },
        {
            "title": "Problem And Opportunity",
            "subtitle": "Why the project deserves support now",
            "layout": "cards",
            "accent_color": "00A676",
            "bullets": [
                _clip(grant_description, 128),
                "The project addresses a practical gap in capacity, delivery quality, validation, or market readiness.",
                "Without co-funding, the company may need to slow implementation, reduce scope, or defer validation work.",
                f"The opportunity is to convert {sector} capability into a more evidence-ready commercial project.",
            ],
            "grant_alignment": f"Connects the business need to the public funding purpose of {grant_name}.",
            "speaker_notes": "Explain the pain point in plain business terms, then tie it to the grant provider's expected impact.",
        },
        {
            "title": "Solution And Differentiation",
            "subtitle": "A focused implementation plan",
            "layout": "split",
            "accent_color": "E09F3E",
            "bullets": [
                f"Build or enhance a focused {sector} solution tied to the funded project scope.",
                "Prioritise internal capability, accountable owners, milestone evidence, and controlled supplier delivery.",
                "Use validation activity to prove the solution works for target users before wider commercial scaling.",
                f"End-user partner status: {partner}.",
            ],
            "metrics": [
                {"label": "Internal Team", "value": str(employees)},
                {"label": "Partner Status", "value": partner},
            ],
            "grant_alignment": "Shows how the proposed activity turns funding into a concrete implementation project.",
            "speaker_notes": "Describe what will actually be built or improved, how it is differentiated, and how the team will prove delivery.",
        },
        {
            "title": "Grant Alignment",
            "subtitle": "How the application maps to review criteria",
            "layout": "metrics",
            "accent_color": "0087A5",
            "bullets": [
                _clip(eligibility, 128),
                f"Funding ask of {funding} is assessed against grant cap of {grant_cap}.",
                f"Sector and nationality fit should be reviewed as {sector} and {ownership}.",
                f"Mandatory documents tracked for this grant: {document_summary}.",
                "Proposal, deck, and script should use the same figures and claims.",
            ],
            "metrics": [
                {"label": "Documents Tracked", "value": str(document_count)},
                {"label": "Funding Ask", "value": funding},
                {"label": "Grant Cap", "value": grant_cap},
            ],
            "grant_alignment": "Makes the evaluator's checklist visible inside the pitch deck.",
            "speaker_notes": "Walk reviewers through fit signals and call out any items still marked to be confirmed.",
        },
        {
            "title": "Use Of Funds",
            "subtitle": "Budget logic and governance",
            "layout": "split",
            "accent_color": "494BD6",
            "bullets": [
                f"Requested funding: {funding}; total project cost: {project_cost}; funding share: {funding_share}.",
                "Allocate funds to delivery work packages, validation, commercial readiness, and reporting evidence.",
                f"Outsourced cost is {outsourced}, representing {outsourcing_share} of total project cost where data is available.",
                "Maintain procurement records, claims evidence, budget tracking, and milestone approvals for audit readiness.",
            ],
            "metrics": [
                {"label": "Funding Share", "value": funding_share},
                {"label": "Outsourcing", "value": outsourced},
                {"label": "Outsource Share", "value": outsourcing_share},
            ],
            "grant_alignment": "Shows the funding request is controlled, auditable, and tied to eligible outcomes.",
            "speaker_notes": "This is the finance confidence slide. Say how the funds will be governed, not only what they will buy.",
        },
        {
            "title": "Timeline And KPIs",
            "subtitle": "Milestone-based execution",
            "layout": "timeline",
            "accent_color": "00A676",
            "bullets": [
                "Month 1: finalize scope, internal owners, vendor checks, and evidence checklist.",
                "Months 2-3: execute main delivery work packages and capture milestone proof.",
                "Month 4: validate outcomes, reconcile spend, prepare reporting pack, and close audit gaps.",
                "KPIs: milestone completion, evidence readiness, budget control, delivery quality, and adoption path.",
            ],
            "grant_alignment": "Gives the panel a practical delivery path for post-award monitoring.",
            "speaker_notes": "Present this as a commitment plan. Mention who owns tracking and how the team will know each milestone is complete.",
        },
        {
            "title": "Outcomes And Closing Request",
            "subtitle": "Decision-ready summary",
            "layout": "closing",
            "accent_color": "494BD6",
            "bullets": [
                f"Aligned to {grant_name} by {provider}.",
                f"{company} is requesting {funding} to deliver measurable, evidence-backed project outcomes.",
                "Expected benefits include stronger capability, clearer market readiness, and improved delivery confidence.",
                "Key risks are document delay, supplier delivery, budget variance, and weak evidence; mitigations are built into governance.",
                "Closing ask: approve support subject to final document verification and provider assessment.",
            ],
            "grant_alignment": "Ends with the award decision the panel is being asked to make.",
            "speaker_notes": "Close with confidence, restate the amount requested, and invite questions on eligibility, budget, milestones, or evidence.",
        },
    ]


def build_pitch_deck_pptx(
    sme_profile: Mapping[str, Any],
    grant_context: Mapping[str, Any] | None = None,
) -> bytes:
    slides = build_pitch_deck_slides(sme_profile, grant_context)
    return build_pitch_deck_pptx_from_slides(slides)


async def build_creative_pitch_deck_pptx(
    sme_profile: Mapping[str, Any],
    grant_context: Mapping[str, Any] | None = None,
    api_key: str | None = None,
) -> tuple[bytes, dict[str, Any]]:
    fallback_slides = build_pitch_deck_slides(sme_profile, grant_context)
    try:
        plan = await generate_creative_deck_plan(sme_profile, grant_context, api_key=api_key)
    except Exception as exc:  # noqa: BLE001
        return build_pitch_deck_pptx_from_slides(fallback_slides), {
            "slides": fallback_slides,
            "generation_mode": "deterministic_fallback",
            "fallback_reason": str(exc)[:240],
        }
    slides = _normalize_ai_slides(plan, fallback_slides)
    return build_pitch_deck_pptx_from_slides(slides), {"slides": slides}


async def generate_creative_deck_plan(
    sme_profile: Mapping[str, Any],
    grant_context: Mapping[str, Any] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    from .glm_client import GLMClient

    payload = {
        "profile": _compact_profile(sme_profile),
        "grant": _compact_grant(grant_context or {}),
    }
    client = GLMClient(api_key=api_key)
    return await client.generate_json(
        system_prompt=CREATIVE_DECK_SYSTEM_PROMPT,
        user_prompt=json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
        temperature=0.85,
    )


def build_pitch_deck_pptx_from_slides(
    slides: list[dict[str, Any]],
    template: str | None = None,
) -> bytes:
    selected_template = _resolve_template(template)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as deck:
        _write_static_parts(deck, len(slides))
        for index, slide in enumerate(slides, start=1):
            deck.writestr(f"ppt/slides/slide{index}.xml", _slide_xml(index, slide, selected_template))
            deck.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", _slide_rels_xml())
    return buffer.getvalue()


def save_pitch_deck_pptx(
    path: str,
    sme_profile: Mapping[str, Any],
    grant_context: Mapping[str, Any] | None = None,
) -> None:
    with open(path, "wb") as file:
        file.write(build_pitch_deck_pptx(sme_profile, grant_context))


def _compact_profile(sme_profile: Mapping[str, Any]) -> dict[str, Any]:
    keys = [
        "company_name",
        "ssm_number",
        "sector",
        "industry",
        "summary",
        "business_stage",
        "annual_revenue",
        "age_in_months",
        "full_time_employees",
        "employee_count",
        "ownership_majority",
        "nationality",
        "total_project_cost_rm",
        "requested_funding_rm",
        "target_grant_amount",
        "outsourced_cost_rm",
        "has_end_user_partner",
        "documents_provided",
    ]
    return _compact_dict(sme_profile, keys, max_text=180)


def _compact_grant(grant_context: Mapping[str, Any]) -> dict[str, Any]:
    keys = [
        "grant_name",
        "title",
        "provider_name",
        "provider",
        "description",
        "eligibility_notes",
        "industry",
        "nationality",
        "amount_min",
        "amount_max",
        "max_funding_rm",
        "application_deadline",
        "mandatory_documents",
        "requirements",
        "application_roadmap",
    ]
    return _compact_dict(grant_context, keys, max_text=180)


def _compact_dict(source: Mapping[str, Any], keys: list[str], max_text: int) -> dict[str, Any]:
    compact = {}
    for key in keys:
        value = source.get(key)
        if value in (None, "", [], {}):
            continue
        compact[key] = _clip(str(value), max_text) if isinstance(value, str) else value
    return compact


def _normalize_ai_slides(plan: Mapping[str, Any], fallback_slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_slides = plan.get("slides") if isinstance(plan, Mapping) else None
    if not isinstance(raw_slides, list):
        return fallback_slides

    slides = []
    for index, raw in enumerate(raw_slides[:8], start=1):
        if not isinstance(raw, Mapping):
            continue
        title = _clip(str(raw.get("title") or f"Slide {index}"), 58)
        bullets = [
            _clip(str(item), 135)
            for item in raw.get("bullets", [])
            if item not in (None, "")
        ][:5]
        metrics = []
        for metric in raw.get("metrics", [])[:3]:
            if not isinstance(metric, Mapping):
                continue
            metrics.append(
                {
                    "label": _clip(str(metric.get("label") or "Metric"), 28),
                    "value": _clip(str(metric.get("value") or ""), 32),
                }
            )
        slides.append(
            {
                "title": title,
                "subtitle": _clip(str(raw.get("subtitle") or ""), 82),
                "layout": raw.get("layout") if raw.get("layout") in LAYOUTS else "split",
                "accent_color": _safe_color(raw.get("accent_color"), None),
                "bullets": bullets or fallback_slides[min(index - 1, len(fallback_slides) - 1)]["bullets"][:5],
                "metrics": metrics,
                "grant_alignment": _clip(str(raw.get("grant_alignment") or ""), 160),
                "speaker_notes": _clip(str(raw.get("speaker_notes") or ""), 320),
            }
        )

    if not slides:
        return fallback_slides
    if len(slides) < len(fallback_slides):
        slides.extend(fallback_slides[len(slides) : 8])
    return slides


def _text(source: Mapping[str, Any], *keys_and_default: str) -> str:
    *keys, default = keys_and_default
    for key in keys:
        value = source.get(key)
        if value not in (None, "", [], {}):
            return str(value)
    return default


def _value(source: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = source.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _money(value: Any) -> str:
    try:
        return f"RM {float(value):,.0f}"
    except (TypeError, ValueError):
        return "RM not specified"


def _percentage(part: Any, total: Any) -> str:
    try:
        total_float = float(total)
        if total_float <= 0:
            return "not specified"
        return f"{(float(part) / total_float) * 100:.0f}%"
    except (TypeError, ValueError):
        return "not specified"


def _list_text(value: Any) -> list[str]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, (list, tuple, set)):
        return [str(value)]

    items: list[str] = []
    for item in value:
        if item in (None, "", [], {}):
            continue
        if isinstance(item, Mapping):
            text = item.get("name") or item.get("title") or item.get("document_type") or item.get("description")
            if text not in (None, "", [], {}):
                items.append(str(text))
            continue
        items.append(str(item))
    return items


def _clip(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip() + "."


def _safe_color(value: Any, fallback: str | None = "0087A5") -> str | None:
    if not isinstance(value, str):
        return fallback
    candidate = value.strip().lstrip("#").upper()
    if re.fullmatch(r"[0-9A-F]{6}", candidate):
        return candidate
    return fallback


def _resolve_template(template: str | None) -> str:
    if template in PITCH_DECK_TEMPLATES:
        return str(template)
    return random.choice(PITCH_DECK_TEMPLATES)


def _write_static_parts(deck: zipfile.ZipFile, slide_count: int) -> None:
    deck.writestr("[Content_Types].xml", _content_types_xml(slide_count))
    deck.writestr("_rels/.rels", _root_rels_xml())
    deck.writestr("docProps/core.xml", _core_xml())
    deck.writestr("docProps/app.xml", _app_xml(slide_count))
    deck.writestr("ppt/presentation.xml", _presentation_xml(slide_count))
    deck.writestr("ppt/_rels/presentation.xml.rels", _presentation_rels_xml(slide_count))
    deck.writestr("ppt/theme/theme1.xml", _theme_xml())
    deck.writestr("ppt/slideMasters/slideMaster1.xml", _slide_master_xml())
    deck.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", _slide_master_rels_xml())
    deck.writestr("ppt/slideLayouts/slideLayout1.xml", _slide_layout_xml())
    deck.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", _slide_layout_rels_xml())
    deck.writestr("ppt/presProps.xml", "<p:presentationPr xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\"/>")
    deck.writestr("ppt/viewProps.xml", "<p:viewPr xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\"/>")
    deck.writestr("ppt/tableStyles.xml", "<a:tblStyleLst xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" def=\"{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}\"/>")


def _content_types_xml(slide_count: int) -> str:
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  {slide_overrides}
</Types>"""


def _root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def _core_xml() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Grantly Pitch Deck</dc:title>
  <dc:creator>Grantly Drafter Agent</dc:creator>
  <cp:lastModifiedBy>Grantly Drafter Agent</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def _app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Grantly</Application>
  <PresentationFormat>Wide</PresentationFormat>
  <Slides>{slide_count}</Slides>
</Properties>"""


def _presentation_xml(slide_count: int) -> str:
    slide_ids = "\n".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_CX}" cy="{SLIDE_CY}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def _presentation_rels_xml(slide_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    ]
    rels.extend(
        [
            f'<Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
            f'<Relationship Id="rId{slide_count + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>',
            f'<Relationship Id="rId{slide_count + 3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>',
            f'<Relationship Id="rId{slide_count + 4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>',
            f'<Relationship Id="rId{slide_count + 5}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
        ]
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {"".join(rels)}
</Relationships>"""


def _slide_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def _slide_xml(index: int, slide: Mapping[str, Any], template: str) -> str:
    title = escape(str(slide.get("title", "")))
    subtitle = slide.get("subtitle")
    bullets = [escape(str(item)) for item in slide.get("bullets", [])[:5]]
    metrics = [
        {"label": escape(str(item.get("label", ""))), "value": escape(str(item.get("value", "")))}
        for item in slide.get("metrics", [])[:3]
        if isinstance(item, Mapping)
    ]
    layout = slide.get("layout") if slide.get("layout") in LAYOUTS else None
    accent = _safe_color(slide.get("accent_color"), None) or ["0087A5", "494BD6", "00A676", "E09F3E"][(index - 1) % 4]
    body = _slide_body(index, layout or "split", title, escape(str(subtitle or "")), bullets, metrics, accent)
    footer = _footer(index, template)
    background = _template_background(template)
    chrome = _template_chrome(index, accent, template)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="{background}"/></a:solidFill></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {chrome}
      {body}
      {footer}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def _template_background(template: str) -> str:
    return {
        "classic_left_rail": "F8FBFC",
        "executive_header": "FFFFFF",
        "corner_focus": "FBFCFD",
        "ledger_grid": "FFFFFF",
    }.get(template, "F8FBFC")


def _template_chrome(index: int, accent: str, template: str) -> str:
    if template == "executive_header":
        return _executive_header_template(index, accent)
    if template == "corner_focus":
        return _corner_focus_template(index, accent)
    if template == "ledger_grid":
        return _ledger_grid_template(index, accent)
    return _accent_bar(index, accent)


def _executive_header_template(index: int, accent: str) -> str:
    return (
        _rect(910, 0, 0, SLIDE_CX, 520000, "EEF7F9", geometry="rect")
        + _rect(911, 0, 0, SLIDE_CX, 105000, accent, geometry="rect")
        + _rect(912, 10800000, 0, 1320000, 520000, "0A3945", geometry="rect")
        + _rect(913, 0, 6320000, SLIDE_CX, 70000, "D8E5E9", geometry="rect")
        + _textbox(914, 10930000, 170000, 1000000, 210000, f"{index:02d}", 1050, "FFFFFF", bold=True)
    )


def _corner_focus_template(index: int, accent: str) -> str:
    return (
        _rect(920, 0, 0, 2580000, SLIDE_CY, "F1F6F8", geometry="rect")
        + _rect(921, 0, 0, 2580000, 160000, accent, geometry="rect")
        + _rect(922, 10480000, 5280000, 1350000, 1010000, "E9F2F5", geometry="rect")
        + _rect(923, 10820000, 5550000, 760000, 480000, accent, geometry="rect")
        + _textbox(924, 320000, 6280000, 1500000, 220000, f"SLIDE {index:02d}", 950, "78909C", bold=True)
    )


def _ledger_grid_template(index: int, accent: str) -> str:
    grid = (
        _rect(930, 0, 1040000, SLIDE_CX, 26000, "EEF3F5", geometry="rect")
        + _rect(931, 0, 2160000, SLIDE_CX, 26000, "EEF3F5", geometry="rect")
        + _rect(932, 0, 3280000, SLIDE_CX, 26000, "EEF3F5", geometry="rect")
        + _rect(933, 0, 4400000, SLIDE_CX, 26000, "EEF3F5", geometry="rect")
        + _rect(934, 3050000, 0, 26000, SLIDE_CY, "F2F6F7", geometry="rect")
        + _rect(935, 6100000, 0, 26000, SLIDE_CY, "F2F6F7", geometry="rect")
        + _rect(936, 9150000, 0, 26000, SLIDE_CY, "F2F6F7", geometry="rect")
    )
    return (
        grid
        + _rect(937, 620000, 545000, 820000, 110000, accent, geometry="rect")
        + _rect(938, 11100000, 0, 280000, SLIDE_CY, "F2F7F9", geometry="rect")
        + _rect(939, 11380000, 0, 140000, SLIDE_CY, accent, geometry="rect")
        + _textbox(940, 11170000, 6200000, 700000, 220000, f"{index:02d}", 950, "78909C", bold=True)
    )


def _slide_body(
    index: int,
    layout: str,
    title: str,
    subtitle: str,
    bullets: list[str],
    metrics: list[dict[str, str]],
    accent: str,
) -> str:
    if layout == "hero":
        metric_row = _metric_row(30, 960000, 4050000, metrics, accent)
        return (
            _textbox(2, 860000, 1250000, 10200000, 1250000, title, 4200, "0A3945", bold=True)
            + (_textbox(3, 900000, 2600000, 9000000, 650000, subtitle, 2300, "516071") if subtitle else "")
            + _bullet_box(4, 980000, 3300000, 9000000, 700000, bullets[:2], 2100)
            + metric_row
        )

    if layout == "metrics":
        return (
            _textbox(2, 760000, 820000, 10000000, 850000, title, 3400, "0A3945", bold=True)
            + (_textbox(3, 800000, 1620000, 9500000, 500000, subtitle, 1800, "516071") if subtitle else "")
            + _metric_row(40, 900000, 2350000, metrics or _bullets_as_metrics(bullets), accent)
            + _bullet_box(5, 1100000, 5100000, 9300000, 750000, bullets[:2], 1700)
        )

    if layout == "timeline":
        return (
            _textbox(2, 760000, 840000, 10000000, 850000, title, 3400, "0A3945", bold=True)
            + (_textbox(3, 800000, 1580000, 9300000, 500000, subtitle, 1800, "516071") if subtitle else "")
            + _timeline(50, 980000, 2750000, bullets[:3], accent)
        )

    if layout == "cards":
        return (
            _textbox(2, 760000, 840000, 10000000, 850000, title, 3400, "0A3945", bold=True)
            + (_textbox(3, 800000, 1580000, 9300000, 500000, subtitle, 1800, "516071") if subtitle else "")
            + _cards(60, 920000, 2450000, bullets[:3], accent)
        )

    if layout == "closing":
        return (
            _textbox(2, 1000000, 1500000, 9800000, 1000000, title, 3800, "0A3945", bold=True)
            + _bullet_box(4, 1450000, 2750000, 9000000, 2350000, bullets[:5], 2000)
            + _rect(8, 3600000, 5250000, 4900000, 160000, accent)
        )

    return (
        _textbox(2, 760000, 840000, 10000000, 850000, title, 3400, "0A3945", bold=True)
        + (_textbox(3, 800000, 1600000, 5000000, 500000, subtitle, 1800, "516071") if subtitle else "")
        + _bullet_box(4, 850000, 2350000, 5200000, 3200000, bullets, 2000)
        + _side_panel(20, 7000000, 2200000, metrics or _bullets_as_metrics(bullets[:2]), accent)
    )


def _bullet_box(shape_id: int, x: int, y: int, cx: int, cy: int, bullets: list[str], font_size: int) -> str:
    bullet_text = "".join(_paragraph(item, font_size, "263238", bullet=True) for item in bullets)
    return f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Bullets"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm></p:spPr>
  <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{bullet_text}</p:txBody>
</p:sp>"""


def _bullets_as_metrics(bullets: list[str]) -> list[dict[str, str]]:
    return [{"label": f"Point {index}", "value": bullet} for index, bullet in enumerate(bullets[:3], start=1)]


def _metric_row(shape_id: int, x: int, y: int, metrics: list[dict[str, str]], accent: str) -> str:
    if not metrics:
        return ""
    width = 3150000
    gap = 280000
    return "".join(
        _metric_card(shape_id + index * 3, x + index * (width + gap), y, width, 1120000, metric, accent)
        for index, metric in enumerate(metrics[:3])
    )


def _side_panel(shape_id: int, x: int, y: int, metrics: list[dict[str, str]], accent: str) -> str:
    panel = _rect(shape_id, x, y, 3600000, 3100000, "EAF5F7", line_color=accent)
    content = ""
    for index, metric in enumerate(metrics[:3]):
        content += _textbox(shape_id + 1 + index, x + 240000, y + 320000 + index * 820000, 3100000, 620000, f"{metric.get('value', '')}", 1900, "0A3945", bold=index == 0)
    return panel + content


def _metric_card(shape_id: int, x: int, y: int, cx: int, cy: int, metric: Mapping[str, str], accent: str) -> str:
    return (
        _rect(shape_id, x, y, cx, cy, "FFFFFF", line_color=accent)
        + _textbox(shape_id + 1, x + 180000, y + 180000, cx - 360000, 380000, metric.get("value", ""), 2200, "0A3945", bold=True)
        + _textbox(shape_id + 2, x + 180000, y + 620000, cx - 360000, 300000, metric.get("label", ""), 1200, "516071")
    )


def _timeline(shape_id: int, x: int, y: int, bullets: list[str], accent: str) -> str:
    content = ""
    if len(bullets) > 3:
        for index, bullet in enumerate(bullets[:4]):
            node_x = x + (index % 2) * 5050000
            node_y = y + (index // 2) * 1450000
            content += _rect(shape_id + index * 3, node_x, node_y, 4600000, 1200000, "FFFFFF", line_color=accent)
            content += _textbox(shape_id + index * 3 + 1, node_x + 220000, node_y + 130000, 4100000, 280000, f"Milestone {index + 1}", 1350, accent, bold=True)
            content += _textbox(shape_id + index * 3 + 2, node_x + 220000, node_y + 500000, 4100000, 520000, bullet, 1450, "263238")
        return content
    for index, bullet in enumerate(bullets[:3]):
        node_x = x + index * 3400000
        content += _rect(shape_id + index * 3, node_x, y, 2850000, 1650000, "FFFFFF", line_color=accent)
        content += _textbox(shape_id + index * 3 + 1, node_x + 220000, y + 170000, 2400000, 340000, f"Step {index + 1}", 1500, accent, bold=True)
        content += _textbox(shape_id + index * 3 + 2, node_x + 220000, y + 620000, 2400000, 760000, bullet, 1700, "263238")
    return content


def _cards(shape_id: int, x: int, y: int, bullets: list[str], accent: str) -> str:
    content = ""
    if len(bullets) > 3:
        for index, bullet in enumerate(bullets[:4]):
            card_x = x + (index % 2) * 5050000
            card_y = y + (index // 2) * 1450000
            content += _rect(shape_id + index * 3, card_x, card_y, 4700000, 1200000, "FFFFFF", line_color="D9E4E8")
            content += _rect(shape_id + index * 3 + 1, card_x, card_y, 4700000, 140000, accent)
            content += _textbox(shape_id + index * 3 + 2, card_x + 220000, card_y + 350000, 4200000, 600000, bullet, 1500, "263238")
        return content
    for index, bullet in enumerate(bullets[:3]):
        card_x = x + index * 3400000
        content += _rect(shape_id + index * 3, card_x, y, 3000000, 2300000, "FFFFFF", line_color="D9E4E8")
        content += _rect(shape_id + index * 3 + 1, card_x, y, 3000000, 180000, accent)
        content += _textbox(shape_id + index * 3 + 2, card_x + 260000, y + 500000, 2480000, 1200000, bullet, 1900, "263238")
    return content


def _paragraph(text: str, font_size: int, color: str, bullet: bool = False) -> str:
    bullet_xml = '<a:buChar char="•"/>' if bullet else "<a:buNone/>"
    return f"""<a:p><a:pPr marL="{360000 if bullet else 0}" indent="{ -180000 if bullet else 0}">{bullet_xml}</a:pPr><a:r><a:rPr lang="en-US" sz="{font_size}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{text}</a:t></a:r><a:endParaRPr lang="en-US" sz="{font_size}"/></a:p>"""


def _rect(
    shape_id: int,
    x: int,
    y: int,
    cx: int,
    cy: int,
    fill_color: str,
    line_color: str | None = None,
    geometry: str = "roundRect",
) -> str:
    line_xml = (
        f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line_color}"/></a:solidFill></a:ln>'
        if line_color
        else "<a:ln><a:noFill/></a:ln>"
    )
    return f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Shape {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="{geometry}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill_color}"/></a:solidFill>{line_xml}</p:spPr>
</p:sp>"""


def _textbox(shape_id: int, x: int, y: int, cx: int, cy: int, text: str, font_size: int, color: str, bold: bool = False) -> str:
    bold_attr = ' b="1"' if bold else ""
    return f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Text {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm></p:spPr>
  <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="{font_size}"{bold_attr}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{text}</a:t></a:r></a:p></p:txBody>
</p:sp>"""


def _accent_bar(index: int, color: str | None = None) -> str:
    colors = ["0087A5", "494BD6", "00A676", "E09F3E"]
    color = color or colors[(index - 1) % len(colors)]
    return f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="10" name="Accent"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="230000" cy="{SLIDE_CY}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>
</p:sp>"""


def _footer(index: int, template: str = "classic_left_rail") -> str:
    if template == "executive_header":
        return _textbox(11, 9300000, 6360000, 2300000, 250000, f"Grantly Deck / {index}", 1050, "607D8B")
    if template == "corner_focus":
        return _textbox(11, 9400000, 6360000, 2100000, 250000, f"Grantly / {index}", 1050, "78909C")
    if template == "ledger_grid":
        return _textbox(11, 9200000, 6360000, 1700000, 250000, f"Grantly / {index}", 1050, "78909C")
    return _textbox(11, 9600000, 6350000, 2000000, 260000, f"Grantly / {index}", 1100, "78909C")


def _paragraph(text: str, font_size: int, color: str, bullet: bool = False) -> str:
    bullet_xml = '<a:buChar char="&#8226;"/>' if bullet else "<a:buNone/>"
    return f"""<a:p><a:pPr marL="{360000 if bullet else 0}" indent="{ -180000 if bullet else 0}">{bullet_xml}</a:pPr><a:r><a:rPr lang="en-US" sz="{font_size}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{text}</a:t></a:r><a:endParaRPr lang="en-US" sz="{font_size}"/></a:p>"""


def _theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Grantly">
  <a:themeElements>
    <a:clrScheme name="Grantly"><a:dk1><a:srgbClr val="0A3945"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="263238"/></a:dk2><a:lt2><a:srgbClr val="F8FBFC"/></a:lt2><a:accent1><a:srgbClr val="0087A5"/></a:accent1><a:accent2><a:srgbClr val="494BD6"/></a:accent2><a:accent3><a:srgbClr val="00A676"/></a:accent3><a:accent4><a:srgbClr val="E09F3E"/></a:accent4><a:accent5><a:srgbClr val="516071"/></a:accent5><a:accent6><a:srgbClr val="B0BEC5"/></a:accent6><a:hlink><a:srgbClr val="0087A5"/></a:hlink><a:folHlink><a:srgbClr val="494BD6"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="Grantly"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Grantly"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def _slide_master_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def _slide_master_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def _slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def _slide_layout_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""
