"""Drafter agent (Track B): generate the final submission package.

Given a 100%-ready SMEProfile and a GrantRequirement, this produces:
  - a persuasive business proposal (Markdown),
  - a pitch-day presentation script (Markdown), and
  - EITHER a freshly generated 6-8 slide deck, OR a critique of the
    founder's uploaded deck text -- not both.

The branch is chosen by inspecting ``sme_data.uploaded_pitch_deck_text``.
"""

from __future__ import annotations

import asyncio
import json

from glm_client import GLMClient
from schemas import DrafterOutput, GrantRequirement, SMEProfile


DRAFTER_SYSTEM_PROMPT_TEMPLATE = """You are an elite startup fundraiser and grant writer in Malaysia.

The user has a 100% readiness score. You must generate a concise, 1-paragraph
Executive Summary Business Proposal and a brief, high-level Presentation
Script tailored to the grant's outcomes, tone, and evaluation criteria
(reference the grant_name, promoted_sectors, and funding tiers in the copy).

Style:
  - Write in clear, confident, investor-grade English.
  - Lean on concrete numbers from the SME Profile (funding ask,
    outsourcing ratio, employee count, months in operation).
  - No fluff, no filler. Every sentence should either sell the
    opportunity or de-risk it.
  - Keep it short. Prioritise signal over length.

BRANCHING LOGIC (read carefully):
  - If SME Profile's "uploaded_pitch_deck_text" is a non-empty string,
    act as an investor reviewing their deck. Populate "deck_critique"
    with strengths, weaknesses, and action_items_to_improve grounded
    in the text they provided. Leave "generated_deck" as null.
  - If "uploaded_pitch_deck_text" is null, missing, or an empty
    string, act as a creator. Populate "generated_deck" with a
    short, 3-slide presentation tailored to this grant (typical flow:
    Problem + Solution, Traction + Team, Ask + Use of Funds).
    Leave "deck_critique" as null.

You MUST populate EXACTLY ONE of {{generated_deck, deck_critique}} and leave
the other as null. Never populate both. Never leave both null.

Output: return strict JSON matching this schema exactly. No Markdown
fences around the JSON, no prose outside it. Markdown inside the string
fields (business_proposal_markdown, presentation_script_markdown) is
expected and encouraged.

{schema}
"""


async def run_drafter(
    sme_data: SMEProfile,
    grant_data: GrantRequirement,
) -> DrafterOutput:
    """Generate the grant submission package for a fully-ready SME."""

    schema_json = json.dumps(DrafterOutput.model_json_schema(), indent=2)
    system_prompt = DRAFTER_SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)

    user_prompt = (
        f"SME Profile:\n{sme_data.model_dump_json(indent=2)}\n\n"
        f"Grant Requirements:\n{grant_data.model_dump_json(indent=2)}"
    )

    client = GLMClient()
    result_dict = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.5,
    )

    return DrafterOutput(**result_dict)


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
