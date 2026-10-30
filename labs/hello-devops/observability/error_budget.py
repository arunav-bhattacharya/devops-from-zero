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

# Burn rate = how fast you spend the budget. 1 means "used up exactly at the end".
# The three rows are the starting points from Google's SRE Workbook (Day 44):
# page at 14.4 over 1 hour or 6 over 6 hours, open a ticket at 1 over 3 days.
for burn, window_h, action in [(14.4, 1, "page"), (6, 6, "page"), (1, 72, "ticket")]:
    used = burn * window_h / (days * 24)
    print(
        f"Burn rate {burn:>4}: error ratio {burn * budget:.2%}, budget gone in {days / burn:.1f} days;"
        f" {window_h} h of this uses {used:.0%} ({action})"
    )
