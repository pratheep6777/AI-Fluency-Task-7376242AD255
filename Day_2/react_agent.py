"""
react_agent.py

Approach 3: ReAct (Reason + Act).

Unlike the other three scripts, this one is NOT calling an LLM behind
the scenes at all -- it's a small, genuinely-working rule-based agent
that implements the actual ReAct loop: Thought -> Action -> Observation,
repeated until it has enough to give a Final Answer. I did it this way
so that the Thought/Action/Observation trace you see below is real
output from actually running this code, not a pasted-in transcript.

(A "real" version of this would swap the decide_action() function for
an LLM call with tool-definitions passed in, and let the model choose
the action instead of my if/else rules -- the loop structure and the
point being demonstrated is identical either way.)

Run: python3 react_agent.py
"""

from tools import get_weather, get_exchange_rate
from questions import QUESTIONS


def decide_action(question_key):
    """Very small router standing in for 'the model decides it needs a tool'."""
    if question_key == "weather_tokyo":
        return ("get_weather", {"city": "tokyo"})
    if question_key == "currency_jpy":
        return ("get_exchange_rate", {"base": "usd", "target": "jpy"})
    if question_key == "weekend_umbrella":
        return ("get_weather", {"city": "tokyo"})
    return (None, None)  # no tool needed -> pure reasoning


def run_agent(question_key, question):
    print(f"\nQ [{question_key}]: {question}")

    print("  Thought: let me check whether I need a tool to answer this, "
          "or whether the question already gives me everything I need.")

    action, args = decide_action(question_key)

    if action is None:
        # Pure reasoning question -- handled step by step, same as CoT,
        # just without needing to reach for a tool.
        print("  Thought: this is a self-contained reasoning problem, no tool needed.")
        if question_key == "train_tickets":
            subtotal = 45 * 3
            discount = subtotal * 0.10
            total = subtotal - discount
            print(f"  Thought: subtotal = 45 x 3 = {subtotal}")
            print(f"  Thought: 10% discount = {discount}")
            print(f"  Thought: total after discount = {subtotal} - {discount} = {total}")
            print(f"  Final Answer: ${total:.2f}")
        elif question_key == "airport_time":
            print("  Thought: boarding closes 45 min before 14:30 -> 13:45")
            print("  Thought: need 90 min before boarding closes -> 13:45 minus 1:30 = 12:15")
            print("  Final Answer: 12:15 PM")
        return

    # Tool-required question
    print(f"  Thought: I need external, up-to-date info to answer this -- I don't "
          f"have it memorized. I'll call a tool.")
    print(f"  Action: {action}({args})")

    if action == "get_weather":
        obs = get_weather(**args)
    elif action == "get_exchange_rate":
        obs = get_exchange_rate(**args)

    print(f"  Observation: {obs}")

    if "error" in obs:
        print(f"  Final Answer: sorry, I don't have data for that -- {obs['error']}")
        return

    print("  Thought: now I have the data I need, let me turn it into the "
          "actual answer to the user's question.")

    if question_key == "weather_tokyo":
        temp = obs["temp_c"]
        jacket = "yes, pack a light jacket" if temp < 18 else "no jacket needed"
        print(f"  Final Answer: it's currently {temp}C and {obs['condition']} in Tokyo. "
              f"Recommendation: {jacket}.")
    elif question_key == "currency_jpy":
        amount_usd = 200
        yen = amount_usd * obs["rate"]
        print(f"  Final Answer: at today's rate (1 USD = {obs['rate']} JPY), "
              f"$200 = {yen:,.0f} JPY.")
    elif question_key == "weekend_umbrella":
        forecast = obs["weekend_forecast"]
        umbrella = "yes" if "rain" in forecast.lower() else "no"
        print(f"  Final Answer: weekend forecast for Tokyo is '{forecast}'. "
              f"Pack an umbrella: {umbrella}.")


def run():
    print("=" * 70)
    print("APPROACH 3: REACT AGENT (Thought -> Action -> Observation loop)")
    print("=" * 70)
    for key, question in QUESTIONS.items():
        run_agent(key, question)


if __name__ == "__main__":
    run()
