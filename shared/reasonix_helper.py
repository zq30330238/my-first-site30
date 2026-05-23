"""DeepSeek API wrapper — direct HTTP calls, bypasses `reasonix` agent framework.

reasonix is a DeepSeek-native agent framework that gives the model tools (file access,
skill running, etc.). For article generation we need the model to output clean JSON,
not research the codebase. So we call the API directly.

System prompt caching still works at the API level — identical system prompts
get server-side cache hits (~94% on consecutive calls).
"""

import json
import os
import time
from pathlib import Path

import requests


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"


def _call_deepseek(system_prompt: str, user_message: str, model: str = MODEL, timeout: int = 300) -> str:
    """Call DeepSeek chat API directly. Returns the response text."""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY not set in environment")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,  # lower = more deterministic JSON output
        "max_tokens": 8192,
    }

    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"DeepSeek API error {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"No choices in DeepSeek response: {data}")

    return choices[0]["message"]["content"]


def _sanitize_json_text(text: str) -> str:
    """Replace smart quotes and common Unicode that breaks json.loads."""
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('–', '-').replace('—', '--')
    text = text.replace('…', '...')
    return text


def reasonix_call(system_prompt: str, user_message: str, model: str = MODEL, timeout: int = 300) -> str:
    """Call DeepSeek with a system prompt and user message. Returns the raw text output.

    Uses direct API call (bypasses reasonix agent framework).
    """
    return _call_deepseek(system_prompt, user_message, model, timeout)


def _repair_unescaped_quotes(text: str) -> str:
    """Repair unescaped double quotes inside JSON string values.

    The model sometimes outputs HTML content with unescaped " inside JSON strings
    (e.g. `<blockquote>"text"</blockquote>`). This function scans for such patterns
    and escapes them.
    """
    import re
    # Pattern: inside a JSON string value, a " preceded by an HTML tag end (>) or
    # followed by an HTML tag start (<) is likely unescaped.
    # Replace " that appears right before < or right after > within the text.
    text = re.sub(r'"(?=<)', r'\"', text)
    text = re.sub(r'(?<=>)(")', r'\"', text)
    return text


def reasonix_call_json(system_prompt: str, user_message: str, model: str = MODEL, timeout: int = 300) -> dict:
    """Call DeepSeek and parse the output as JSON.

    Finds the LAST valid JSON object in output (most robust approach).
    Falls back to repairing unescaped quotes in HTML content within JSON strings.
    Raises json.JSONDecodeError if no valid JSON is found.
    """
    output = _call_deepseek(system_prompt, user_message, model, timeout)
    output = output.strip()

    # Remove markdown code fences if present
    if output.startswith("```json"):
        output = output[7:]
    elif output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]

    # Replace smart quotes and Unicode that break json.loads
    output = _sanitize_json_text(output)

    def _try_parse(clean_output: str) -> dict | None:
        """Try multiple parsing strategies."""
        # Strategy 1: direct json.loads
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            pass

        # Strategy 2: raw_decode from each { position backwards
        decoder = json.JSONDecoder()
        search = clean_output
        while True:
            brace_start = search.rfind("{")
            if brace_start == -1:
                break
            try:
                obj, end = decoder.raw_decode(search, brace_start)
                return obj
            except json.JSONDecodeError:
                search = search[:brace_start] + " " + search[brace_start + 1:]
                continue

        return None

    # First try: parse as-is
    result = _try_parse(output)
    if result is not None:
        return result

    # Second try: repair unescaped quotes in HTML content and retry
    repaired = _repair_unescaped_quotes(output)
    result = _try_parse(repaired)
    if result is not None:
        return result

    raise json.JSONDecodeError("No JSON object found in output", output, 0)


ARK_API_KEY = os.environ.get("ARK_API_KEY", "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727")
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"


def _call_ark(system_prompt: str, user_message: str, model: str = "doubao-seed-1-8-251228", timeout: int = 300) -> str:
    """Call Volcengine Ark chat API directly. Returns the response text."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 8192,
    }
    resp = requests.post(
        ARK_API_URL,
        headers={
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Ark API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"No choices in Ark response: {data}")
    return choices[0]["message"]["content"]


def ark_call_json(system_prompt: str, user_message: str, model: str = "doubao-seed-1-8-251228", timeout: int = 300) -> dict:
    """Call Ark API (Doubao Seed) and parse the output as JSON.
    Uses the same JSON parsing logic as reasonix_call_json but with Ark API.
    """
    output = _call_ark(system_prompt, user_message, model, timeout)
    output = output.strip()

    if output.startswith("```json"):
        output = output[7:]
    elif output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]

    output = _sanitize_json_text(output)

    def _try_parse(clean_output: str) -> dict | None:
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            pass
        decoder = json.JSONDecoder()
        search = clean_output
        while True:
            brace_start = search.rfind("{")
            if brace_start == -1:
                break
            try:
                obj, end = decoder.raw_decode(search, brace_start)
                return obj
            except json.JSONDecodeError:
                search = search[:brace_start] + " " + search[brace_start + 1:]
                continue
        return None

    result = _try_parse(output)
    if result is not None:
        return result

    repaired = _repair_unescaped_quotes(output)
    result = _try_parse(repaired)
    if result is not None:
        return result

    raise json.JSONDecodeError("No JSON object found in output", output, 0)
