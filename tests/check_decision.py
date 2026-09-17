from src.decision import make_decision


ticket = "My ₹3,500 order arrived damaged yesterday."

decision = make_decision(ticket)

print("\nACTION:", decision.action)
print("CONFIDENCE:", decision.confidence)
print("REASON:", decision.reason)
print("SOURCES:", decision.sources)