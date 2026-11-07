# labs/git: practice repositories for Part 2 (Days 8 and 9)

Two scripts that build throwaway git repositories, so you can explore history and
break things without touching real work. Everything in them is fake: the people
(Ana Silva and Ben Okafor), the `example.com` emails and the "token" in `.env`.

| Script | What it makes | Used on |
|---|---|---|
| `make-practice-repo.sh [folder]` | A small Python project, `price-tool`, with 8 commits by two people, a branch `currency-first` that conflicts with `main`, and two ignored files (`debug.log`, `.env`). Default folder: `~/code/git-practice`. | Day 8 (explore, undo, reflog), Day 9 worked example (merge conflict) |
| `make-team-scenario.sh [folder]` | A pretend team: `origin.git` (a bare repository that plays GitHub), `ana/` and `ben/`. Ben has pushed a branch `json-logs`; Ana has since pushed a change to `main` next to Ben's lines. Default folder: `~/code/git-team`. | Day 9 hands-on (fetch, rebase, conflict, interactive rebase, safe force push, tags) |

## Get the scripts

If you cloned the course repo on Day 3, update it. Otherwise clone it once:

```bash
git -C ~/code/devops-from-zero pull
# or, the first time:
git clone --depth 1 https://github.com/arunav-bhattacharya/devops-from-zero ~/code/devops-from-zero
```

## Run them

```bash
bash ~/code/devops-from-zero/labs/git/make-practice-repo.sh
cd ~/code/git-practice
git log --oneline --graph --all
```

```bash
bash ~/code/devops-from-zero/labs/git/make-team-scenario.sh
cd ~/code/git-team/ben
git log --oneline --graph --all
```

Pass a folder to make a second copy, for example
`bash make-practice-repo.sh ~/code/git-merge-demo`. A script refuses to touch a folder
that already exists.

## Same commit IDs as the lessons

The scripts fix every name, email and date, and they ignore your global git settings
while they run (`GIT_CONFIG_GLOBAL=/dev/null`). So the commits they make have the same
IDs on your Mac as in the lessons, for example `d6aad6e Group thousands in prices`.
Commits you make yourself afterwards use your own name and the current time, so their
IDs will differ from the ones printed in the lessons.

They need bash and git 2.32 or later (for `GIT_CONFIG_GLOBAL`). They were tested with
git 2.43, 2.54 and 2.56, with bash 3.2 (the version macOS ships) and bash 5.

## Start again

Broke it beyond repair? That is the point. Delete the folder and run the script again:

```bash
rm -rf ~/code/git-practice
bash ~/code/devops-from-zero/labs/git/make-practice-repo.sh
```
