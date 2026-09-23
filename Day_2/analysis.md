# Analysis: Direct Prompting vs Chain-of-Thought vs ReAct

**Scenario:** Weekend Trip Planning Assistant. I'm getting ready for a short trip to
Tokyo and I ask the assistant a mix of five questions -- two need live/external info
(current temperature, current exchange rate, plus a weekend forecast question is a third
one in that bucket), and two are self-contained word problems that just need careful
arithmetic (splitting a discounted train fare three ways, and working backward from a
flight time to an airport arrival time).

I picked this scenario because it's a realistic case where a single "assistant"
personality genuinely needs both capabilities at once -- it can't get away with pure
reasoning on everything, and it can't get away with pure tool-calling either, since two
of the questions don't need a tool at all.

All the code for this lives in the repo root (`tools.py`, `direct_prompt.py`,
`cot_prompt.py`, `self_consistency.py`, `react_agent.py`) and the raw console output is
saved as images in `screenshots/`.

---

## 3.1 Explanation of each approach

### Direct prompting

Direct prompting is just handing the model the question with nothing else attached --
no instruction to reason out loud, and no tools available to call. It goes straight from
question to answer in one shot.

On my scenario this showed up in a pretty telling way. For the two questions that
actually needed live data (Tokyo's current temperature, and today's USD->JPY rate), the
model was upfront that it didn't have real-time access and gave a rough, caveated guess
instead of pretending to know. That's the honest failure mode, but it's still a failure
-- the user asked for a current number and didn't get one.

The more interesting failure was on the train ticket question. Without being asked to
show its work, the model answered "$135" -- which is just 3 tickets x $45, completely
skipping the 10% group discount that was explicitly mentioned in the question. It didn't
skip the discount because it doesn't know how to do a discount calculation; it skipped it
because with no instruction to slow down, it pattern-matched to the more obvious number
and didn't check itself. That's exactly the kind of mistake direct prompting is known
for on anything with more than one arithmetic step.

It got the airport-arrival question right, though, so direct prompting isn't broken --
it's just unreliable in a way you can't predict from the outside, and you can't see *why*
it got one multi-step question right and the other wrong because there's no visible
reasoning at all.

### Chain-of-Thought (CoT)

CoT prompting is the same setup -- still no tools -- but with an instruction to reason
step by step before committing to a final answer.

On the two tool-need questions, CoT didn't magically fix anything, and it shouldn't --
no amount of step-by-step reasoning invents real-time data the model was never given.
What it did do was make the *reason* for the uncertainty visible and explicit ("I do not
have access to live data sources, so I cannot know today's real temperature") instead of
just quietly guessing, which is a smaller but genuinely useful improvement in honesty.

Where CoT actually mattered was the train ticket question. Forced to write out the steps
(subtotal, then discount, then subtract), it correctly landed on $121.50 -- the same
question direct prompting got wrong. Being made to externalize the intermediate steps
caught the exact mistake direct prompting made. Same thing on the airport question: the
reasoning was now visible step by step (14:30 -> 13:45 -> 12:15), so even though direct
prompting also got that one right, with CoT I can actually check *how* it got there
instead of just trusting the number.

So the limitation of CoT on my scenario is specifically the tool-need questions -- CoT
improves reasoning depth and reliability on self-contained problems, but it has a hard
ceiling: it cannot fetch a fact the model doesn't already have.

### ReAct

ReAct is the only one of the three that can actually close the gap on the tool-need
questions, because it isn't limited to "reason harder" -- it can go get more information.
The loop is: Thought (what do I need / do I already have enough to answer), Action (call
a tool if not), Observation (read back what the tool returned), and repeat until there's
enough to give a Final Answer.

On my scenario, the agent correctly recognized that the temperature, exchange rate, and
weekend forecast questions all needed live data it didn't have memorized, called
`get_weather()` or `get_exchange_rate()`, read the observation back, and only then
produced a final answer grounded in that data -- e.g. "$200 = 29,970 JPY" using the
actual rate returned by the tool, instead of a hedged historical guess. For the two pure
reasoning questions, it correctly skipped the tool step entirely and reasoned directly,
landing on the same $121.50 and 12:15 answers CoT got.

The full Thought/Action/Observation/Final Answer trace for all five questions is in
`screenshots/4_react_agent.png` and it's straightforward to follow end to end without
needing to see the code.

Where ReAct's limitation shows up on my scenario is tool coverage, not reasoning: it's
only as good as the tools it's been given. If I asked it about a city that isn't in my
mocked weather database, it can't reason its way around that gap either -- it would just
get back an error observation and have to say so, which is a different kind of honest
failure than direct prompting's silent guess, but still a failure.

---

## 3.2 Comparison table

| Basis for comparison | Direct prompting | Chain-of-Thought | ReAct agent |
|---|---|---|---|
| Reasoning depth | None visible -- answer appears in one step | Full step-by-step breakdown shown before the final answer | Full step-by-step Thought trace, interleaved with tool calls |
| Tool usage | None -- can't access anything outside its own knowledge | None -- same limitation as direct prompting | Yes -- decides per-question whether a tool is needed, calls it, reads the result |
| Reliability on multi-step questions | Inconsistent -- got the discount question wrong, airport question right, with no way to predict which | High on self-contained problems -- caught the exact mistake direct prompting made | High on both types -- correct on the reasoning-only questions, and grounded/correct on the tool-need questions since it uses live-ish data instead of guessing |
| Transparency (can you see how it got there?) | No -- black box, just a final answer | Yes -- every intermediate step is written out | Yes -- every Thought, Action, and Observation is logged, plus the final reasoning step that turns the observation into an answer |
| Speed / cost | Fastest / cheapest -- one short call, no extra tokens | Slower / more expensive than direct -- extra reasoning tokens generated every time | Slowest / most expensive of the three -- multiple round trips (reasoning + tool call + reasoning again) per tool-need question |
| Consistency across repeated runs | Not tested formally here, but by nature has no way to catch its own slip-ups | Mostly consistent, but see 3.3 -- a small number of runs at higher temperature still landed on a slightly wrong number | Deterministic for the tool-need questions, since the tool call always returns the same value; still depends on the reasoning step around it being consistent |

---

## 3.3 Self-consistency observation

I used the train ticket question (`train_tickets` in `questions.py`) for this, since it
has one objectively correct answer ($121.50), which makes it easy to check whether a
"majority vote" answer is actually right.

I ran the CoT-style prompt 5 times at temperature 0.7. Output is in
`screenshots/3_self_consistency.png`. Results:

| Run | Final answer |
|---|---|
| 1 | $121.50 |
| 2 | $121.50 |
| 3 | $121.50 |
| 4 | $121.50 |
| 5 | $122.00 |

Distribution: `{'$121.50': 4, '$122.00': 1}`.

**Majority answer: $121.50, and it's correct.** 4 out of 5 runs landed on the right
number by taking the discount off the $135 subtotal correctly. Run 5 is the interesting
one -- it took a different (and slightly muddled) path, discounting each ticket
individually and then re-combining in a way that introduced a small rounding/logic slip,
landing one dollar off at $122.00. That's a small but real example of why running the
same reasoning question multiple times and voting on the outcome can be more robust than
trusting any single run, especially at a non-zero temperature where the model doesn't
always take the same path to the answer.

At **temperature 0**, I ran the same question once and it gave $121.50 -- and it would
keep giving $121.50 every time, because temperature 0 means the model always picks the
single most likely next token (greedy decoding) instead of sampling, so there's no
run-to-run randomness left to vote across. Self-consistency as a technique is really only
meaningful at temperature > 0; at temperature 0 "consistency" is guaranteed by how the
decoding works, not something you need to measure by repeating the call.

---

## 3.4 Suitability analysis

For my scenario specifically, **ReAct is the most suitable approach**, and it's not
close.

The scenario was deliberately built so that some questions need live/external data
(current temperature, current exchange rate, weekend forecast) and some don't (the two
arithmetic word problems). Direct prompting and CoT are both structurally incapable of
answering the tool-need questions correctly -- not because they reason poorly, but
because the information simply isn't available inside the model's own knowledge, and no
amount of "think step by step" changes that (see 3.1 and the table in 3.2, "tool usage"
row). Both of them were honest about this rather than hallucinating a confident wrong
number, which is good, but "I don't know" isn't actually a satisfying answer to "what's
the weather right now" from a trip-planning assistant -- the whole point of asking is to
get a real answer.

ReAct closes that gap directly, because it can recognize when it's missing information
and go get it rather than just reasoning around the hole. On the two pure-reasoning
questions where no tool was needed, ReAct performed identically to CoT (same $121.50,
same 12:15), so it didn't cost anything on that half of the scenario either.

The self-consistency observation in 3.3 reinforces this a different way: even on a
question that *doesn't* need a tool, a single CoT run can still occasionally slip
(the $122.00 outlier), which is the kind of thing ReAct's more structured,
step-verified loop (explicit subtotal -> explicit discount -> explicit total, each
printed as its own Thought) is less prone to than a single free-form CoT pass, since each
intermediate quantity is pinned down explicitly rather than computed inside one longer
block of reasoning.

The trade-off, and it's a real one from the comparison table, is cost and speed: ReAct is
the slowest and most expensive of the three because of the extra round trips for tool
calls. For a scenario like a trip-planning assistant where accuracy on live facts
actually matters to the user's plans, that trade-off is clearly worth it. It would be a
worse trade-off for something like "give me a quick synonym for 'happy'" where direct
prompting is not just adequate but obviously the better choice.

---

## 3.5 Conclusion

Stepping back from my specific scenario, here's when I'd reach for each approach in
general:

**Direct prompting** is the right call when the question is simple, the model's own
knowledge is genuinely enough to answer it, and speed/cost matter more than seeing the
reasoning. Simple factual recall, rewriting text, quick translations, casual
conversation -- none of that needs step-by-step reasoning or tool access, and adding
either would just be slower and more expensive for no real benefit.

**Chain-of-Thought** earns its extra cost when the question involves multiple steps that
have to be tracked correctly -- arithmetic word problems, multi-step logic, anything
where a model jumping straight to an answer is prone to skipping a step (like the
discount it missed in my direct-prompting run). CoT's ceiling is that it only improves
*reasoning about information the model already has* -- it doesn't extend what the model
knows or let it interact with the outside world, so it's the wrong tool whenever the
question depends on something time-sensitive, personal to the user, or otherwise outside
the model's training data.

**ReAct** is the right choice specifically when a question needs both reasoning *and*
outside information (or action) to answer correctly -- live data, private/user-specific
data, doing a calculation on numbers that live in a database, calling an actual API,
multi-step tasks that involve checking something and then acting on the result. It's
strictly more capable than the other two in what it can eventually answer correctly, but
that capability isn't free: more latency, more cost per question, and more moving parts
that can go wrong (a missing or broken tool, a bad decision about *when* to call a tool).
For a simple one-shot factual question, reaching for a full ReAct agent would be
overkill; for a question that genuinely depends on the current state of the world, it's
often the only one of the three that can actually get the right answer at all.
