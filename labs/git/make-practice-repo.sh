#!/usr/bin/env bash
# make-practice-repo.sh: build a small git repository with some history,
# so you can explore it and break it safely (Day 8, and the Day 9 worked example).
#
# Usage:  bash make-practice-repo.sh [folder]
#         The folder defaults to ~/code/git-practice and must not exist yet.
#
# The script makes the same commits, with the same commit IDs, on every
# machine: the names, emails and dates are fixed, and your own git settings
# are ignored while it runs. Commits you make later use your normal settings.
set -euo pipefail

dest="${1:-$HOME/code/git-practice}"
if [ -e "$dest" ]; then
  echo "make-practice-repo: $dest already exists." >&2
  echo "Delete it first (rm -rf \"$dest\") or pass another folder." >&2
  exit 1
fi

# Ignore your global and system git config while building, so the result
# is identical everywhere. This only applies inside this script.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

# commit_as NAME EMAIL DATE MESSAGE: commit what is staged, as that person.
commit_as() {
  GIT_AUTHOR_NAME="$1" GIT_AUTHOR_EMAIL="$2" GIT_AUTHOR_DATE="$3" \
    GIT_COMMITTER_NAME="$1" GIT_COMMITTER_EMAIL="$2" GIT_COMMITTER_DATE="$3" \
    git commit --quiet -m "$4"
}
ana() { commit_as "Ana Silva" "ana@example.com" "$@"; }
ben() { commit_as "Ben Okafor" "ben@example.com" "$@"; }

mkdir -p "$(dirname "$dest")"
git init --quiet -b main "$dest"
cd "$dest"

# 1. A README.
cat > README.md <<'EOF'
# price-tool

A tiny price calculator. It exists so you can practise git on it.
EOF
git add README.md
ana "2026-10-05T09:14:00+02:00" "Add a README"

# 2. The calculator itself.
cat > price.py <<'EOF'
"""Add tax to a net price and print the result."""

TAX_RATE = 0.20
CURRENCY = "EUR"


def total(net):
    return round(net * (1 + TAX_RATE), 2)


def label(net):
    return f"{total(net):.2f} {CURRENCY}"


if __name__ == "__main__":
    print(label(10))
EOF
git add price.py
ana "2026-10-05T10:02:00+02:00" "Add the price calculator"

# 3. Files git should never track.
cat > .gitignore <<'EOF'
# Logs, local settings and build output never go into git
*.log
.env
build/
__pycache__/
EOF
git add .gitignore
ben "2026-10-05T16:40:00+02:00" "Ignore logs, local settings and build output"

# 4. A new function between total() and label().
cat > price.py <<'EOF'
"""Add tax to a net price and print the result."""

TAX_RATE = 0.20
CURRENCY = "EUR"


def total(net):
    return round(net * (1 + TAX_RATE), 2)


def discounted(net, percent):
    return total(net * (1 - percent / 100))


def label(net):
    return f"{total(net):.2f} {CURRENCY}"


if __name__ == "__main__":
    print(label(10))
EOF
git add price.py
ana "2026-10-06T11:25:00+02:00" "Add a discount function"

# 5. A change you will revert on Day 8.
cat > price.py <<'EOF'
"""Add tax to a net price and print the result."""

TAX_RATE = 0.25
CURRENCY = "EUR"


def total(net):
    return round(net * (1 + TAX_RATE), 2)


def discounted(net, percent):
    return total(net * (1 - percent / 100))


def label(net):
    return f"{total(net):.2f} {CURRENCY}"


if __name__ == "__main__":
    print(label(10))
EOF
git add price.py
ben "2026-10-07T09:50:00+02:00" "Raise the tax rate to 25%"

# 6. README: how to run it.
cat > README.md <<'EOF'
# price-tool

A tiny price calculator. It exists so you can practise git on it.

Run it with `python3 price.py`. It prints the price of a 10 EUR item, tax included.
EOF
git add README.md
ana "2026-10-07T14:05:00+02:00" "Explain how to run the calculator"

# 7. Ben's branch: currency first. It changes the same line as commit 8.
git switch --quiet -c currency-first
cat > price.py <<'EOF'
"""Add tax to a net price and print the result."""

TAX_RATE = 0.25
CURRENCY = "EUR"


def total(net):
    return round(net * (1 + TAX_RATE), 2)


def discounted(net, percent):
    return total(net * (1 - percent / 100))


def label(net):
    return f"{CURRENCY} {total(net):.2f}"


if __name__ == "__main__":
    print(label(10))
EOF
git add price.py
ben "2026-10-08T10:30:00+02:00" "Show the currency before the amount"

# 8. Meanwhile on main: group thousands with commas.
git switch --quiet main
cat > price.py <<'EOF'
"""Add tax to a net price and print the result."""

TAX_RATE = 0.25
CURRENCY = "EUR"


def total(net):
    return round(net * (1 + TAX_RATE), 2)


def discounted(net, percent):
    return total(net * (1 - percent / 100))


def label(net):
    return f"{total(net):,.2f} {CURRENCY}"


if __name__ == "__main__":
    print(label(1234.5))
EOF
git add price.py
ana "2026-10-08T15:45:00+02:00" "Group thousands in prices"

# Two files that .gitignore keeps out of git. They exist, but git status ignores them.
printf '%s\n' "2026-10-08 15:50:01 INFO price-tool started" "2026-10-08 15:50:02 INFO label=1,543.12 EUR" > debug.log
printf '%s\n' "# Local settings. Never commit this file." "PRICE_API_TOKEN=not-a-real-token" > .env

echo "Made a practice repo in $dest:"
echo "  8 commits: 7 on main, 1 more on the branch currency-first."
echo "Next:  cd \"$dest\" && git log --oneline --graph --all"
