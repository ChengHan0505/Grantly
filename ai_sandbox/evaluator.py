"""Evaluator agent: audit an ``SMEProfile`` against a ``GrantRequirement``.

Produces an ``EvaluatorOutput`` with one ``EvidenceTrace`` per requirement
plus an overall ``readiness_score``. The LLM is given explicit logical
rules for funding caps, outsourcing limits, and mandatory-document
cross-referencing so the audit is deterministic and auditable.
"""

from __future__ import annotations

import asyncio
import json

from glm_client import GLMClient
from schemas import EvaluatorOutput, GrantRequirement, SMEProfile


EVALUATOR_SYSTEM_PROMPT_TEMPLATE = """You are an expert Malaysian Grant Auditor for the Malaysia SME Grant Copilot.

Compare the SME Profile against the Grant Requirements. For each requirement
below, determine if the SME is "MET", "UNMET", or "UNKNOWN", and cite the
specific source_document (e.g. "SME Profile.requested_funding_rm" or a name
from documents_provided) that you used to decide.

Requirements to evaluate (produce one EvidenceTrace per item):
  1. Sector eligibility — SME.sector must be in Grant.promoted_sectors.
  2. Funding cap — see Rule 1.
  3. Outsourcing limit — see Rule 2.
  4. End-user partner — if Grant.requires_end_user_partner is true, then
     SME.has_end_user_partner must be true.
  5. Mandatory documents — see Rule 3. Produce ONE EvidenceTrace per
     entry in Grant.mandatory_documents.

Logical constraints (apply strictly):
  Rule 1: If SME.ownership_majority is "Local", max allowed funding is
    Grant.funding_tier_local_percent / 100 * SME.total_project_cost_rm.
    If "Foreign", use Grant.funding_tier_foreign_percent instead.
    Additionally, funding must not exceed Grant.max_funding_rm.
    If SME.requested_funding_rm exceeds either limit, the requirement is UNMET.
  Rule 2: SME.outsourced_cost_rm must not exceed
    Grant.max_outsourcing_percent / 100 * SME.requested_funding_rm.
    If it does, the requirement is UNMET.
  Rule 3: Cross-reference Grant.mandatory_documents against
    SME.documents_provided (case-insensitive, allow reasonable synonyms).
    If a mandatory document is missing from documents_provided, that specific
    document requirement is UNMET.

Scoring:
  Calculate the readiness_score (0 to 100) using a weighted system:
    - Financial & Rule Criteria (50 points total): Give proportional points
      for Sector, Funding Cap, Outsourcing Limit, and End-User Partner being MET.
    - Document Criteria (50 points total): Give proportional points based on
      the percentage of mandatory_documents that are MET.
    - Add both components, then round to the nearest integer.
  UNKNOWN traces count as NOT met for whichever component they belong to.

Output: return strict JSON matching this schema exactly. No prose, no
Markdown fences.

{schema}
"""


async def run_evaluator(
    sme_data: SMEProfile,
    grant_data: GrantRequirement,
) -> EvaluatorOutput:
    """Audit ``sme_data`` against ``grant_data`` and return the structured result."""

    schema_json = json.dumps(EvaluatorOutput.model_json_schema(), indent=2)
    system_prompt = EVALUATOR_SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)

    user_prompt = (
        f"SME Profile:\n{sme_data.model_dump_json(indent=2)}\n\n"
        f"Grant Requirements:\n{grant_data.model_dump_json(indent=2)}"
    )

    client = GLMClient()
    result_dict = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
    )

    return EvaluatorOutput(**result_dict)


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
        documents_provided=["SSM Certificate", "Pitch Deck"],
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

    result = await run_evaluator(sme, grant)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
