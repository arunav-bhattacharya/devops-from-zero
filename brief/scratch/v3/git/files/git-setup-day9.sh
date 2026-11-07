#!/usr/bin/env bash
# git-setup-day9.sh: settings for working with branches and a team (Day 9).
# Run it after git-setup.sh from Day 8.
set -euo pipefail

# git pull replays your unpushed commits on top, instead of making a merge commit.
git config --global pull.rebase true

# The first git push of a new branch also sets its upstream, no -u needed.
git config --global push.autoSetupRemote true

# Conflicts also show the common ancestor, between ||||||| and =======.
git config --global merge.conflictStyle zdiff3

# Remember how you resolved a conflict, and reuse it when the same one comes back.
git config --global rerere.enabled true

# Sign every commit and tag with your SSH key from Day 7 (needs Git 2.34 or later).
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgSign true

git config --global --list
