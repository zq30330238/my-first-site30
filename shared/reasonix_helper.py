"""Reasonix CLI wrapper — replaces direct DeepSeek API calls with `reasonix run`.

Benefits:
- Automatic prefix caching (~94% cache hit on consecutive calls with same system prompt)
- Token counting and cost tracking
- No need to manage API keys in Python (Reasonix reads from env)
"""

import json
import subprocess
import sys
from pathlib import Path


def _find_reasonix():
    import shutil
    return shutil.which("reasonix") or "reasonix"


def reasonix_call(system_prompt: str, user_message: str, model: str = "deepseek-v4-flash", timeout: int = 300) -> str:
    """Call Reasonix with a system prompt and user message. Returns the raw text output.

    Reasonix's prefix caching ensures that repeated calls with the same system prompt
    get ~94% cache hit rate on subsequent calls.
    """
    cmd = [
        _find_reasonix(),
        "run",
        user_message,
        "--system", system_prompt,
        "--model", model,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=None,  # inherit env (includes DEEPSEEK_API_KEY)
        )

        if result.returncode != 0:
            raise RuntimeError(f"Reasonix exited code {result.returncode}: {result.stderr}")

        output = result.stdout

        # Remove the stats footer line (starts with "— turns:")
        lines = output.split("\n")
        content_lines = [l for l in lines if not l.startswith("— turns:")]
        output = "\n".join(content_lines).strip()

        return output

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Reasonix call timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError("Reasonix not found. Install with: npm install -g reasonix")


def reasonix_call_json(system_prompt: str, user_message: str, model: str = "deepseek-v4-flash", timeout: int = 300) -> dict:
    """Call Reasonix and parse the output as JSON.

    Expects the model to output valid JSON. Raises json.JSONDecodeError if parsing fails.
    """
    output = reasonix_call(system_prompt, user_message, model, timeout)

    # Try to find JSON in the output (handle potential surrounding text)
    output = output.strip()

    # Remove markdown code fences if present
    if output.startswith("```json"):
        output = output[7:]
    elif output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]

    # Find JSON boundaries
    brace_start = output.find("{")
    brace_end = output.rfind("}")

    if brace_start >= 0 and brace_end > brace_start:
        output = output[brace_start:brace_end + 1]

    return json.loads(output)
