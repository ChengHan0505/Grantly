"""Drafter agent (Track B): parallelized divide-and-conquer drafting.

This module splits drafting into focused calls:
  1) proposal writer
  2) deck generator
  3) presentation script writer

If the SME uploaded an existing deck, we switch to critique mode instead.
"""

from __future__ import annotations

import asyncio
import json

try:
    from .glm_client import GLMClient
    from .schemas import (
        DeckCritique,
        DeckOutput,
        DrafterOutput,
        GrantRequirement,
        ProposalOutput,
        SMEProfile,
        ScriptOutput,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from glm_client import GLMClient
    from schemas import (
        DeckCritique,
        DeckOutput,
        DrafterOutput,
        GrantRequirement,
        ProposalOutput,
        SMEProfile,
        ScriptOutput,
    )


def _make_user_prompt(sme: SMEProfile, grant: GrantRequirement, extra_context: str | None = None) -> str:
    prompt = (
        f"SME Profile:\n{sme.model_dump_json(indent=2)}\n\n"
        f"Grant Requirements:\n{grant.model_dump_json(indent=2)}"
    )
    if extra_context:
        prompt += f"\n\nAdditional Context:\n{extra_context}"
    return prompt


DRAFTER_STRATEGY_PROMPT = """
Persona:
You are an elite, highly paid grant writer and business strategist specializing
in Malaysian SME funding (e.g., MDEC, Cradle Fund). Your sole objective is to
transform raw, messy SME data into a premium, persuasive, and highly
professional Business Proposal.

Tone & Style:
Use a confident, enterprise-grade, and formal corporate tone. Avoid fluff,
buzzwords, or overly enthusiastic marketing speak. Use strong, active verbs.
The writing must sound like it was drafted by a top-tier management consultant.

Missing Data Handling (CRITICAL):
The raw data may contain fields that say "not specified", "null",
"To be confirmed", "TBC", or "0". DO NOT EVER print these phrases in your
output. If a specific metric, date, or name is missing, gracefully write around
it. Speak to the general capability, strategic intent, or market opportunity
without drawing attention to the missing detail.

Narrative Framing:
- Frame the SME as highly fundable, operationally mature, and ready to execute.
- Frame the Problem as a critical market gap or a scalable operational bottleneck.
- Frame the Solution as an innovative, sustainable, and high-ROI intervention.
- Describe the Budget/Use of Funds as a strategic investment in capability and
  compliance, even if the exact financial breakdown is sparse.

Evidence Discipline:
Do not invent customers, certifications, revenue, partners, awards, approvals,
or signed documents. If evidence is missing, write around it using strategic
intent and operational readiness rather than exposing the missing field.
""".strip()


async def draft_proposal(sme: SMEProfile, grant: GrantRequirement) -> ProposalOutput:
    """Generate a focused business proposal."""
    schema = json.dumps(ProposalOutput.model_json_schema(), indent=2)
    system_prompt = f"""{DRAFTER_STRATEGY_PROMPT}

Task:
Write a board-ready Malaysian SME grant proposal in polished Markdown. Use
structured sections with headings, not a casual note. Every paragraph must
strengthen the case that the SME can responsibly deploy grant funding and
deliver measurable outcomes.

Must include:
- I. Executive Summary
- II. Company Description
- III. Products & Services
- IV. Marketing Plan
  - Include target market research
  - Include a Competitor Data Collection Plan
  - Include a SWOT Analysis
- V. Operational Plan
- VI. Management & Organization
- VII. Startup Expenses & Capitalization
- VIII. Conclusion

Quality Bar:
- Prefer precise, polished, grant-panel language over generic startup language.
- Write in complete paragraphs with management-consulting polish, not short generic fragments.
- Use available numbers naturally, but never expose missing placeholders.
- Avoid raw database phrasing and never output "not specified", "null",
  "To be confirmed", "TBC", or "0" as a missing-value substitute.
- Target length: 1800-2400 words.
- Each major section should contain enough detail to be useful in a real grant submission.
- The proposal must feel premium, information-rich, commercially serious, and audit-ready.
- The Marketing Plan must be especially substantive: describe the target market,
  how competitor data should be collected, and provide a clear SWOT analysis.
- The Startup Expenses & Capitalization section must explain the funding ask,
  project cost, use of funds, and how grant support strengthens delivery capacity.

Output strict JSON only matching this schema:
{schema}
"""
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=_make_user_prompt(sme, grant),
        temperature=0.5,
    )
    return ProposalOutput(**result)


async def draft_deck(sme: SMEProfile, grant: GrantRequirement) -> DeckOutput:
    """Generate an evidence-rich grant pitch deck."""
    schema = json.dumps(DeckOutput.model_json_schema(), indent=2)
    system_prompt = f"""{DRAFTER_STRATEGY_PROMPT}

You are now converting the business proposal narrative into a premium
grant-panel pitch deck.

Generate exactly 8 slides total. The deck should be as useful and information-rich
as a formal proposal, but still formatted for slides.

Requirements:
- Use 4-5 substantive bullet points per slide, each specific enough for a grant panel.
- Include concrete figures from the SME/grant data whenever available: funding ask,
  project cost, grant cap, team size, company age, ownership, outsourcing cost,
  end-user partner status, deadline, and required documents.
- Do not invent traction, revenue, partners, or certifications.
- If a value is missing, omit that detail or write around it. Never print raw
  placeholders such as "not specified", "null", "To be confirmed", "TBC", or "0".
- Add metrics on slides where they strengthen the decision case.
- Add a one-sentence grant_alignment field for every slide.
- Add speaker_notes that explain how the presenter should narrate the slide.

Recommended sequence:
1. Company and grant ask
2. Company snapshot and eligibility signals
3. Problem, market need, and why now
4. Solution and differentiation
5. Grant alignment and supporting documents
6. Use of funds and budget governance
7. Implementation timeline, KPIs, and risk controls
8. Outcomes, economic value, and closing request

Output strict JSON only matching this schema:
{schema}
"""
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=_make_user_prompt(sme, grant),
        temperature=0.5,
    )
    return DeckOutput(**result)


async def draft_script(sme: SMEProfile, grant: GrantRequirement, deck: DeckOutput | None = None) -> ScriptOutput:
    """Generate a practical presentation script."""
    schema = json.dumps(ScriptOutput.model_json_schema(), indent=2)
    deck_context = (
        "Use this generated slide sequence as the source of truth for the script:\n"
        f"{deck.model_dump_json(indent=2)}"
        if deck
        else None
    )
    system_prompt = f"""{DRAFTER_STRATEGY_PROMPT}

You are now writing the founder's grant-panel presentation script as an elite
demo-day speaking coach and grant storyteller.

Write a practical presenter script that follows the generated pitch deck
slide-by-slide. It should help the founder present, not merely repeat bullets.

Requirements:
- Target a 6-8 minute grant-panel presentation.
- Include an opening, one section per slide, transitions between slides, and a closing ask.
- For each slide, expand the bullets into a spoken talk track with specific figures
  and grant alignment from the SME/grant context.
- Include delivery cues for what to emphasize and what evidence/document the presenter
  should be ready to show.
- End with 4 likely panel questions and concise suggested answers.
- Keep the tone professional, confident, factual, and submission-ready.
- Never say "not specified", "null", "To be confirmed", "TBC", or "0" when
  information is missing. Speak around missing data gracefully.

Output strict JSON only matching this schema:
{schema}
"""
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=_make_user_prompt(sme, grant, deck_context),
        temperature=0.5,
    )
    return ScriptOutput(**result)


async def evaluate_deck(sme: SMEProfile, grant: GrantRequirement) -> DeckCritique:
    """Critique an uploaded pitch deck when present."""
    schema = json.dumps(DeckCritique.model_json_schema(), indent=2)
    system_prompt = f"""{DRAFTER_STRATEGY_PROMPT}

You are now acting as an investor and Malaysian grant-review panelist.

Given the SME and grant context plus uploaded deck text, provide a rigorous
critique with practical improvements.

If the uploaded deck or SME data contains missing-value placeholders, do not
repeat them. Identify the strategic gap in professional language instead.

Output strict JSON only matching this schema:
{schema}
"""
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=_make_user_prompt(sme, grant),
        temperature=0.5,
    )
    return DeckCritique(**result)


async def run_drafter(
    sme_data: SMEProfile,
    grant_data: GrantRequirement,
) -> DrafterOutput:
    """Orchestrate parallel drafting or critique mode."""
    if sme_data.uploaded_pitch_deck_text and sme_data.uploaded_pitch_deck_text.strip():
        critique = await evaluate_deck(sme_data, grant_data)
        return DrafterOutput(
            proposal=None,
            deck=None,
            script=None,
            deck_critique=critique,
        )

    proposal = await draft_proposal(sme_data, grant_data)
    deck = await draft_deck(sme_data, grant_data)
    script = await draft_script(sme_data, grant_data, deck)
    return DrafterOutput(
        proposal=proposal,
        deck=deck,
        script=script,
        deck_critique=None,
    )


async def _main() -> None:
    sme = SMEProfile(
        company_name="TechBina Sdn Bhd",
        ssm_number="1234567-V",
        age_in_months=24,
        full_time_employees=5,
        ownership_majority="Local",
        sector="ICT",
        total_project_cost_rm=500000,
        requested_funding_rm=250000,
        outsourced_cost_rm=20000,
        has_end_user_partner=True,
        documents_provided=[
            "SSM Certificate",
            "Pitch Deck",
            "Audited Financials",
            "BOD Resolution",
            "Integrity Declaration",
        ],
        uploaded_pitch_deck_text=None,
    )

    grant = GrantRequirement(
        grant_name="MDEC MDCG",
        promoted_sectors=["ICT", "Medical Devices"],
        max_funding_rm=1000000,
        funding_tier_local_percent=50,
        funding_tier_foreign_percent=30,
        max_outsourcing_percent=20,
        requires_end_user_partner=True,
        mandatory_documents=[
            "Pitch Deck",
            "Audited Financials",
            "BOD Resolution",
            "Integrity Declaration",
        ],
        application_roadmap=[],
    )

    result = await run_drafter(sme, grant)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
