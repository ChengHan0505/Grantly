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


def _make_user_prompt(sme: SMEProfile, grant: GrantRequirement) -> str:
    return (
        f"SME Profile:\n{sme.model_dump_json(indent=2)}\n\n"
        f"Grant Requirements:\n{grant.model_dump_json(indent=2)}"
    )


async def draft_proposal(sme: SMEProfile, grant: GrantRequirement) -> ProposalOutput:
    """Generate a focused business proposal."""
    schema = json.dumps(ProposalOutput.model_json_schema(), indent=2)
    system_prompt = f"""You are an elite startup fundraiser and grant writer in Malaysia.

Write a maximum of 2 short paragraphs for the business proposal.
Keep it concrete, numerical, and persuasive for the target grant.

Must include:
- Executive summary
- Problem and market opportunity
- Product/service differentiation
- Traction and validation
- Team and governance
- Detailed use-of-funds plan aligned to grant outcomes
- Risk management and mitigation
- KPI and implementation timeline
- Clear closing argument for award decision

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
    """Generate a concise 5-slide grant pitch deck."""
    schema = json.dumps(DeckOutput.model_json_schema(), indent=2)
    system_prompt = f"""You are a top-tier startup pitch strategist for Malaysian grants.

Generate exactly 3 slides total. Keep bullet points very brief.
Each slide should still include concrete metrics and grant alignment.

Recommended sequence:
1. Vision + Problem + Solution
2. Traction + Team
3. Grant Ask + Outcomes

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


async def draft_script(sme: SMEProfile, grant: GrantRequirement) -> ScriptOutput:
    """Generate a tight 3-minute presentation script."""
    schema = json.dumps(ScriptOutput.model_json_schema(), indent=2)
    system_prompt = f"""You are an elite demo-day speaking coach and grant storyteller.

Write a maximum of 2 paragraphs for the presentation script.
Keep the tone professional, persuasive, and outcome-driven.

Output strict JSON only matching this schema:
{schema}
"""
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=_make_user_prompt(sme, grant),
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
    script = await draft_script(sme_data, grant_data)
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
