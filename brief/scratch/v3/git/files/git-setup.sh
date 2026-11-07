#!/usr/bin/env bash
# git-setup.sh: one-time git settings for your Mac (Day 8).
# Put your own name and email in first. Use an email your GitHub account has verified.
set -euo pipefail

git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# New repositories start on a branch called main, not master.
git config --global init.defaultBranch main

# The editor git opens for commit messages. --wait makes git wait until you close the tab.
git config --global core.editor "code --wait"

# Short names for commands you type all day.
git config --global alias.st "status --short --branch"
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.last "log -1 --stat"
git config --global alias.unstage "restore --staged"

# Show what you just set, and where it lives.
git config --global --list --show-origin
