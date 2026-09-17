import os
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .retrieval import retrieve_relevant_chunks


load_dotenv()


MODEL_NAME = "gemini-3.6-flash"


AllowedAction = Literal[
    "REQUEST_PHOTOS",
    "APPROVE_RETURN",
    "OPEN_SHIPPING_INVESTIGATION",
    "REPLACE_CORRECT_ITEM",
    "NEEDS_MORE_INFORMATION",
    "APPROVE_REFUND_OR_REPLACEMENT",
    "REQUEST_DEFECT_EVIDENCE",
    "APPROVE_REPLACEMENT",
    "CANNOT_CANCEL_AFTER_DISPATCH",
    "CANCEL_AND_REFUND",
]


class DecisionOutput(BaseModel):
    action: AllowedAction
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )
    reason: str
    sources: list[str]


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    return genai.Client(
        api_key=api_key
    )


def build_prompt(
    ticket_message: str,
    retrieved_chunks: list[dict]
) -> str:

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"Source: {chunk['source']}\n"
            f"Policy:\n{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    return f"""
You are an AI support-ticket decision assistant.

Your job is to determine the correct action for the customer
using ONLY the supplied policy context.

Do not invent policy rules.

If the available information is insufficient to make a reliable
decision, choose NEEDS_MORE_INFORMATION.

The confidence must be between 0 and 1.

The sources field must contain only filenames from the supplied
policy context that were actually used for the decision.

Allowed actions:
- REQUEST_PHOTOS
- APPROVE_RETURN
- OPEN_SHIPPING_INVESTIGATION
- REPLACE_CORRECT_ITEM
- NEEDS_MORE_INFORMATION
- APPROVE_REFUND_OR_REPLACEMENT
- REQUEST_DEFECT_EVIDENCE
- APPROVE_REPLACEMENT
- CANNOT_CANCEL_AFTER_DISPATCH
- CANCEL_AND_REFUND

Customer ticket:
{ticket_message}

Relevant policy context:
{context}
"""


def make_decision(
    ticket_message: str
) -> DecisionOutput:

    client = get_gemini_client()

    retrieved_chunks = retrieve_relevant_chunks(
        ticket_message,
        client,
        top_k=3
    )

    prompt = build_prompt(
        ticket_message,
        retrieved_chunks
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DecisionOutput,
            temperature=0
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    try:
        decision = DecisionOutput.model_validate_json(
            response.text
        )
    except Exception as exc:
        raise RuntimeError(
            "Gemini returned an invalid decision"
        ) from exc

    available_sources = {
        chunk["source"]
        for chunk in retrieved_chunks
    }

    invalid_sources = set(decision.sources) - available_sources

    if invalid_sources:
        raise RuntimeError(
            "Gemini returned a source that was not retrieved"
        )

    return decision