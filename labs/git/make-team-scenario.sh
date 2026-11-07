#!/usr/bin/env bash
# make-team-scenario.sh: a pretend team on your laptop (Day 9).
#
# Usage:  bash make-team-scenario.sh [folder]
#         The folder defaults to ~/code/git-team and must not exist yet.
#
# It creates three repositories side by side:
#   origin.git  a bare repository that plays the part of GitHub
#   ana/        Ana's repository. She started the project and commits as "Ana Silva".
#   ben/        Ben's clone. He commits as "Ben Okafor". You play Ben.
#
# The story so far: Ben pushed his branch json-logs. Then Ana pushed a change
# to main that touches the lines next to Ben's change. Ben has not fetched
# since, so his clone does not know about Ana's commit yet.
set -euo pipefail

dest="${1:-$HOME/code/git-team}"
if [ -e "$dest" ]; then
  echo "make-team-scenario: $dest already exists." >&2
  echo "Delete it first (rm -rf \"$dest\") or pass another folder." >&2
  exit 1
fi

# Ignore your global and system git config while building, so the commit IDs
# are the same on every machine. This only applies inside this script.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

# commit_as NAME EMAIL DATE MESSAGE: commit what is staged, as that person.
commit_as() {
  GIT_AUTHOR_NAME="$1" GIT_AUTHOR_EMAIL="$2" GIT_AUTHOR_DATE="$3" \
    GIT_COMMITTER_NAME="$1" GIT_COMMITTER_EMAIL="$2" GIT_COMMITTER_DATE="$3" \
    git commit --quiet -m "$4"
}
ana() { commit_as "Ana Silva" "ana@example.com" "$@"; }
ben() { commit_as "Ben Okafor" "ben@example.com" "$@"; }

mkdir -p "$dest"
cd "$dest"

# The shared "remote". Bare means it has no working tree, only the .git data.
git init --quiet --bare -b main origin.git

# Ana starts the project on her laptop, then pushes main to the remote.
git init --quiet -b main ana
cd ana
git remote add origin ../origin.git
cat > README.md <<'EOF'
# checkout-config

Settings for the checkout service. Change them on a branch, never on main.
EOF
cat > service.ini <<'EOF'
# Settings for the checkout service
[server]
port = 8000
workers = 2

[logging]
level = info
format = text
EOF
git add README.md service.ini
ana "2026-10-12T09:05:00+02:00" "Add the service settings"
cat > service.ini <<'EOF'
# Settings for the checkout service
[server]
port = 8000
workers = 4

[logging]
level = info
format = text
EOF
git add service.ini
ana "2026-10-12T11:30:00+02:00" "Use four workers"
git push --quiet -u origin main 2> /dev/null
cd ..

# Ben clones, starts a branch, and pushes it with three commits.
git clone --quiet origin.git ben
cd ben
git switch --quiet -c json-logs
cat > service.ini <<'EOF'
# Settings for the checkout service
[server]
port = 8000
workers = 4

[logging]
level = info
format = json
EOF
git add service.ini
ben "2026-10-13T10:10:00+02:00" "Write logs as JSON"
cat >> README.md <<'EOF'

TODO Ben: say which fields the JSON logs have
EOF
git add README.md
ben "2026-10-13T10:40:00+02:00" "wip"
cat > README.md <<'EOF'
# checkout-config

Settings for the checkout service. Change them on a branch, never on main.

Logs are JSON, one object per line, with the fields time, level and msg.
EOF
git add README.md
ben "2026-10-13T11:15:00+02:00" "Describe the JSON log fields"
git push --quiet -u origin json-logs 2> /dev/null
cd ..

# Ana changes the logging level on main and pushes. Ben has not fetched yet.
cd ana
cat > service.ini <<'EOF'
# Settings for the checkout service
[server]
port = 8000
workers = 4

[logging]
level = warning
format = text
EOF
git add service.ini
ana "2026-10-13T14:20:00+02:00" "Log only warnings and errors"
git push --quiet 2> /dev/null
cd ..

# From now on, each repository commits under its owner's name (local config).
git -C ana config user.name "Ana Silva"
git -C ana config user.email "ana@example.com"
git -C ben config user.name "Ben Okafor"
git -C ben config user.email "ben@example.com"

echo "Made a team scenario in $dest:"
echo "  origin.git  the shared remote (plays GitHub)"
echo "  ana/        Ana's repository, on main"
echo "  ben/        Ben's clone, on json-logs. You play Ben."
echo "Next:  cd \"$dest/ben\" && git log --oneline --graph --all"
