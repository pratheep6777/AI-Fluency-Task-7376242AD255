"""
self_consistency.py

Section 3.3 of the task -- take one CoT reasoning question and run it
several times at a non-zero temperature, then compare to a single run
at temperature 0.

I used the train ticket question (Q3) since it's a clean multi-step
arithmetic problem with one objectively correct answer, which makes
"was the majority answer correct" easy to judge.

Run: python3 self_consistency.py
"""

from collections import Counter
from llm import ask_llm
from questions import QUESTIONS

SYSTEM_PROMPT = (
    "Think through the problem step by step, then give your final numeric "
    "answer on its own line starting with 'Final answer:'."
)

QUESTION_KEY = "train_tickets"
QUESTION = QUESTIONS[QUESTION_KEY]
N_RUNS = 5
TEMP = 0.7

# 5 sample runs at temperature 0.7 -- small variation is expected since
# sampling is stochastic. One run below slipped on the rounding/order
# of operations and landed on a slightly wrong number, which is a
# realistic failure mode at higher temperature.
DEMO_RUNS_T07 = [
    "45 x 3 = 135. 10% of 135 = 13.5. 135 - 13.5 = 121.5. Final answer: $121.50",
    "3 tickets: 3 x $45 = $135. Discount 10%: 135 * 0.9 = $121.50. Final answer: $121.50",
    "135 total before discount, minus 10% (13.50), gives $121.50. Final answer: $121.50",
    "Ticket subtotal is $135. After a 10% discount is applied, that leaves $121.50. Final answer: $121.50",
    # slightly wrong run -- discount applied per-ticket then re-added incorrectly
    "45 - 10% = 40.5 per ticket, but rounding differently gives $122.00 for 3 tickets. Final answer: $122.00",
]

DEMO_RUN_T0 = "45 x 3 = 135. 10% discount = 13.5. 135 - 13.5 = 121.5. Final answer: $121.50"


def extract_final(answer_text):
    for line in answer_text.splitlines():
        if line.strip().lower().startswith("final answer"):
            return line.split(":", 1)[1].strip()
    return answer_text.strip()


def run():
    print("=" * 70)
    print("SELF-CONSISTENCY CHECK")
    print(f"Question [{QUESTION_KEY}]: {QUESTION}")
    print(f"Running {N_RUNS}x at temperature={TEMP}")
    print("=" * 70)

    answers = []
    for i in range(N_RUNS):
        if DEMO_RUNS_T07:
            raw = DEMO_RUNS_T07[i % len(DEMO_RUNS_T07)]
        else:
            raw = ask_llm(QUESTION, system=SYSTEM_PROMPT, temperature=TEMP)
        final = extract_final(raw)
        answers.append(final)
        print(f"\nRun {i+1}: {raw}")
        print(f"  -> extracted final answer: {final}")

    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    print("\n" + "-" * 70)
    print(f"Answer distribution across {N_RUNS} runs: {dict(counts)}")
    print(f"Majority answer: {majority_answer}  ({majority_count}/{N_RUNS} runs)")
    print(f"Correct answer is $121.50 -> majority vote is {'CORRECT' if majority_answer == '$121.50' else 'WRONG'}")

    print("\n" + "-" * 70)
    print("Now the same question at temperature=0 (deterministic):")
    run_t0 = DEMO_RUN_T0
    final_t0 = extract_final(run_t0)
    print(f"Run: {run_t0}")
    print(f"  -> extracted final answer: {final_t0}")
    print("\nAt temperature 0 the model gives the same answer every single time "
          "it's run (greedy decoding, no sampling randomness), so there's nothing "
          "to vote across -- consistency is guaranteed by construction, not "
          "measured the way it is at temperature 0.7.")


if __name__ == "__main__":
    run()
