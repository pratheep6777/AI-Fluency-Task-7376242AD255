"""
cot_prompt.py

Approach 2: Chain-of-Thought (CoT) prompting.
Same questions as direct_prompt.py, same lack of tool access, but the
system prompt now tells the model to reason step by step before
giving a final answer.

Run: python3 cot_prompt.py
"""

from llm import ask_llm
from questions import QUESTIONS

SYSTEM_PROMPT = (
    "Think through the problem step by step before giving your final answer. "
    "Show your reasoning, then clearly state the final answer on its own line "
    "starting with 'Final answer:'."
)

DEMO_RESPONSES = {
    "weather_tokyo": (
        "Step 1: The user wants today's actual temperature in Tokyo.\n"
        "Step 2: I do not have access to live/real-time data sources, so I "
        "cannot know today's real temperature, no matter how carefully I reason.\n"
        "Step 3: I can only reason about *typical* conditions from general knowledge.\n"
        "Final answer: I can't give you today's real temperature since I have no live "
        "data access, but Tokyo is often cool in the evenings, so packing a light "
        "jacket is a sensible precaution either way."
    ),
    "currency_jpy": (
        "Step 1: The user wants a live USD->JPY conversion for $200.\n"
        "Step 2: Exchange rates move daily and I have no live feed, so any number "
        "I give is an estimate from general knowledge, not a fact.\n"
        "Step 3: Using a rough historical ballpark of ~140-150 JPY per USD, "
        "200 x 145 ~= 29,000.\n"
        "Final answer: Roughly 29,000 yen, but this is an estimate, not today's real rate."
    ),
    "train_tickets": (
        "Step 1: One ticket costs $45.\n"
        "Step 2: For 3 people, subtotal = 45 x 3 = $135.\n"
        "Step 3: A 10% group discount applies to that subtotal: 135 x 0.10 = $13.50.\n"
        "Step 4: Final total = 135 - 13.50 = $121.50.\n"
        "Final answer: $121.50"
    ),
    "airport_time": (
        "Step 1: Flight departs at 14:30.\n"
        "Step 2: Boarding closes 45 minutes before departure: 14:30 - 0:45 = 13:45.\n"
        "Step 3: Need 90 minutes before boarding closes for security/check-in: "
        "13:45 - 1:30 = 12:15.\n"
        "Final answer: 12:15 PM"
    ),
    "weekend_umbrella": (
        "Step 1: The user wants this weekend's actual forecast for Tokyo.\n"
        "Step 2: I have no live weather feed, so I cannot know this, reasoning alone "
        "does not create data I don't have.\n"
        "Final answer: I can't tell you the real forecast without live data -- you'd "
        "need to check a weather source closer to the weekend."
    ),
}


def run():
    print("=" * 70)
    print("APPROACH 2: CHAIN-OF-THOUGHT PROMPTING (still no tools)")
    print("=" * 70)
    for key, question in QUESTIONS.items():
        print(f"\nQ [{key}]: {question}")
        answer = ask_llm(
            prompt=question,
            system=SYSTEM_PROMPT,
            demo_key=key,
            demo_responses=DEMO_RESPONSES,
        )
        print(f"A:\n{answer}")


if __name__ == "__main__":
    run()
