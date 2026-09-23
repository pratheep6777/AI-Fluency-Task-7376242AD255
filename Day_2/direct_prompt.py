"""
direct_prompt.py

Approach 1: Direct prompting.
The model just gets the raw question and answers immediately -- no
"think step by step" instruction, no tools available to it at all.

Run: python3 direct_prompt.py
"""

from llm import ask_llm
from questions import QUESTIONS

# Cached sample answers (see llm.py docstring for why these exist).
# These are what direct prompting actually produced when I tested the
# prompts -- deliberately kept as-is, including the wrong answer on
# Q3, because that mistake is the whole point of comparing to CoT.
DEMO_RESPONSES = {
    "weather_tokyo": (
        "I don't have access to real-time weather data, so I can't give you "
        "today's exact temperature in Tokyo. Generally speaking, Tokyo evenings "
        "can get cool, so bringing a light jacket is a reasonably safe idea."
    ),
    "currency_jpy": (
        "I don't have live exchange rate data, but historically USD to JPY has "
        "hovered somewhere around 140-150. So $200 would be roughly 28,000-30,000 "
        "yen, though you should check a live converter before your trip."
    ),
    "train_tickets": (
        "The total cost would be $135."
    ),
    "airport_time": (
        "You should arrive at the airport by 12:15 PM."
    ),
    "weekend_umbrella": (
        "I don't have live forecast data for this weekend, so I can't say for "
        "certain -- I'd check a weather app closer to the date."
    ),
}


def run():
    print("=" * 70)
    print("APPROACH 1: DIRECT PROMPTING (no tools, no CoT instruction)")
    print("=" * 70)
    for key, question in QUESTIONS.items():
        print(f"\nQ [{key}]: {question}")
        answer = ask_llm(prompt=question, demo_key=key, demo_responses=DEMO_RESPONSES)
        print(f"A: {answer}")


if __name__ == "__main__":
    run()
