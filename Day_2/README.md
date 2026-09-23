# Weekend Trip Planner -- Direct Prompting vs CoT vs ReAct

Day 2 task for Agentic AI: Foundations and Open-Source Practice (Unit 1, sub-topics 1.3
and 1.4 -- Chain-of-Thought and the ReAct cycle).

Scenario: a small assistant helping someone plan a weekend trip to Tokyo. Some questions
need live/external info (current temperature, current exchange rate, weekend forecast),
and some are just arithmetic word problems the model can solve on its own (splitting a
discounted train fare, working out an airport arrival time). The point of the task is to
show how the same scenario plays out under three different prompting/agent styles.

## Files

| File | What it does |
|---|---|
| `questions.py` | The 5 scenario questions, shared by every script |
| `tools.py` | Mocked `get_weather()` / `get_exchange_rate()` "tool" functions (see docstring for why they're mocked, not live) |
| `llm.py` | Thin Anthropic API wrapper shared by the prompting scripts, with a DEMO_MODE fallback |
| `direct_prompt.py` | Approach 1 -- straight question, no reasoning instruction, no tools |
| `cot_prompt.py` | Approach 2 -- adds a "think step by step" system prompt, still no tools |
| `self_consistency.py` | Runs one CoT question 5x at temperature 0.7 and once at temperature 0, majority-votes the result |
| `react_agent.py` | Approach 3 -- a real, working Thought -> Action -> Observation loop that actually calls `tools.py` |
| `analysis.md` | The full written analysis (task section 3) |
| `screenshots/` | PNG captures of each script's console output |

## Running it

```bash
pip install -r requirements.txt

# optional: set a real key to hit the live API instead of demo mode
export ANTHROPIC_API_KEY=your_key_here

python3 direct_prompt.py
python3 cot_prompt.py
python3 self_consistency.py
python3 react_agent.py
```

If `ANTHROPIC_API_KEY` isn't set, `direct_prompt.py`, `cot_prompt.py` and
`self_consistency.py` fall back to pre-recorded sample responses (see `llm.py`) so the
whole thing still runs end to end without a key -- that's what I used to generate the
screenshots in this submission. `react_agent.py` doesn't need a key at all; it's a
genuine rule-based agent, not a wrapped LLM call, so its output in the screenshots is
real, not cached.

## Notes

- `tools.py` uses local mock data instead of a live weather/forex API (see the docstring
  at the top of that file for why). The tool-calling *pattern* -- deciding a tool is
  needed, calling it, reading the observation back -- is unaffected by whether the data
  behind it is live or local.
- Full analysis, including the comparison table and self-consistency results, is in
  `analysis.md`.
