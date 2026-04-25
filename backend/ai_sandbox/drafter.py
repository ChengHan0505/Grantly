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


async def draft_proposal(sme: SMEProfile, grant: GrantRequirement) -> ProposalOutput:
    """Generate a focused business proposal."""
    schema = json.dumps(ProposalOutput.model_json_schema(), indent=2)
    system_prompt = f"""You are an elite startup fundraiser and grant writer in Malaysia.

Write a board-ready grant proposal in polished Markdown.
Use 8 concise sections with headings, not a casual note. Keep the tone formal,
specific, numerical, and suitable for submission to a Malaysian grant agency.

Must include:
- Executive summary
- Problem and market opportunity
- Product/service differentiation
- Traction and validation
- Team and governance
- Detailed use-of-funds table or bullet plan aligned to grant outcomes
- Risk management and mitigation
- KPI and implementation timeline
- Clear closing argument for award decision

Target length: 700-1100 words. Avoid filler, hype, and unsupported claims.

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
    system_prompt = f"""You are a top-tier startup pitch strategist for Malaysian grants.

Generate exactly 8 slides total. The deck should be as useful and information-rich
as a formal proposal, but still formatted for slides.

Requirements:
- Use 4-5 substantive bullet points per slide, each specific enough for a grant panel.
- Include concrete figures from the SME/grant data whenever available: funding ask,
  project cost, grant cap, team size, company age, ownership, outsourcing cost,
  end-user partner status, deadline, and required documents.
- Do not invent traction, revenue, partners, or certifications. If a value is not
  available, state the review point as "to be validated" or "to be confirmed".
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
    system_prompt = f"""You are an elite demo-day speaking coach and grant storyteller.

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
    system_prompt = f"""You are an investor and grant-review panelist in Malaysia.

Given the SME and grant context plus uploaded deck text, provide a rigorous
critique with practical improvements.

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
