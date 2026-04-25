"""Coach agent (Track A): turn UNMET/UNKNOWN evaluator traces into next steps.

Takes the cold-logic output from the Evaluator and, for every requirement
the SME has not yet satisfied, produces a supportive, actionable step the
founder can take in Malaysia (e.g. where to obtain an SSM search, how to
pass a BOD resolution, which auditor templates to use).
"""

from __future__ import annotations

import asyncio
import json

try:
    from .glm_client import GLMClient
    from .schemas import CoachOutput, EvaluatorOutput, EvidenceTrace
except ImportError:  # pragma: no cover - supports direct script execution
    from glm_client import GLMClient
    from schemas import CoachOutput, EvaluatorOutput, EvidenceTrace


COACH_SYSTEM_PROMPT_TEMPLATE = """You are a supportive Startup Coach for Malaysian SMEs.

The user just applied for a grant but is missing some requirements. You will
be given a JSON array of Evaluator traces where status is "UNMET" or "UNKNOWN".

For every trace, create one ActionStep that:
  - explains plainly what the document / requirement is,
  - tells them exactly how to obtain or draft it in Malaysia
    (reference real, concrete sources where relevant: SSM, LHDN, MDEC,
    MIDA, MoF, licensed auditors, company secretary, template examples,
    etc.),
  - keeps the tone highly encouraging, professional, and can-do. Avoid
    shaming language. Assume the founder is smart and busy.

Also write one short "encouraging_message" (1-3 sentences) that frames the
gap as a small, solvable checklist — not a rejection.

Output: return strict JSON matching this schema exactly. No Markdown
fences, no prose outside the JSON.

{schema}
"""


async def run_coach(evaluator_results: EvaluatorOutput) -> CoachOutput:
    """Generate a supportive checklist of next steps for unmet requirements."""

    unmet_traces: list[EvidenceTrace] = [
        trace
        for trace in evaluator_results.evidence_traces
        if trace.status != "MET"
    ]

    schema_json = json.dumps(CoachOutput.model_json_schema(), indent=2)
    system_prompt = COACH_SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)

    user_prompt = json.dumps(
        [trace.model_dump() for trace in unmet_traces],
        indent=2,
    )

    client = GLMClient()
    result_dict = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
    )

    return CoachOutput(**result_dict)


async def _main() -> None:
    failed_audit = EvaluatorOutput(
        evidence_traces=[
            EvidenceTrace(
                requirement="Sector eligibility",
                status="MET",
                source_document="SME Profile.sector",
                reasoning="ICT is in the promoted sectors list.",
            ),
            EvidenceTrace(
                requirement="Mandatory document: Audited Financials",
                status="UNMET",
                source_document="SME Profile.documents_provided",
                reasoning="Audited Financials is not in documents_provided.",
            ),
            EvidenceTrace(
                requirement="Mandatory document: BOD Resolution",
                status="UNMET",
                source_document="SME Profile.documents_provided",
                reasoning="BOD Resolution is not in documents_provided.",
            ),
            EvidenceTrace(
                requirement="Mandatory document: Integrity Declaration",
                status="UNMET",
                source_document="SME Profile.documents_provided",
                reasoning="Integrity Declaration is not in documents_provided.",
            ),
        ],
        readiness_score=63,
    )

    result = await run_coach(failed_audit)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
