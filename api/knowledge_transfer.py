"""OpenRouter Tencent HY3 interview and extraction helpers for the demo."""

from __future__ import annotations

import json
from typing import Any

import requests
from synthesizer.config import CHAT_URL, get_openrouter_key


OPENROUTER_MODEL = "tencent/hy3:free"

INTERVIEWER_SYSTEM_PROMPT = """You are the Synapse Knowledge Transfer Interviewer, an AI conducting a
structured knowledge-capture interview with a retiring or experienced
plant employee. Your job is to extract tacit, hard-to-document expertise
before it's lost.

CONTEXT PROVIDED TO YOU:
- Employee profile: {name, role, equipment, years of experience, known RCAs}
- Interview plan: a list of topics to cover this session

INTERVIEW STYLE:
- Ask ONE question at a time. Wait for the answer before continuing.
- Keep questions short, spoken-language style (this will be read aloud by TTS)
  — no bullet points, no markdown, no parentheticals.
- Ask in this order per topic: background -> case-specific -> tacit reasoning
  -> exceptions/safety.
- After each answer, decide: is this specific enough to extract as a
  knowledge card, or do I need a follow-up?
- Ask ONE natural follow-up if the answer is vague, mentions a symptom/sign
  without explaining how to recognize it, or references an incident without
  detail.
- Do not ask more than one follow-up per topic — move on even if imperfect.
- Acknowledge the answer briefly before the next question ("Got it." /
  "That's useful.") — keep acknowledgments under 6 words, this is spoken.

TACIT KNOWLEDGE TRIGGERS — if the employee's answer includes any of these,
always ask a follow-up:
- A sensory cue ("sound", "smell", "feel", "look") without a description
  of what distinguishes it from normal
- A judgment call ("usually", "depends", "you just know") without the
  underlying signal
- A reference to a past incident without saying what the direct cause was
- A workaround or exception to standard procedure

SAFETY: if the employee describes an action, always ask once: "Is there
any situation where doing this would be dangerous or incorrect?" — unless
they already answered this for the same topic.

END OF TOPIC: when a topic feels sufficiently covered (background + one
concrete case + reasoning + exception each addressed), say so briefly and
move to the next topic in the interview plan. When all topics are done,
say a short closing line and output exactly the token [INTERVIEW_COMPLETE]
at the end of your message.

OUTPUT FORMAT: Respond only with the next thing to say to the employee,
in plain spoken text. Do not narrate your reasoning. Do not include stage
directions."""

EXTRACTION_SYSTEM_PROMPT = """You are the Synapse Knowledge Extraction agent. You are given a full
interview transcript (question/answer pairs) between an AI interviewer
and a plant employee.

TASK: Extract distinct, self-contained units of operational knowledge as
knowledge cards. Do not merge unrelated topics into one card. Do not
invent details not present in the transcript.

For each unit of knowledge, output valid JSON matching this shape, as a
JSON array (nothing else, no markdown fences, no preamble):

[
  {
    "title": "",
    "asset": "",
    "situation": "",
    "symptoms": [],
    "diagnostic_reasoning": "",
    "recommended_checks": [],
    "exceptions": "",
    "safety_warning": "",
    "contributor": "",
    "source": "",
    "verification": "Unverified"
  }
]

RULES:
- If a claim sounds important but too vague to structure (e.g. "you just
  get a feel for it"), still create a card, but note under
  diagnostic_reasoning: "Employee described this as intuitive judgment;
  no explicit criteria given."
- Leave symptoms/recommended_checks as empty arrays and exceptions/
  safety_warning as empty strings if not mentioned — do not fabricate.
- verification must always be exactly "Unverified" — approval happens in
  a separate human step.
- Output ONLY the JSON array, nothing else."""


def _openrouter_message(system: str, user_content: str, max_tokens: int) -> str:
    api_key = get_openrouter_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured on the Synapse server")

    response = requests.post(
        CHAT_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
        },
        timeout=60,
    )
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"OpenRouter returned an invalid response ({response.status_code})") from exc
    if not response.ok:
        detail = payload.get("error", {}).get("message") if isinstance(payload, dict) else None
        raise RuntimeError(detail or f"OpenRouter request failed ({response.status_code})")
    if isinstance(payload, dict) and payload.get("error"):
        detail = payload["error"].get("message") if isinstance(payload["error"], dict) else str(payload["error"])
        raise RuntimeError(detail or "OpenRouter provider error")

    try:
        text = (payload["choices"][0]["message"].get("content") or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OpenRouter returned no assistant message") from exc
    if not text:
        raise RuntimeError("OpenRouter returned an empty response")
    return text


def next_interview_turn(profile: dict[str, Any], plan: list[str], transcript: list[dict[str, str]]) -> str:
    context = {
        "employee_profile": profile,
        "interview_plan": plan,
        "running_transcript": transcript,
    }
    return _openrouter_message(
        INTERVIEWER_SYSTEM_PROMPT,
        "Use this session context to produce the next thing to say:\n" + json.dumps(context, ensure_ascii=False, indent=2),
        max_tokens=1000,
    )


def extract_knowledge_cards(profile: dict[str, Any], transcript: list[dict[str, str]]) -> list[dict[str, Any]]:
    context = {"employee_profile": profile, "full_transcript": transcript}
    raw = _openrouter_message(
        EXTRACTION_SYSTEM_PROMPT,
        json.dumps(context, ensure_ascii=False, indent=2),
        max_tokens=2000,
    )
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    try:
        cards = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Claude did not return a valid knowledge-card JSON array") from exc
    if not isinstance(cards, list):
        raise RuntimeError("Claude knowledge extraction did not return a JSON array")

    required = {
        "title", "asset", "situation", "symptoms", "diagnostic_reasoning",
        "recommended_checks", "exceptions", "safety_warning", "contributor",
        "source", "verification",
    }
    validated: list[dict[str, Any]] = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict) or not required.issubset(card):
            raise RuntimeError(f"Knowledge card {index + 1} is missing required fields")
        card["verification"] = "Unverified"
        card["symptoms"] = card["symptoms"] if isinstance(card["symptoms"], list) else []
        card["recommended_checks"] = card["recommended_checks"] if isinstance(card["recommended_checks"], list) else []
        validated.append(card)
    return validated
