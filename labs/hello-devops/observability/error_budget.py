"""Turn an SLO into an error budget and burn rates (Day 41).

Usage:   python3 error_budget.py SLO_PERCENT [DAYS] [REQUESTS_PER_DAY]
Example: python3 error_budget.py 99.9 30 200000
"""

import sys

slo = float(sys.argv[1]) / 100  # 99.9 -> 0.999
days = float(sys.argv[2]) if len(sys.argv) > 2 else 30
per_day = float(sys.argv[3]) if len(sys.argv) > 3 else 0

budget = 1 - slo  # the share of requests that may fail
minutes = days * 24 * 60

print(f"SLO {slo:.2%} over {days:g} days")
print(f"Error budget: {budget:.2%} of requests")
print(f"Full outage allowed: {budget * minutes:.1f} minutes")
if per_day:
    total = per_day * days
    print(f"Failed requests allowed: {budget * total:,.0f} of {total:,.0f}")

# Burn rate = how fast you spend the budget. 1 means "exactly on budget".
# 14.4 and 6 are the usual "page" and "ticket" thresholds (Day 44).
for burn, window_h in [(1, None), (6, 6), (14.4, 1)]:
    line = f"Burn rate {burn:>4}: error ratio {burn * budget:.2%}, budget gone in {days / burn:.1f} days"
    if window_h:
        used = burn * window_h / (days * 24)
        line += f" ({window_h} h at this rate uses {used:.0%} of it)"
    print(line)
