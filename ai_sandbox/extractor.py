"""Extractor agent: raw SME blurb -> validated ``SMEProfile``.

Uses GLM with a dynamically-injected Pydantic JSON schema so the model
knows exactly which fields, types, and enum values we expect.
"""

from __future__ import annotations

import asyncio
import json

from glm_client import GLMClient
from schemas import SMEProfile


EXTRACTOR_SYSTEM_PROMPT_TEMPLATE = """You are an expert data extractor for the Malaysia SME Grant Copilot.

Extract the business details from the user's text and return a JSON object that
strictly conforms to this schema:

{schema}

Rules for missing values:
- If a string field is missing, use "Unknown".
- If an integer field is missing, use 0.
- If a boolean is missing, use false.

Only output the JSON object. Do not include Markdown fences, comments, or any
additional prose."""


async def run_extractor(raw_text: str) -> SMEProfile:
    """Extract a validated ``SMEProfile`` from a free-form business description."""

    schema_json = json.dumps(SMEProfile.model_json_schema(), indent=2)
    system_prompt = EXTRACTOR_SYSTEM_PROMPT_TEMPLATE.format(schema=schema_json)

    client = GLMClient()
    result_dict = await client.generate_json(
        system_prompt=system_prompt,
        user_prompt=raw_text,
        temperature=0.0,
    )

    return SMEProfile(**result_dict)


_DUMMY_TEXT = (
    "Welcome to TechBina Sdn Bhd (SSM: 1234567-V). We are a local software "
    "development agency in the ICT sector, operating for 24 months now. We have "
    "a lean team of 5 full-time employees and are 100% locally owned. We are "
    "looking to apply for a grant. Our total project cost is estimated at "
    "RM 500,000, and we are requesting RM 250,000 in funding. We will only be "
    "outsourcing about RM 20,000 for cloud infrastructure setup. We have "
    "already signed an MoU with our end-user partner, Hospital Kuala Lumpur. "
    "I've uploaded our SSM Certificate and Pitch Deck."
)


async def _main() -> None:
    profile = await run_extractor(_DUMMY_TEXT)
    print(profile.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
