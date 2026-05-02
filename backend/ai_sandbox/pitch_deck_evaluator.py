"""Pitch Deck Evaluator agent: analyze and critique an uploaded pitch deck document.

Evaluates the quality and completeness of user-uploaded pitch decks against
best practices for Malaysian grant applications. Provides constructive feedback
on strengths, weaknesses, and actionable improvements.
"""

from __future__ import annotations

import json
import re

try:
    from .glm_client import GLMClient
    from .schemas import DeckCritique
except ImportError:  # pragma: no cover - supports direct script execution
    from glm_client import GLMClient
    from schemas import DeckCritique


PITCH_DECK_EVALUATOR_SYSTEM_PROMPT_TEMPLATE = """You are an expert pitch deck evaluator for Malaysian SME grant applications.

Your role is to analyze uploaded pitch decks and provide constructive, actionable feedback
that helps SMEs improve their materials for grant applications.

When analyzing a pitch deck, evaluate against these criteria:
1. **Clarity of Value Proposition** - Is the business idea and problem being solved clearly stated?
2. **Grant Alignment** - Does the pitch demonstrate understanding of the grant's objectives?
3. **Financial Soundness** - Are funding figures, use of funds, and ROI clearly articulated?
4. **Team Credibility** - Is the team's experience and capability evident?
5. **Market Understanding** - Does the deck show awareness of market size, competition, and opportunity?
6. **Visual Communication** - Is the deck professionally formatted and easy to follow?
7. **Call to Action** - Is there a clear ask and next steps?
8. **Risk Acknowledgment** - Are potential risks and mitigation strategies discussed?

Provide your feedback in JSON format with these sections:
- overall_score: integer from 0 to 100 based on grant-readiness of the deck
- review_summary: a concise 2-3 sentence constructive review
- strengths: List 3-5 key strengths of the pitch deck
- weaknesses: List 3-5 areas for improvement (be specific and constructive)
- action_items_to_improve: List 3-5 specific, actionable steps to strengthen the deck

Focus on practical, implementable improvements. For Malaysian context, consider:
- References to government agencies (MDEC, MIDA, MGTC, MOLF, etc.) where relevant
- Alignment with Malaysia's tech and innovation priorities
- Local market dynamics and competitive landscape
- References to grant criteria if mentioned in the context

Tone: Professional, encouraging, and constructive. Frame weaknesses as growth opportunities, not failures.

Output: return strict JSON matching this schema exactly. No Markdown fences, no prose outside the JSON.

{schema}
"""


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _fallback_pitch_deck_critique(
    deck_text: str,
    grant_context: dict | None = None,
    sme_context: dict | None = None,
    reason: str | None = None,
) -> DeckCritique:
    lower = deck_text.lower()
    score = 45
    strengths: list[str] = []
    weaknesses: list[str] = []
    actions: list[str] = []

    if _contains_any(lower, ("problem", "pain point", "challenge")) and _contains_any(lower, ("solution", "platform", "product")):
        score += 12
        strengths.append("The deck appears to connect a business problem with a proposed solution.")
    else:
        weaknesses.append("The problem and solution are not yet clearly separated for a grant reviewer.")
        actions.append("Add one early slide that states the problem, the target customer, and the proposed solution in plain language.")

    if _contains_any(lower, ("rm ", "fund", "grant", "budget", "use of funds", "cost")):
        score += 12
        strengths.append("The deck includes funding or budget language that can be mapped to grant assessment criteria.")
    else:
        weaknesses.append("The funding ask and use of funds are not explicit enough for grant assessment.")
        actions.append("Add a use-of-funds slide with requested amount, total project cost, eligible cost categories, and expected outcomes.")

    if _contains_any(lower, ("market", "customer", "traction", "revenue", "pilot", "users")):
        score += 10
        strengths.append("The deck gives some evidence of market understanding or commercial validation.")
    else:
        weaknesses.append("Market evidence, customer validation, or traction is thin.")
        actions.append("Add evidence such as market size, customer pilots, revenue, letters of intent, or early user metrics.")

    if _contains_any(lower, ("team", "founder", "ceo", "cto", "experience")):
        score += 8
        strengths.append("The deck references team capability, which helps establish delivery confidence.")
    else:
        weaknesses.append("The team delivery capability is not visible enough.")
        actions.append("Add a team slide with roles, relevant experience, and ownership of project delivery milestones.")

    if grant_context and any(str(value).lower() in lower for value in grant_context.values() if value):
        score += 8
        strengths.append("The deck references grant context, improving alignment with the target opportunity.")
    else:
        grant_name = (grant_context or {}).get("grant_name") or (grant_context or {}).get("title") or "the target grant"
        weaknesses.append(f"The deck should make its alignment to {grant_name} more explicit.")
        actions.append("Add a grant-alignment slide that maps eligibility, project scope, outcomes, and documents to the published criteria.")

    if not strengths:
        strengths.append("The uploaded deck gives Grantly a concrete base to improve instead of starting from a blank page.")
    while len(strengths) < 3:
        strengths.append("The deck can be strengthened into a grant-ready narrative with clearer evidence and structure.")
    while len(weaknesses) < 3:
        weaknesses.append("Some claims would benefit from more specific numbers, evidence, or implementation detail.")
    while len(actions) < 3:
        actions.append("Tighten each slide title into a reviewer-facing claim and support it with one measurable proof point.")

    company = (sme_context or {}).get("company_name") or "the applicant"
    fallback_note = f" Deterministic fallback was used because the AI evaluator was unavailable: {reason}" if reason else ""
    return DeckCritique(
        overall_score=_clamp_score(score),
        review_summary=(
            f"{company}'s uploaded pitch deck is reviewable and can become stronger with clearer grant alignment, "
            f"funding detail, and evidence of execution readiness.{fallback_note}"
        ),
        strengths=strengths[:5],
        weaknesses=weaknesses[:5],
        action_items_to_improve=actions[:5],
    )


def _normalize_critique(payload: dict, fallback: DeckCritique) -> DeckCritique:
    def _list(key: str, default: list[str]) -> list[str]:
        value = payload.get(key)
        if not isinstance(value, list):
            return default
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return cleaned or default

    score = payload.get("overall_score")
    try:
        score_value = _clamp_score(int(float(score))) if score is not None else fallback.overall_score
    except (TypeError, ValueError):
        score_value = fallback.overall_score

    summary = payload.get("review_summary")
    if not isinstance(summary, str) or not summary.strip():
        summary = fallback.review_summary

    return DeckCritique(
        overall_score=score_value,
        review_summary=summary,
        strengths=_list("strengths", fallback.strengths),
        weaknesses=_list("weaknesses", fallback.weaknesses),
        action_items_to_improve=_list("action_items_to_improve", fallback.action_items_to_improve),
    )


async def run_pitch_deck_evaluator(
    deck_text: str,
    grant_context: dict | None = None,
    sme_context: dict | None = None,
) -> DeckCritique:
    """Evaluate an uploaded pitch deck and return constructive feedback."""

    deck_text = re.sub(r"\s+", " ", deck_text).strip()
    fallback = _fallback_pitch_deck_critique(deck_text, grant_context, sme_context)
    if len(deck_text) < 80:
        return fallback

    schema_json = json.dumps(DeckCritique.model_json_schema(), indent=2)
    system_prompt = PITCH_DECK_EVALUATOR_SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)

    # Build a contextual user prompt
    context_parts = ["Pitch Deck Content:\n" + deck_text]
    
    if grant_context:
        context_parts.append(f"\nGrant Context:\n{json.dumps(grant_context, indent=2)}")
    
    if sme_context:
        context_parts.append(f"\nSME Context:\n{json.dumps(sme_context, indent=2)}")

    user_prompt = "\n".join(context_parts)

    try:
        client = GLMClient()
        result_dict = await client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
        )
        return _normalize_critique(result_dict, fallback)
    except Exception as exc:  # noqa: BLE001
        return _fallback_pitch_deck_critique(deck_text, grant_context, sme_context, reason=str(exc)[:180])


async def _main() -> None:
    sample_deck_text = """
    TECHBINA: Revolutionizing Malaysian E-Commerce with AI
    
    Slide 1: The Problem
    - SME sellers struggle with inventory management
    - Manual processes lead to stockouts and overstock
    - Waste costs businesses up to 15% of revenue
    
    Slide 2: Our Solution
    - AI-powered inventory prediction system
    - Real-time demand forecasting
    - Automated reordering
    
    Slide 3: Market Opportunity
    - 5 million SMEs in Malaysia
    - RM 500B annual e-commerce market
    - 45% CAGR growth projected
    
    Slide 4: Business Model
    - SaaS subscription: RM 500-2000/month
    - 5% take-rate on managed inventory
    
    Slide 5: Traction
    - Beta testing with 10 sellers
    - 30% inventory cost reduction achieved
    
    Slide 6: Team
    - CEO: 8 years e-commerce experience
    - CTO: Former MDEC tech innovation lead
    - Operations: Previously at major logistics company
    
    Slide 7: Financials
    - Seeking RM 500,000 grant
    - Using for: Product development (40%), Hiring (35%), Marketing (25%)
    - Projected breakeven: Month 18
    
    Slide 8: Ask
    - RM 500,000 non-dilutive funding
    - Partnership with MyDIGITAL initiative
    """

    sample_grant_context = {
        "grant_name": "MDEC Digital Innovation Fund",
        "provider": "Malaysian Digital Economy Corporation",
        "focus_areas": ["AI/ML", "E-commerce", "Digital Transformation"],
        "max_funding": "RM 1,000,000",
    }

    sample_sme_context = {
        "company_name": "TechBina Sdn Bhd",
        "sector": "ICT / E-commerce",
        "employees": 5,
        "age_months": 18,
    }

    result = await run_pitch_deck_evaluator(
        sample_deck_text,
        grant_context=sample_grant_context,
        sme_context=sample_sme_context,
    )
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(_main())
