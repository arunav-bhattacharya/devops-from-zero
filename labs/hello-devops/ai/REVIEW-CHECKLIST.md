# Review checklist for AI-written changes

Use it for every pull request an assistant or agent wrote, or helped write (Day 65).
Review it like a teammate's pull request, with one extra suspicion: the code can look
finished and still use a flag, field, package or version that does not exist.

## Before you read the code

- [ ] The pull request says what was asked, and which tool wrote the change.
- [ ] The diff is small enough to read in one sitting. If it is not, ask for smaller steps.
- [ ] `ai/check.sh` passes on your laptop, and CI is green.

## Does it do the right thing?

- [ ] It changes only what was asked: no unrelated rewrites, renames or reformatting.
- [ ] Every version, flag, field and API exists. You checked the ones you did not know
      with `--help`, `kubectl explain`, a validator or the official docs.
- [ ] Settings match this repository: port 8000, `/healthz` and `/readyz`, env vars
      `APP_VERSION`, `GREETING`, `REDIS_HOST` and `PORT`.
- [ ] Labels and selectors match, names match the existing files, and paths exist.

## Supply chain

- [ ] No new dependency without a reason in the description.
- [ ] Each new package exists on its registry under that exact name, from the publisher you
      expect, with a real history. AI tools invent package names, and attackers register
      them (slopsquatting).
- [ ] Versions are pinned like the rest: images by tag (no `:latest`), third-party actions by
      full commit SHA, Python packages in `requirements.txt`.

## Safety

- [ ] No secrets, tokens, internal hostnames or customer data in code, tests, logs or comments.
- [ ] No safety removed: `permissions:` blocks, `set -euo pipefail`, probes, resource
      requests, policies, pins.
- [ ] No new escape hatches: `|| true`, `--no-verify`, `--force`, `continue-on-error`,
      skipped tests.
- [ ] No wider access: RBAC verbs, `*`, `cluster-admin`, `write-all`, `pull_request_target`,
      IAM actions.

## Tests

- [ ] New behaviour has a test, and you saw that test fail without the change.
- [ ] No test was deleted, skipped or weakened (for example `assert True`).

## You

- [ ] You can explain every line to a teammate. If you cannot, ask the tool why, check the
      answer, or rewrite that part yourself.
