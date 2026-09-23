"""
questions.py

My scenario: a "Weekend Trip Planning Assistant" -- someone getting
ready for a short trip to Tokyo and asking a mix of questions.

Q1 and Q2 need an external/live tool (current weather, current
exchange rate) -- the model cannot know these on its own.
Q3 and Q4 are pure reasoning/arithmetic word problems -- everything
needed is already in the question, no tool required.
Q5 is another tool question (weekend forecast).

Q3 (the train ticket question) is the one I used for the
self-consistency run in self_consistency.py.
"""

QUESTIONS = {
    "weather_tokyo": "What's the current temperature in Tokyo right now, and should I pack a jacket for my trip there tomorrow?",
    "currency_jpy": "I have 200 US dollars. Using today's exchange rate, roughly how many Japanese Yen will I get?",
    "train_tickets": "A train ticket costs $45. I need to buy tickets for 3 people, and there's a 10% group discount applied to the total. How much will I pay in total?",
    "airport_time": "My flight departs at 14:30 and boarding closes 45 minutes before departure. I need 90 minutes before boarding closes for security and check-in. What is the latest time I should arrive at the airport?",
    "weekend_umbrella": "What's the weather forecast for Tokyo this weekend -- do I need to pack an umbrella?",
}
