import json


with open("data_rated.json", 'r', encoding='utf-8') as file:
    data = json.load(file)

# Weights (Wiegers' defaults; adjust to your project).
# Set W_RISK = 0 to drop risk from the model entirely.
W_BENEFIT = 2
W_PENALTY = 1
W_COST = 1
W_RISK = 0.5


def prioritize(features):
    """Return features with Wiegers priority scores, sorted high to low.

    priority = value% / (cost% * W_COST + risk% * W_RISK)
    where each '%' is that feature's share of its column total.
    """
    # Step 1: total value per feature = weighted benefit + weighted penalty.
    for f in features:
        f["total_value"] = f["Benefit"] * W_BENEFIT + f["Penalty"] * W_PENALTY

    # Step 2: column totals (needed before any share can be computed).
    value_total = sum(f["total_value"] for f in features)
    cost_total = sum(f["Cost"] for f in features)
    risk_total = sum(f["Risk"] for f in features)

    # Step 3: per-feature shares (%) and the final priority.
    for f in features:
        f["value_pct"] = f["total_value"] / value_total * 100
        f["cost_pct"] = f["Cost"] / cost_total * 100
        f["risk_pct"] = f["Risk"] / risk_total * 100

        denominator = f["cost_pct"] * W_COST + f["risk_pct"] * W_RISK
        # Guard against a zero denominator (e.g. cost=risk=0 or both weights 0).
        f["priority"] = f["value_pct"] / denominator

    # Step 4: sort descending — best value-for-burden first.
    return sorted(features, key=lambda f: f["priority"], reverse=True)


ranked = prioritize(data)

# Print a readable table.
header = f"{'Rank':<5}{'ID':<4}{'Value%':>8}{'Cost%':>8}{'Risk%':>8}{'Priority':>10}  Description"
print(header)
print("-" * len(header))
for rank, f in enumerate(ranked, start=1):
    desc = f.get("description", "")
    if len(desc) > 50:
        desc = desc[:47] + "..."
    print(
        f"{rank:<5}{f['id']:<4}"
        f"{f['value_pct']:>8.1f}{f['cost_pct']:>8.1f}{f['risk_pct']:>8.1f}"
        f"{f['priority']:>10.3f}  {desc}"
    )

# Optionally write the enriched, ranked data back out.
with open("prioritized2.json", "w", encoding="utf-8") as out:
    json.dump(ranked, out, indent=2, ensure_ascii=False)