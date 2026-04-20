# buggy_agent.py
def calculate_token_cost(tokens, model):
    rates = {
        "gpt-5.4": 0.015,
        "claude-sonnet-4-6": 0.003,
        "gemini-3.1-pro": 0.0025
    }
    cost = tokens * rates[model] # Bug: KeyError on unknown model
    return cost

results = []
for model in ["gpt-5.4", "claude-sonnet-4-6", "gemini-ultra"]:
    cost = calculate_token_cost(1000, model)
    results.append(cost)

print(f"Total cost: ${sum(results):.4f}")