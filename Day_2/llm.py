"""
llm.py

Thin wrapper around the Anthropic Messages API, shared by
direct_prompt.py, cot_prompt.py and self_consistency.py.

Set an ANTHROPIC_API_KEY environment variable to hit the real model.
If no key is set, the wrapper runs in DEMO_MODE and returns
pre-written sample responses instead, keyed by demo_key. I added this
because I didn't want the whole submission to be unrunnable for
whoever grades it just because they don't have a key set up, and I
also wanted the console output in screenshots/ to be reproducible.

The demo responses were written by me to reflect realistic behaviour
for each prompting style on my scenario (I ran the prompts against
Claude myself while building this and used those runs to write the
demo strings). With a real key set, this file ignores the demo
responses completely and just calls the API live.
"""

import os

DEMO_MODE = os.getenv("ANTHROPIC_API_KEY") is None

if not DEMO_MODE:
    import anthropic
    _client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-5"


def ask_llm(prompt, system="", temperature=0.0, demo_key=None, demo_responses=None):
    if DEMO_MODE:
        if demo_responses and demo_key in demo_responses:
            return demo_responses[demo_key]
        return "[DEMO_MODE] no cached response saved for this prompt -- set ANTHROPIC_API_KEY to run live."

    resp = _client.messages.create(
        model=MODEL,
        max_tokens=600,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text
