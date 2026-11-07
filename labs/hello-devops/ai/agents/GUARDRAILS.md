# Guardrails checklist for AI agents

Use it before you give an agent access to anything in hello-devops: the repository,
the cluster, Grafana or a cloud account (Day 66). Every line is something you can check.
The rule behind all of them: an agent gets the access its task needs and nothing more,
and you assume that one day it will be fooled.

## Identity and credentials

- [ ] The agent has its own identity, never yours: the `ai-agent` ServiceAccount
      (`policy/ai-agent-readonly.yaml`), a fine-grained GitHub token for one repository,
      a Grafana service account with the Viewer role, a read-only IAM role.
- [ ] Its credentials are short-lived. `security/agent-kubeconfig.sh 1h` writes a token
      that expires after an hour.
- [ ] Credentials live outside the repository and are passed to each server on its own,
      never exported for every program in your shell profile.
- [ ] You know the kill switch for each one: delete the ServiceAccount, revoke the token,
      remove the role.

## Access

- [ ] Read-only is set where it is enforced: RBAC, token scopes, IAM. A server's read-only
      flag (`read_only = true`, `--read-only`, `X-MCP-Readonly`) is a second lock, not the first.
- [ ] No Secrets, no `pods/exec`, no `nodes/proxy`, no wildcards (`*`).
      Check with `kubectl auth can-i --list --as=system:serviceaccount:hello:ai-agent`.
- [ ] Changes go one way only: the agent opens a pull request; CI, policies and a person
      check it; Argo CD applies it from git. The agent never needs write access to the cluster.

## MCP servers and tools

- [ ] Each server comes from a publisher you can identify, under the exact name its docs use.
      In the MCP Registry, a name such as `io.github.github/github-mcp-server` is tied to the
      publisher's verified namespace.
- [ ] Each version is pinned (`kubernetes-mcp-server@0.1.2`, an image digest), and the config
      (`ai/agents/.mcp.json`) is in git, so changes are reviewed.
- [ ] Only the toolsets the task needs are on.
- [ ] You have read each server's tool list once, for example with the MCP Inspector.
- [ ] Third-party local servers run in a container with no home folder mounted and only the
      network they need.

## Untrusted input

- [ ] An agent that reads text from other people (issues, pull requests, logs, web pages,
      tool results) has no write access and no secrets it could send out.
- [ ] No session has all three: private data, untrusted content, and a way to send data out.
- [ ] Content filters such as the GitHub server's lockdown mode are extra help, not a boundary.

## CI

- [ ] AI workflows start from a person (a label, `workflow_dispatch`), never on their own for
      every push, and never with `pull_request_target` running pull request code.
- [ ] Every job declares `permissions:`. The job that runs the model has `contents: read` only.
      A separate job posts results (`ai/agents/ai-review.yml`).
- [ ] Third-party actions are pinned to a full commit SHA, and every job has `timeout-minutes`.
- [ ] The AI review is advisory. Branch protection still needs a human approval and green CI.

## Approval, audit and cost

- [ ] A person approves every write: merge, `terraform apply`, rollback, restart.
- [ ] You can see what the agent did afterwards: the agent's transcript, the GitHub audit log,
      Kubernetes audit logs or CloudTrail.
- [ ] No secrets or customer data go into prompts. Use only tools your company has approved.
- [ ] The API key has a spending limit, and long runs have a timeout.
