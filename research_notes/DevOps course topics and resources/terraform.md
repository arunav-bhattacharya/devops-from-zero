# Terraform and OpenTofu for beginners (as of 30 October 2026): research notes for 5 lessons

How things were checked (read this first):
- **Run locally.** Every plan, console, test and error output quoted below came from running **Terraform v1.17.1** (the binary in this sandbox, linux_amd64) on 2026-10-30. Providers were hashicorp/random 3.9.1, hashicorp/local 2.9.1 and hashicorp/null 3.3.2, downloaded from releases.hashicorp.com. kreuzwerker/docker 4.6.0 came from its GitHub release, and a real Docker 29.9.2 daemon was used. These are marked **(verified locally)**. On a Mac the output is the same apart from file paths, ids and generated pet names.
- **Read from the source repos.** HashiCorp's docs were read from the `hashicorp/web-unified-docs` GitHub repo, which holds the source of developer.hashicorp.com (folder `content/terraform/v1.17.x`). OpenTofu's docs were read from `opentofu/opentofu/website/docs`. Changelogs were read from raw.githubusercontent.com. The links point to the GitHub file that was opened.
- **Public doc URLs that were not opened.** Where a public developer.hashicorp.com or opentofu.org page is named but not linked, the path comes from the internal links inside the opened source files. Those pages were not opened. They are marked "(public path, derived)".
- **Blocked sites.** developer.hashicorp.com, opentofu.org, youtube.com, freecodecamp.org and dev.to could not be fetched in this sandbox. registry.terraform.io and registry.opentofu.org were blocked too. URLs from those hosts are listed only when they appeared in search results, and they are marked "(search result)".

---

## Key question 1: What intuitions help a beginner? (desired state vs current state vs real world; the dependency graph; state as Terraform's memory)

### Takeaway
Teach Terraform as a three-way reconciliation loop. Your **config** is the desired state, the **state file** is Terraform's memory of what it built, and the **real world** is what actually exists. `plan` refreshes memory from the real world, diffs it against the config, and orders the actions with a dependency graph. Every later topic hangs off this picture: drift, `moved`, `import`, `count` vs `for_each`, and remote state.

### Cited Findings
- **It is declarative.** Brikman's *Terraform: Up & Running* (3rd ed.) puts it this way: Terraform is declarative, so it has no traditional loops or if-statements. It offers `count`, `for_each`, `for` expressions, the ternary operator and functions instead. Chapter 5 is "Terraform Tips and Tricks: Loops, If-Statements, Deployment, and Gotchas" — [O'Reilly ch. 5 (search result)](https://www.oreilly.com/library/view/terraform-up-and/9781098116736/ch05.html); [Gruntwork blog version (search result)](https://www.gruntwork.io/blog/terraform-tips-tricks-loops-if-statements-and-gotchas)
- **Three-way comparison, shown live.** A local file managed by `local_file` was deleted by hand. `terraform plan -refresh-only` then printed "Note: Objects have changed outside of Terraform … `# local_file.by_each["bravo"] has been deleted`". It added: "This is a refresh-only plan, so Terraform will not take any actions to undo these. If you were expecting these changes then you can apply this plan to record the updated values in the Terraform state without changing any remote objects." A normal `plan` instead proposed `# local_file.by_each["bravo"] will be created` / `Plan: 1 to add, 0 to change, 0 to destroy.` (verified locally)
- **State is the memory that maps addresses to real objects.** The JSON state file had these top-level keys: `version: 4`, `terraform_version: "1.17.1"`, `serial`, `lineage` (a UUID), `outputs`, `resources`, `check_results`. Each resource has `mode` (`managed`), `type`, `name` and `provider`. Each instance has `index_key`, `schema_version`, `attributes`, `sensitive_attributes`, `identity_schema_version` and `dependencies`. (verified locally)
- **Renaming without telling Terraform loses the memory link.** Renaming `random_pet.server` to `random_pet.name` with no `moved` block gave `# random_pet.server will be destroyed (because random_pet.server is not in configuration)` plus `# random_pet.name will be created`. Three dependent files were marked "must be replaced": `Plan: 4 to add, 0 to change, 4 to destroy.` Adding a `moved {}` block turned this into `# random_pet.server has moved to random_pet.name` with no changes. (verified locally)
- **The dependency graph comes from references.** `terraform graph -format=mermaid` (new in Terraform 1.16) printed `local_file.by_count --> random_pet.name`, because the file's content refers to the pet id. Resources with no references between them got no edges, so Terraform can create them in parallel. (verified locally); the Mermaid flag is in the [Terraform v1.16 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md)
- **Unknown values are part of the model.** Attributes that are computed by the provider show as `(known after apply)` in plans. One example: `docker_container.web` `image = (known after apply)` while the image resource is also being created. (verified locally)
- **`count` and `for_each` values must be known at plan time.** The docs say: "the `count` value must be known before Terraform performs any remote resource operations." For `for_each`, if keys are unknown, Terraform errors that `for_each` "has dependencies that cannot be determined before apply" — [count.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/count.mdx), [for_each.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/for_each.mdx)

### Inferences
- **Analogies for software engineers:** the plan is like a `git diff` of infrastructure, or React's virtual-DOM reconcile. The state file is like a database index from logical names (`aws_s3_bucket.logs`) to physical ids (`my-logs-8f3a`). The graph is a build system's DAG (make or Bazel).
- **A lesson framing that works:** "Terraform never looks at your cloud console. It looks at (1) your .tf files, (2) its memory, and (3) whatever the provider API reports during refresh." Drift, `import`, `moved`, `state rm` and `-refresh-only` each move one side of that triangle.
- The "address" idea (`TYPE.NAME`, `TYPE.NAME[0]`, `TYPE.NAME["key"]`, `module.X.TYPE.NAME`) deserves its own slide. Most state surgery and most count/for_each confusion is about addresses.

### Gaps
- No official HashiCorp diagram of the "three-way" model could be opened (developer.hashicorp.com is blocked). The framing above is a synthesis.

---

## Key question 2: What do beginners get wrong?

### Takeaway
The classic mistakes are still the same: `count` index shifting, committing state or tfvars secrets, believing `sensitive = true` keeps secrets out of state, one giant root module per company, routine use of `-target`, and unpinned provider or module versions. Some newer ones: misusing ephemeral values, assuming `terraform import` or `import` blocks write matching config, and CI actions pinned to mutable tags (the Trivy incident of March 2026).

### Cited Findings
- **Count index shifting.** With `count = length(var.names)` over `["alpha","bravo","charlie"]`, removing `"alpha"` gave `local_file.by_count[0] must be replaced`, `local_file.by_count[1] must be replaced` (content `# forces replacement`), and `local_file.by_count[2] will be destroyed (because index [2] is out of range for count)`. The same change with `for_each = toset(var.names)` destroyed only `local_file.by_each["alpha"] (because key ["alpha"] is not in for_each map)`. Combined summary: `Plan: 2 to add, 0 to change, 4 to destroy.` (verified locally)
- **The docs' rule of thumb:** "Use the `count` argument when you want to create nearly identical instances. Use `for_each` when some instance arguments must have distinct values that can't be directly derived from an integer" — [count.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/count.mdx). The style guide also says "Use `count` and `for_each` sparingly" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
- **Committing state.** The style guide's "Do not commit" list: `terraform.tfstate` and `terraform.tfstate.*` backups ("can contain secrets … version control systems do not support locking"), `.terraform.tfstate.lock.info`, the `.terraform` directory, saved plan files from `-out`, and "Any `.tfvars` files that contain sensitive information". Its "Always commit" list: all code, the `.terraform.lock.hcl` dependency lock file, `.gitignore`, and README. It points to [GitHub's Terraform.gitignore](https://github.com/github/gitignore/blob/main/Terraform.gitignore) — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
- **`sensitive` only hides values; it does not keep them out of state.** "Remember that Terraform will still store this value in plain text in its state, but it will not display it when you run `terraform plan` or `terraform apply`" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx). "If you add secret values directly to your configuration, Terraform stores those secrets in its state and plan files" — [manage-sensitive-data/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/index.mdx)
- **`-target` habits.** "Use `-target=ADDRESS` in exceptional circumstances only, such as recovering from mistakes or working around Terraform limitations … it is _not recommended_ to use `-target` for routine operations, since this can lead to undetected configuration drift … prefer instead to break large configurations into several smaller configurations that can each be independently applied" — [plan.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/commands/plan.mdx). OpenTofu added `-exclude` (1.9), plus `-target-file` and `-exclude-file` (1.10), as alternatives — [OpenTofu v1.9 CHANGELOG](https://github.com/opentofu/opentofu/blob/v1.9/CHANGELOG.md), [v1.10 CHANGELOG](https://github.com/opentofu/opentofu/blob/v1.10/CHANGELOG.md)
- **Giant root modules and workspaces as environments.** "Workspaces alone are not a suitable tool for system decomposition because each subsystem should have its own separate configuration and backend." For dev, stage and prod with different credentials, "CLI workspaces within a working directory use the same backend, so they are not a suitable isolation mechanism." Use reusable modules plus a separate root configuration per environment instead — [cli/workspaces/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/workspaces/index.mdx)
- **Version pinning.** "Pin your Terraform, provider, and module versions"; "To prevent provider and module upgrades from introducing unintentional changes to your infrastructure, use version pinning"; "Pin modules to a specific major and minor version" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
- **Lock-file platform gotcha.** When providers were installed from a filesystem mirror, `terraform init` warned: "The current .terraform.lock.hcl file only includes checksums for linux_amd64, so Terraform running on another platform will fail to install these providers. To calculate additional checksums for another platform, run: terraform providers lock -platform=linux_amd64". (verified locally)
- **Imports don't write matching config for you.** An `import` block for `random_string.legacy` (id `abc123`) with config `special = false` produced `# random_string.legacy must be replaced`, `# (imported from "abc123")`, `# Warning: this will destroy the imported resource`, `~ special = true -> false # forces replacement`, `Plan: 1 to import, 3 to add, 0 to change, 1 to destroy.` After changing config to `special = true`: `# random_string.legacy will be imported`, `Plan: 1 to import, 2 to add, 0 to change, 0 to destroy.` (verified locally)
- **`state rm` makes Terraform forget, it doesn't delete.** `terraform state rm 'local_file.by_each["alpha2"]'` printed `Successfully removed 1 resource instance(s).` The next plan proposed creating the file again (`# local_file.by_each["alpha"] will be created`) even though the real file still existed on disk. (verified locally)
- **Ephemeral misuse is a hard error.** Putting `ephemeral.random_password.db.result` into `local_file.content` gave: "Error: Invalid use of ephemeral value … Ephemeral values are not valid for "content", because it is not a write-only attribute and must be persisted to state." (verified locally)
- **Brikman's gotchas list** (3rd ed.): "count and for_each have limitations; Zero-Downtime Deployment has limitations; Valid Plans Can Fail" — [O'Reilly ch. 5 (search result)](https://www.oreilly.com/library/view/terraform-up-and/9781098116736/ch05.html)
- **CI supply chain.** On 19 March 2026, attackers force-pushed malicious code to most version tags of `aquasecurity/trivy-action`, tracked as CVE-2026-33634. The write-ups recommend pinning actions to full commit SHAs and rotating any secrets those runs could reach. Sources disagree on tag counts (75 of 76 vs others) and on the exposure window — [Snyk (search result)](https://snyk.io/articles/trivy-github-actions-supply-chain-compromise/), [Wiz CVE entry (search result)](https://www.wiz.io/vulnerability-database/cve/cve-2026-33634), [BoostSecurity IR guide (search result)](https://labs.boostsecurity.io/tactical-guides/2026-03-aquasecurity-trivy-supply-chain-compromise-incident-response-guide)

### Inferences
- Make the count-shift lab the "aha" of lesson 2. The real output above is short enough to show on one slide.
- Hard-coded secrets: teach in this order. (1) Never put secrets in `.tf` or committed `.tfvars`. (2) `sensitive = true` hides them from output only. (3) Ephemeral values and write-only args keep them out of state where providers support it (TF ≥1.11). (4) Use OIDC or SSO instead of long-lived keys.
- The mirror lock-file warning matters for Mac (darwin_arm64) laptops plus Linux CI. Telling learners to run `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64` is cheap insurance. That exact command was not run here; the flag form comes from the warning text.

### Gaps
- Not verified this session: whether a normal registry install, as opposed to a filesystem mirror, records hashes for all platforms. Reportedly it does, via `zh:` hashes, but test it on a Mac before teaching it as a fact.

---

## Key question 3: What is current (October 2026)? Terraform 1.17, OpenTofu 1.13, HCP Terraform free tier, S3 locking

### Takeaway
Current versions: Terraform **1.17.1** (released 28 Oct 2026; 1.17.0 on 21 Oct 2026) and OpenTofu **1.13.5** (tag dated 29 Oct 2026; 1.13.0 tag dated 30 Sep 2026). S3 native locking (`use_lockfile = true`) is the default recommendation, and DynamoDB locking is deprecated. Ephemeral values and write-only arguments, `import` blocks with identity, `terraform test` with mocks, and provider-defined functions are mature and worth teaching. Stacks, Terraform Policy, actions and `terraform query` are real but optional for beginners. HCP Terraform still has a Free plan capped at 500 managed resources. The legacy free plan ended on 31 March 2026, according to third-party reports.

### Cited Findings
**Terraform release timeline**, all from the official CHANGELOGs on GitHub:
- **1.17.1** — 28 Oct 2026, bug fixes. **1.17.0** — 21 Oct 2026, with these new features:
  - "variables and locals in provider requirements"
  - a `-minimal-refresh` planning option that "will only refresh resources that have proposed changes"
  - "Terraform Policy is now generally available. The `-policies` flag for `plan`, `apply`, and `query` no longer requires an experimental build", with docs at [developer.hashicorp.com/terraform/policy](https://developer.hashicorp.com/terraform/policy)
  - mock_provider support for ephemeral resources in tests
  - `log`/`pow` now error on infinite results
  - `show` reads variable values from a plan file

  Source: [Terraform v1.17 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.17/CHANGELOG.md); also mirrored at [newreleases.io (search result)](https://newreleases.io/project/github/hashicorp/terraform/release/v1.17.0)
- **1.18.0** is unreleased. Its alpha-only experiments: "deferred actions" (`-allow-deferral`, which lets `count`/`for_each` have unknown values), `terraform test cleanup`, test `backend` blocks and `skip_cleanup` — [Terraform main CHANGELOG](https://github.com/hashicorp/terraform/blob/main/CHANGELOG.md)
- **1.16.0** — 26 Aug 2026:
  - `import` blocks inside modules
  - `terraform_data` gets a `store` block for ephemeral or sensitive values
  - `lifecycle { destroy = false }`
  - `terraform console -scope=<module address>`
  - `terraform graph -format=mermaid`
  - `state show -json`
  - `contains()` can test for null
  - actions with `before_destroy`/`after_destroy`

  Source: [v1.16 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md)
- **1.15.0** — 29 Apr 2026:
  - `deprecated` attribute on variable and output blocks
  - S3 backend auth via `aws login`
  - `validate` checks the backend block
  - `convert` function
  - "variables and locals in module source and version attributes"
  - output blocks may declare type constraints
  - Windows ARM64 builds

  Source: [v1.15 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md)
- **1.14.0** — 19 Nov 2025:
  - list resources in `*.tfquery.hcl` files, plus the new `terraform query` command (can generate import config)
  - a top-level `action` block for provider-defined imperative side effects (e.g. `aws_lambda_invoke`), triggered by resource lifecycle or `-invoke`

  Source: [v1.14 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.14/CHANGELOG.md)
- **1.13.0** — 20 Aug 2025: a `terraform stacks` CLI command, and test improvements — [v1.13 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.13/CHANGELOG.md)
- **1.12.0** — 14 May 2025: `import` blocks can use a resource `identity` instead of `id`, and `terraform test -parallelism` — [v1.12 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.12/CHANGELOG.md)
- **1.11.0** — 27 Feb 2025:
  - "Add write-only attributes to resources … They are not persisted in state"
  - "S3 native state locking is now generally available. The `use_lockfile` argument … we've deprecated the DynamoDB-related arguments"
  - `terraform test -junit-xml` GA

  Source: [v1.11 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.11/CHANGELOG.md)
- **1.10.0** — 27 Nov 2024:
  - ephemeral resources and ephemeral input variables and outputs ("not persisted to the plan or state files")
  - the `ephemeralasnull` function
  - S3 backend native locking, first introduced alongside DynamoDB

  Source: [v1.10 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.10/CHANGELOG.md)
- **Older milestones**, from the CHANGELOGs:
  - **1.5.0** (12 Jun 2023): `import` blocks ("Import is now a configuration-driven, plannable action") and `check` blocks
  - **1.6.0** (4 Oct 2023): `terraform test` GA, with `.tftest.hcl` and `run` blocks
  - **1.7.0** (17 Jan 2024): `mock_provider`/`override_*` in tests, and the `removed` block
  - **1.8.0** (10 Apr 2024): "Providers can now offer functions"
  - **1.9.0** (26 Jun 2024): variable validation can reference other objects; the `templatestring` function; `moved` from `null_resource` to `terraform_data`

  Sources: [v1.5](https://github.com/hashicorp/terraform/blob/v1.5/CHANGELOG.md), [v1.6](https://github.com/hashicorp/terraform/blob/v1.6/CHANGELOG.md), [v1.7](https://github.com/hashicorp/terraform/blob/v1.7/CHANGELOG.md), [v1.8](https://github.com/hashicorp/terraform/blob/v1.8/CHANGELOG.md), [v1.9](https://github.com/hashicorp/terraform/blob/v1.9/CHANGELOG.md)

**Stacks**
- Stacks are "a configuration layer in HCP Terraform". They replace the root-module structure with `component` blocks in `*.tfcomponent.hcl` and `deployment` blocks in `*.tfdeploy.hcl`, and "each deployment has an isolated state file". The docs include an "Update from beta to general availability" page — [stacks/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/stacks/index.mdx), [stacks/update-GA.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/stacks/update-GA.mdx)
- On Terraform Enterprise, Stacks require "resource under management (RUM) pricing". The note names the product "IBM Terraform Self-Managed 2.0" — [rum-pricing-stacks partial](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform-docs-common/docs/partials/tfc-package-callouts/rum-pricing-stacks.mdx)

**OpenTofu releases**, from the OpenTofu CHANGELOGs and git tags:
- **1.13** (tags: v1.13.0 dated 2026-09-30, v1.13.5 dated 2026-10-29; 1.13.3 and 1.13.4 were "skipped due to issues in the release process"). The series "is supported until August 1 2027". Changes:
  - removed the WinRM provisioner connection
  - requires macOS 13 Ventura or later
  - last series with 32-bit builds
  - new `convert` and `assume...` functions
  - experimental Symbol Libraries
  - experimental `-lint`
  - plan files embed provider schemas
  - `tofu test` override instances with wildcards

  Source: [OpenTofu v1.13 CHANGELOG](https://github.com/opentofu/opentofu/blob/v1.13/CHANGELOG.md); also [raw (search result)](https://raw.githubusercontent.com/opentofu/opentofu/v1.13/CHANGELOG.md)
- **1.14.0** is unreleased. It drops 32-bit builds and adds module output type constraints. "The v1.14.x release series is supported until February 1 2028" — [OpenTofu main CHANGELOG](https://github.com/opentofu/opentofu/blob/main/CHANGELOG.md)
- **Feature history:**
  - **1.7:** state encryption ("optional end-to-end encryption for state files"), `removed` blocks, provider-defined functions (`provider::<name>::<func>`), `for_each` in `import` — [v1.7](https://github.com/opentofu/opentofu/blob/v1.7/CHANGELOG.md)
  - **1.8:** "Variables and Locals allowed in module sources and backend configurations (with limitations)" (the "early evaluation" feature), `.tofu` file extension overrides, `mock_provider` — [v1.8](https://github.com/opentofu/opentofu/blob/v1.8/CHANGELOG.md)
  - **1.9:** `for_each` in provider blocks, `-exclude` — [v1.9](https://github.com/opentofu/opentofu/blob/v1.9/CHANGELOG.md)
  - **1.10:** OCI registries for modules and providers, "The `s3` backend can now implement locking without DynamoDB", deprecated variables and outputs — [v1.10](https://github.com/opentofu/opentofu/blob/v1.10/CHANGELOG.md); blog: [opentofu.org/blog/opentofu-1-10-0 (search result)](https://opentofu.org/blog/opentofu-1-10-0/)
  - **1.11:** ephemeral values, resources and write-only attributes; the `enabled` meta-argument inside `lifecycle`. Support for the 1.11 series ended 1 Aug 2026 — [v1.11](https://github.com/opentofu/opentofu/blob/v1.11/CHANGELOG.md)
  - **1.12:** `lifecycle { destroy = false }`, `import` by `identity`, `const = true` variables. Supported until 1 Feb 2027 — [v1.12](https://github.com/opentofu/opentofu/blob/v1.12/CHANGELOG.md)
- **OpenTofu early evaluation in module sources** (doc example):
  `locals { modules_repo = "github.com/myorg/tofu-modules/"; modules_version = "?ref=v1.20.4" }` and `source = "${local.modules_repo}/storage${local.modules_version}"`. The doc adds that the values "may not contain any references to data in the state or provider defined functions. All values must be able to be resolved during `tofu init`" — [OpenTofu modules/sources.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/language/modules/sources.mdx)

**S3 backend locking**
- "State locking is an opt-in feature of the S3 backend … **DynamoDB-based locking is deprecated** and will be removed in a future minor version." `use_lockfile` defaults to `false`. With `use_lockfile`, the backend needs `s3:GetObject`, `s3:PutObject` and `s3:DeleteObject` on the lock file, which sits next to the state as `<key>.tflock` (e.g. `arn:aws:s3:::mybucket/path/to/my/key.tflock`). "It is highly recommended that you enable Bucket Versioning." Non-default workspaces are stored under `env:/<workspace>/<key>` — [S3 backend (s3.mdx)](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/backend/s3.mdx)

**HCP Terraform plans**
- The docs list Free, Essentials, Standard and Premium plans. "Free plans are limited to 500 managed resources" (page created 2026-08-19) — [manage-plan.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform-docs-common/docs/cloud-docs/overview/manage-plan.mdx)
- The legacy HCP Terraform Free plan reached end of life on 31 March 2026, and remaining orgs were moved to the "enhanced Free tier": unlimited users, a 500 managed-resource cap, 1 concurrent run, null resources excluded from the count. These details come from vendor or competitor sources. HashiCorp's own post titled "Continuing HCP Terraform's enhanced free tier experience" exists but was not opened, and the sources disagree on whether the legacy plan had a resource cap — [Scalr (search result)](https://scalr.com/learning-center/hcp-terraform-free-tier-is-being-discontinued-what-you-need-to-know), [env0 (search result)](https://www.env0.com/insights/hcp-terraforms-free-tier-changed-is-it-time-to-consider-a-terraform-cloud-alternative), [HashiCorp blog (search result)](https://www.hashicorp.com/blog/continuing-hcp-terraform-s-enhanced-free-tier-experience)

**Current provider versions**
- hashicorp/aws **6.71.0** (28 Oct 2026) — [AWS provider CHANGELOG](https://github.com/hashicorp/terraform-provider-aws/blob/main/CHANGELOG.md)
- kreuzwerker/docker **v4.6.0** (2026-09-01) — [docker provider CHANGELOG](https://github.com/kreuzwerker/terraform-provider-docker/blob/master/CHANGELOG.md)
- hashicorp/random **3.9.1** (11 Sep 2026), which has an ephemeral `random_password` and an ephemeral `random_bytes` — [random CHANGELOG](https://github.com/hashicorp/terraform-provider-random/blob/main/CHANGELOG.md)
- hashicorp/local **2.9.1** (10 Sep 2026), which has `action/local_command` and `ephemeral/local_command` — [local CHANGELOG](https://github.com/hashicorp/terraform-provider-local/blob/main/CHANGELOG.md)
- hashicorp/null **3.3.2** (10 Sep 2026) — [null CHANGELOG](https://github.com/hashicorp/terraform-provider-null/blob/main/CHANGELOG.md)

**License background**
- A YouTube description in the search results says HashiCorp moved Terraform to the Business Source License in August 2023, and the community forked the last MPL 2.0 release as OpenTofu. This is a weak source, so verify it before quoting — ["OpenTofu Basics Tutorial" (search result)](https://www.youtube.com/watch?v=ctx3nUz0wnQ)

### Inferences
**What to teach, and where.** Ephemeral and write-only values (lesson 3), `import` and `moved` blocks (lesson 3), `terraform test` with `mock_provider` (lesson 4), and provider-defined functions (one slide in lesson 2) are all stable in both tools and are worth teaching.

**Mention only.** Stacks (HCP-only), Terraform Policy (`-policies`), actions, `terraform query`, `-minimal-refresh`, and OpenTofu's experimental Symbol Libraries and lint.

**Terraform vs OpenTofu, as of Oct 2026.** The core language and workflow are the same; mostly you swap `terraform` for `tofu`. The meaningful differences for a beginner:

| OpenTofu-only | Terraform-only |
|---|---|
| state and plan encryption | HCP Terraform and the `cloud` block |
| provider `for_each` | Stacks |
| `-exclude` | Terraform Policy GA |
| the `enabled` meta-argument | actions |
| OCI registries | list resources / `query` |
| `.tofu` overrides | |

Some features are converging: variables in module sources (Tofu 1.8, Terraform 1.15), `destroy = false` (Tofu 1.12, Terraform 1.16), `convert()` (Terraform 1.15, Tofu 1.13), and deprecated variables (Tofu 1.10, Terraform 1.15).

**S3 lock teaching point.** Learners on blog posts from before 2025 will see `dynamodb_table`. Tell them it is deprecated and to use `use_lockfile = true`.

### Gaps
- The exact GA date of Terraform Stacks was not found. The docs confirm GA but give no date.
- The HCP Terraform pricing page and HashiCorp's free-tier blog post could not be opened. Treat the "1 concurrent run" and "EOL March 31, 2026" details as third-party claims.
- The OpenTofu 1.13.0 announcement blog post was not found. The dates above are git tag commit dates, not announcement dates.
- The OpenTofu/BSL/Linux Foundation history was not verified from a primary source this session.

---

## Key question 4: Which free, local exercises work without a cloud account? (kreuzwerker/docker, local, random, null)

### Takeaway
Every core concept except cloud auth and remote backends can be taught for free on a Mac using `hashicorp/random`, `hashicorp/local` and `kreuzwerker/docker`. That covers plan reading, count vs for_each, modules, state, moved/import, drift, tests and ephemeral values. All of the exercises below were run successfully with Terraform 1.17.1.

### Cited Findings
- **Docker provider basics.** Use `source = "kreuzwerker/docker"`; the docs example pins `version = "4.6.0"`, and the provider block can set `host = "unix:///var/run/docker.sock"`. A `context` argument names a Docker context. It "Can also be set via `DOCKER_CONTEXT` environment variable. Overrides the `host` if set." This is useful for Colima or Docker Desktop contexts on a Mac — [kreuzwerker docs/index.md](https://github.com/kreuzwerker/terraform-provider-docker/blob/master/docs/index.md)
- **HashiCorp's official Docker tutorials.** There is a "Get Started – Docker" tutorial series (install, build, change, destroy, variables, outputs) that uses `kreuzwerker/docker` — [docker-get-started (search result)](https://developer.hashicorp.com/terraform/tutorials/docker-get-started), [docker-build (search result)](https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-build)
- **Docker lab, verified.** The config used `docker_image "nginx"` (`name = "nginx:alpine"`, `keep_locally = true`) and `docker_container "web"` (`ports { internal = 80, external = var.external_port }`, default 8081).
  - `plan` printed `Plan: 2 to add, 0 to change, 0 to destroy.`
  - After apply, `curl localhost:8081` returned 200.
  - With `-var external_port=8082` the plan showed `# docker_container.web must be replaced`, `~ external = 8081 -> 8082 # forces replacement`, `Plan: 1 to add, 0 to change, 1 to destroy.`
  - Changing `restart` from `"no"` to `"unless-stopped"` showed `~ update in-place`, `# docker_container.web will be updated in-place`, `Plan: 0 to add, 1 to change, 0 to destroy.`
  - `destroy` printed `Destroy complete! Resources: 2 destroyed.`

  (verified locally)
- **Dynamic block, verified.** `dynamic "ports" { for_each = var.port_map; content { internal = tonumber(ports.key); external = ports.value } }` with `{ "80" = 8091, "443" = 8443 }` produced two `+ ports {}` blocks. (verified locally)
- **random and local labs, verified.** `random_pet` + `local_file` with `count` and `for_each` worked, and so did these: rename with and without `moved`, drift with `-refresh-only`, `state mv`/`state rm`, the `import` block on `random_string`, an ephemeral `random_password` error, and `terraform test` on a local module. Outputs are quoted in the lesson sections below. (verified locally)
- **Local lock contention, verified.** Starting `terraform apply` in the background and then running `terraform plan -lock-timeout=0s` gave "Error: Error acquiring the state lock … Lock Info: ID: … Path: terraform.tfstate Operation: OperationTypeApply Who: root@vm". (verified locally)
- **`terraform_data` replaces `null_resource`.** It is the built-in substitute for `null_resource`; Terraform 1.9 allows `moved` from `null_resource` to `terraform_data` — [v1.9 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.9/CHANGELOG.md)
- **German video series uses Docker.** Two German-language YouTube modules (CLI workflow and project structure; state, backends and collaboration) use the Docker provider so no cloud account is needed — [CLI-Workflow (search result)](https://www.youtube.com/watch?v=uNVqIY97XM4), [State/Backends (search result)](https://www.youtube.com/watch?v=lj9MCWCETQU)

### Inferences
- **Recommended "no-cloud" track:**
  - L1: random_pet + local_file hello world, then nginx in Docker.
  - L2: console drills, count vs for_each shift, dynamic ports.
  - L3: state inspection, moved, drift, import, `state rm`, ephemeral error, lock contention.
  - L4: a `greeting` or `web_container` module with for_each, plus `terraform test`.
  - L5: run tflint, trivy config and checkov against the L4 code. Cloud steps are optional.
- **Possible remote-backend lab without AWS:** an S3-compatible MinIO container, or the `pg` backend against a Postgres container. **Not tested**; endpoint and path-style flags would need verifying before you put this in a lesson.
- **Mac specifics:** Docker Desktop or Colima is required for the docker labs. If `unix:///var/run/docker.sock` isn't present (e.g. with Colima), set `DOCKER_CONTEXT` or the provider's `context`.

### Gaps
- The Docker labs were not run on macOS/Apple Silicon. The provider ships darwin_arm64 builds per its release process, but this was not opened here.
- A MinIO/S3 backend with `use_lockfile` was not tested locally.

---

## Lesson 1 pack: Infrastructure as code and your first Terraform

### Takeaway
Use a 40-minute arc: why IaC, then declarative vs imperative, then install (brew), then providers and resources, then `init`, `plan` (how to read it), `apply`, `destroy`. Do it twice: first with random/local (instant), then nginx in Docker (tangible: curl it). End with "what just appeared: `.terraform/`, `.terraform.lock.hcl`, `terraform.tfstate`".

### Cited Findings
#### Concepts in teaching order (one line each, plus an intuition)
1. **Infrastructure as code:** infrastructure described in versioned text, reviewed like code and applied by a tool. *Intuition: your infra gets a pull request.*
2. **Declarative vs imperative:** you state the end result and Terraform works out the steps. There are no loops or ifs in the usual sense — [O'Reilly ch. 5 (search result)](https://www.oreilly.com/library/view/terraform-up-and/9781098116736/ch05.html). *Intuition: SQL `SELECT` vs a for-loop over rows; React render vs DOM calls.*
3. **Terraform vs OpenTofu:** same language and workflow, different CLI name (`terraform` vs `tofu`). OpenTofu ships a migration guide built around backing up state and testing reversibly — [OpenTofu migration-guide.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/intro/migration/migration-guide.mdx)
4. **Install on a Mac:**
   - Terraform: `brew install hashicorp/tap/terraform`. "Homebrew ignores formulae … from third-party taps until they are trusted … Installing with the fully qualified name … trusts that formula or cask automatically" — [hashicorp/homebrew-tap README](https://github.com/hashicorp/homebrew-tap)
   - OpenTofu: it "is available in the Homebrew Core repository" — [OpenTofu homebrew.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/intro/install/homebrew.mdx). OpenTofu 1.13 requires macOS 13+ — [v1.13 CHANGELOG](https://github.com/opentofu/opentofu/blob/v1.13/CHANGELOG.md)
5. **Providers:** plugins that translate HCL into API calls. They are declared in `required_providers` with `source` and `version`, downloaded by `init`, and pinned in `.terraform.lock.hcl`, which should be committed — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx). *Intuition: a driver, or an npm package for an API.*
6. **Resources:** `resource "TYPE" "NAME" { ... }`, addressed as `TYPE.NAME`. *Intuition: a row Terraform owns.*
7. **The workflow:** `init`, then `fmt`/`validate`, then `plan`, then `apply`, then `destroy`. The style guide says to run `terraform fmt` and `terraform validate` before committing — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
8. **Reading a plan.** Symbols seen in real runs: `+ create`, `~ update in-place`, `-/+ destroy and then create replacement`, `- destroy`. Also `(known after apply)`, `# forces replacement`, `# (N unchanged attributes hidden)`, and the summary line `Plan: X to add, Y to change, Z to destroy.` (verified locally). Plan modes (normal, destroy, refresh-only) and `-out` are described in [plan.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/commands/plan.mdx)

#### Small HCL examples with expected plan output (verified locally)
Example A, instant, no Docker:
```hcl
terraform {
  required_version = ">= 1.10"
  required_providers {
    random = { source = "hashicorp/random", version = "~> 3.9" }
    local  = { source = "hashicorp/local",  version = "~> 2.9" }
  }
}
resource "random_pet" "server" { length = 2 }
resource "local_file" "hello" {
  filename = "${path.module}/out/hello.txt"
  content  = "hello from ${random_pet.server.id}\n"
}
output "pet" { value = random_pet.server.id }
```
Expected plan (pattern from the verified run):
```
  # random_pet.server will be created
  + resource "random_pet" "server" {
      + id        = (known after apply)
      + length    = 2
      + separator = "-"
    }
Plan: 2 to add, 0 to change, 0 to destroy.
Changes to Outputs:
  + pet = (known after apply)
```
After apply the output looks like `pet = "lenient-opossum"` (a random name).

Example B, Docker nginx:
```hcl
terraform {
  required_providers {
    docker = { source = "kreuzwerker/docker", version = "~> 4.6" }
  }
}
provider "docker" {}
variable "external_port" {
  type    = number
  default = 8081
}
resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}
resource "docker_container" "web" {
  name  = "tf-demo-web"
  image = docker_image.nginx.image_id
  ports {
    internal = 80
    external = var.external_port
  }
}
```
- `plan`: `# docker_container.web will be created`, `+ image = (known after apply)`, `+ ports { + external = 8081 + internal = 80 }`, `# docker_image.nginx will be created`, `Plan: 2 to add, 0 to change, 0 to destroy.`
- After `apply`, `curl localhost:8081` returns 200.
- `-var external_port=8082` gives `# docker_container.web must be replaced`, `~ external = 8081 -> 8082 # forces replacement`, `Plan: 1 to add, 0 to change, 1 to destroy.`
- Adding `restart = var.restart` and changing it from `"no"` to `"unless-stopped"` gives `~ update in-place`, `Plan: 0 to add, 1 to change, 0 to destroy.`

(verified locally)

### Inferences
#### Misconceptions to address
- "plan changes things": it doesn't. Apply does, and `apply` re-plans unless you pass a saved plan file.
- "Terraform edits resources in place": many arguments force replacement (the port change above). Teach learners to scan for `-/+` and `# forces replacement` before typing yes.
- "destroy only deletes what I wrote today": it deletes everything in state for that configuration.
- "Lock file = state lock": no. `.terraform.lock.hcl` pins provider versions and hashes. State locks are separate (lesson 3).
- "`(known after apply)` means something is broken": it means the value is computed by the provider.

#### Hands-on exercise ideas
1. Hello world (Example A). Run `init` and inspect `.terraform/` and `.terraform.lock.hcl`. Run `plan`, `apply`, `cat out/hello.txt`, `destroy`.
2. Docker nginx (Example B). Apply, curl it, change the port and predict the plan, change `restart` and predict the plan, then destroy.
3. "Predict the summary line" drill: show three HCL edits and have learners write the `Plan:` line before running.
4. Save a plan: `terraform plan -out=tfplan`, then `terraform show tfplan`, then `terraform apply tfplan`. Explain why CI uses saved plans.

#### Resources (3–8)
- HashiCorp, "Get Started – Docker" tutorials: https://developer.hashicorp.com/terraform/tutorials/docker-get-started and https://developer.hashicorp.com/terraform/tutorials/docker-get-started/docker-build (search results; not opened)
- Terraform `plan` command docs (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/commands/plan.mdx (opened). Public path, derived: developer.hashicorp.com/terraform/cli/commands/plan
- kreuzwerker/docker provider docs (source): https://github.com/kreuzwerker/terraform-provider-docker/blob/master/docs/index.md (opened)
- Video, HashiCorp channel: "Introduction to HashiCorp Terraform with Armon Dadgar", https://www.youtube.com/watch?v=h970ZBgKINg, and the newer "Introduction to Terraform", https://www.youtube.com/watch?v=ZFLWA1kQ3ls (search results; the search summary says the first video's description points to the newer one; both are several years old)
- Video, DevOps Directive (Sid Palas): "Complete Terraform Course – From BEGINNER to PRO!", https://www.youtube.com/watch?v=7xngnjfIlK4 (search result; ID confirmed in the companion repo README https://github.com/sidpalas/devops-directive-terraform-course, opened). It is AWS-based, about 2.5 h, and from 2022.
- OpenTofu migration guide (source): https://github.com/opentofu/opentofu/blob/main/website/docs/intro/migration/migration-guide.mdx (opened)

### Gaps
- The `<= read (data resources)` plan symbol and `+/-` (create_before_destroy) were not reproduced in this session. Both are standard, but confirm them from a live run before showing them.
- HashiCorp's install page for macOS could not be opened. The brew command comes from the tap README.

---

## Lesson 2 pack: The HCL language

### Takeaway
Teach HCL as "JSON with references and expressions". Cover blocks and arguments, then references, types, variables (with validation and precedence), locals and outputs. Then the expression toolbox: templates, conditionals, `for`, splat, functions. Then repetition: count vs for_each, then dynamic blocks. Use `terraform console` as the REPL for the whole lesson; every expression below was evaluated in it.

### Cited Findings
#### Concepts in teaching order
1. **Blocks, labels and arguments:** `resource "local_file" "x" { filename = "..." }`. The block type and labels identify the thing, and arguments set values. The style guide covers ordering: meta-arguments (`count`/`for_each`) come first — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
2. **References:** `var.x`, `local.x`, `TYPE.NAME.attr`, `module.NAME.output`, `data.TYPE.NAME.attr`, `each.key`/`each.value`, `count.index`, `path.module`. *Intuition: references are how you draw graph edges.* For example, `"web-${random_pet.name.id}"` evaluated to `"web-lenient-opossum"`. (verified locally)
3. **Types:**
   - primitives: `string`, `number`, `bool`
   - collections: `list(T)`, `map(T)`, `set(T)`
   - structural: `object({...})`, `tuple([...])`

   `type(var.names)` gives `list(string)`. `toset(["b","a","b"])` gives `toset(["a","b"])`, so sets dedupe and sort. (verified locally) `optional(bool, false)` inside an object type worked: `map(object({ loud = optional(bool, false) }))`. (verified locally)
4. **Variables:** `type`, `default`, `description`, `sensitive`, `validation { condition, error_message }`, `ephemeral` (TF 1.10+), and `deprecated` (TF 1.15+) — [v1.15 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md). Since 1.9, validation conditions may refer to other objects — [v1.9 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.9/CHANGELOG.md)
5. **Variable precedence**, later sources win: (1) `-var`/`-var-file` in order given, and HCP Terraform variables; (2) `*.auto.tfvars`/`.auto.tfvars.json` in lexical order; (3) `terraform.tfvars.json`; (4) `terraform.tfvars`; (5) environment variables (`TF_VAR_name`). The docs list it highest-first. A missing value with no default triggers a prompt — [values/variables.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/values/variables.mdx)
6. **Locals:** named intermediate expressions, scoped to the module. *Intuition: `const` in a function body.*
7. **Outputs:** values exported from a module or root, which can be `sensitive`. Output type constraints are new in TF 1.15 — [v1.15 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md)
8. **String templates:** `"${...}"` interpolation and `%{ if }`/`%{ for }` directives. `templatefile()` reads a template from a file; `templatestring()` (TF 1.9) renders a template held in a string — [v1.9 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.9/CHANGELOG.md)
9. **Conditionals:** `var.names[0] == "alpha" ? "first" : "other"` gives `"first"`. (verified locally)
10. **`for` expressions:**
    - `[for n in var.names : upper(n) if n != "bravo"]` gives `["ALPHA","CHARLIE"]`
    - `{for n in var.names : n => length(n)}` gives `{"alpha"=5,"bravo"=5,"charlie"=7}`

    (verified locally)
11. **Splat:** `local_file.by_count[*].filename` gives `["./out/count-0.txt","./out/count-1.txt","./out/count-2.txt"]`. (verified locally)
12. **`count` vs `for_each`:**
    - `count` takes a number, giving instances `NAME[0..n-1]`.
    - `for_each` takes a map or a set of strings, giving `NAME["key"]`.
    - Both must be known at plan time.
    - `for_each` can't use sensitive values; the docs suggest `toset([for k,v in local.map : k])` as a workaround.

    Sources: [count.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/count.mdx), [for_each.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/for_each.mdx). OpenTofu 1.11 adds `lifecycle { enabled = var.x }` for zero-or-one instances — [OpenTofu enabled.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/language/meta-arguments/enabled.mdx)
13. **Dynamic blocks:** generate repeated nested blocks (e.g. `ports`) from a collection. The iterator is named after the block (`ports.key`, `ports.value`). (verified locally)
14. **Built-in functions**, verified in console:
    - `upper("hello")` gives `"HELLO"`
    - `merge({a=1},{b=2},{a=3})` gives `{a=3,b=2}`, so the last one wins
    - `lookup({dev="t3.micro"},"prod","t3.nano")` gives `"t3.nano"`
    - `cidrsubnet("10.0.0.0/16",8,2)` gives `"10.0.2.0/24"`

    New functions: `convert()` (TF 1.15), and `contains()` with null (TF 1.16) — [v1.15](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md), [v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md)
15. **Provider-defined functions:** `provider::<name>::<func>(...)`, in Terraform since 1.8 and OpenTofu since 1.7 — [TF v1.8 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.8/CHANGELOG.md), [OpenTofu v1.7 CHANGELOG](https://github.com/opentofu/opentofu/blob/v1.7/CHANGELOG.md)
16. **`terraform console`:** a REPL against your config and state. TF 1.16 adds `-scope=<module address>` — [v1.16 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md). Piping expressions works, e.g. `echo 'upper("hello")' | terraform console`. (verified locally)

#### Small HCL examples with expected output (verified locally)
Validation:
```hcl
variable "name" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,20}$", var.name))
    error_message = "name must be lowercase letters, digits or dashes, 2-21 chars."
  }
}
```
Passing `"Bad Name"` gives:
```
Error: Invalid value for variable
  │ var.name is "Bad Name"
name must be lowercase letters, digits or dashes, 2-21 chars.
This was checked by the validation rule at modules/greeting/main.tf:4,3-13.
```
Conditional and local:
```hcl
locals {
  message = var.loud ? upper("hello ${var.name}!") : "hello ${var.name}"
}
```
Dynamic block:
```hcl
variable "port_map" {
  type    = map(number)
  default = { "80" = 8091, "443" = 8443 }
}
resource "docker_container" "multi" {
  name  = "tf-dyn"
  image = "nginx:alpine"
  dynamic "ports" {
    for_each = var.port_map
    content {
      internal = tonumber(ports.key)
      external = ports.value
    }
  }
}
```
The plan shows two `+ ports { + external = ... + internal = ... }` blocks and `Plan: 1 to add, 0 to change, 0 to destroy.`

count vs for_each shift (the key demo):
```hcl
variable "names" {
  type    = list(string)
  default = ["alpha", "bravo", "charlie"]
}
resource "local_file" "by_count" {
  count    = length(var.names)
  filename = "${path.module}/out/count-${count.index}.txt"
  content  = "hello ${var.names[count.index]}\n"
}
resource "local_file" "by_each" {
  for_each = toset(var.names)
  filename = "${path.module}/out/each-${each.key}.txt"
  content  = "hello ${each.key}\n"
}
```
Apply, then run `plan -var='names=["bravo","charlie"]'`:
```
  # local_file.by_count[0] must be replaced
      ~ content = <<-EOT # forces replacement
  # local_file.by_count[1] must be replaced
  # local_file.by_count[2] will be destroyed
  # (because index [2] is out of range for count)
  # local_file.by_each["alpha"] will be destroyed
  # (because key ["alpha"] is not in for_each map)
Plan: 2 to add, 0 to change, 4 to destroy.
```

### Inferences
#### Misconceptions to address
- "HCL is a programming language": no. There is no mutation and no loops with side effects; everything is an expression evaluated against a graph.
- "`for` expressions create resources": they transform values. Only `count`/`for_each` (or modules) create instances.
- "`list` vs `set` doesn't matter": sets are unordered and deduped, and `for_each` needs a set or map, not a list.
- "I can make `count` depend on a resource attribute": not if that attribute is unknown until apply (the plan-time-known rule).
- "`sensitive` variables are safe in state": no (lesson 3).

#### Hands-on exercise ideas
1. A console kata: 10 expressions from the table above. Learners predict, then evaluate.
2. Write `variable "environment"` with validation `contains(["dev","prod"], var.environment)` and trigger the error.
3. The count-shift lab above, then refactor to `for_each` using `moved` blocks (preview of lesson 3).
4. A dynamic `ports` block driven by a `map(number)`.
5. Use `templatefile()` to render an `index.html` for nginx and mount it or upload it into the container. **Not tested here;** check the `docker_container` `upload` block before using it.

#### Resources (3–8)
- Gruntwork, "Terraform tips & tricks: loops, if-statements, and gotchas": https://www.gruntwork.io/blog/terraform-tips-tricks-loops-if-statements-and-gotchas (search result)
- *Terraform: Up & Running*, 3rd ed., ch. 5: https://www.oreilly.com/library/view/terraform-up-and/9781098116736/ch05.html (search result; paywalled)
- count docs (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/count.mdx and for_each docs: https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/meta-arguments/for_each.mdx (opened; public paths, derived: developer.hashicorp.com/terraform/language/meta-arguments/count and /for_each)
- Variables and precedence (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/values/variables.mdx (opened)
- Style guide (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx (opened; public path, derived: developer.hashicorp.com/terraform/language/style)
- Video: DevOps Directive course, modules 04 "Variables and Outputs" and 05 "Language Features": https://www.youtube.com/watch?v=7xngnjfIlK4 (module list from the repo README https://github.com/sidpalas/devops-directive-terraform-course)

### Gaps
- The `dynamic-blocks.mdx` doc page was located in the repo but not read; the example above was verified by running it instead.
- Exact `%{ if }` template-directive syntax was not exercised in this session.

---

## Lesson 3 pack: State

### Takeaway
State is Terraform's memory: a JSON map from addresses to real object ids and attributes, plus outputs and dependencies. Because it holds secrets and is the source of truth for "what do I own", it must live in a locked, versioned remote backend. In 2026 that means S3 with `use_lockfile = true` (no DynamoDB) or HCP Terraform. Refactor with `moved`/`removed`/`import` blocks rather than CLI state surgery. Detect drift with `-refresh-only`. Keep secrets out of state with ephemeral values and write-only arguments. On OpenTofu, encrypt state.

### Cited Findings
#### Concepts in teaching order
1. **What state holds:** `version`, `terraform_version`, `serial` (it went up to 9 after several applies), `lineage`, `outputs`, and `resources[]` (each with `mode`/`type`/`name`/`provider` and `instances[].attributes`/`sensitive_attributes`/`dependencies`). (verified locally)
2. **Why it matters:**
   - Mapping: renames destroy and recreate without `moved` (verified locally).
   - Drift detection (verified locally).
   - Secrets are stored in plaintext: local state "includes any secret values you defined in your configuration. Treat your state file as sensitive data by excluding it from Git workflows" — [manage-sensitive-data/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/index.mdx)
3. **Locking:** concurrent runs are refused: "Error: Error acquiring the state lock … Operation: OperationTypeApply". (verified locally) VCS can't lock state — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
4. **Remote backend: S3.**
   - Use `backend "s3" { bucket, key, region, use_lockfile = true }`. Enable bucket versioning. DynamoDB locking is deprecated.
   - Using partial configuration for access credentials is recommended.
   - Workspaces are stored at `env:/<ws>/<key>`.

   Source: [s3.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/backend/s3.mdx). Native S3 locking was experimental in 1.10 and GA in 1.11 — [v1.10](https://github.com/hashicorp/terraform/blob/v1.10/CHANGELOG.md), [v1.11](https://github.com/hashicorp/terraform/blob/v1.11/CHANGELOG.md). OpenTofu has had it since 1.10 — [OpenTofu v1.10](https://github.com/opentofu/opentofu/blob/v1.10/CHANGELOG.md). The S3 backend supports `aws login` auth since TF 1.15 — [v1.15](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md)
5. **Remote backend: HCP Terraform.** The Free plan is capped at 500 managed resources — [manage-plan.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform-docs-common/docs/cloud-docs/overview/manage-plan.mdx). See key question 3 for the legacy-plan change.
6. **State commands**, verified locally:
   - `terraform state list` prints addresses, e.g. `local_file.by_count[0]`.
   - `terraform state show random_pet.name` prints the resource block with its attributes.
   - `terraform state mv 'local_file.by_each["alpha"]' 'local_file.by_each["alpha2"]'` prints `Successfully moved 1 object(s).`
   - `terraform state rm …` prints `Successfully removed 1 resource instance(s).`, after which Terraform plans to create it again.

   `state show -json` is new in TF 1.16 — [v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md). The full command set (identities, list, mv, pull, push, replace-provider, rm, show) is under [cli/commands/state/](https://github.com/hashicorp/web-unified-docs/tree/main/content/terraform/v1.17.x/docs/cli/commands/state) (directory listing seen via git; individual pages not all read)
7. **`moved` blocks:** declarative renames, reviewable in a PR. Example: `moved { from = random_pet.server  to = random_pet.name }` gives `# random_pet.server has moved to random_pet.name` and no changes. (verified locally) They also cover moving from `null_resource` to `terraform_data` (TF 1.9) and cross-type moves where the provider supports them (TF 1.8) — [v1.9](https://github.com/hashicorp/terraform/blob/v1.9/CHANGELOG.md), [v1.8](https://github.com/hashicorp/terraform/blob/v1.8/CHANGELOG.md)
8. **`removed` blocks:** forget a resource without destroying it (TF 1.7; OpenTofu 1.7). `lifecycle { destroy = false }` arrived in TF 1.16 and OpenTofu 1.12 — [TF v1.7](https://github.com/hashicorp/terraform/blob/v1.7/CHANGELOG.md), [TF v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md), [OpenTofu v1.12](https://github.com/opentofu/opentofu/blob/v1.12/CHANGELOG.md)
9. **`import` blocks:** "Import is now a configuration-driven, plannable action" (TF 1.5). The `id` accepts expressions (1.6), `identity` can replace `id` (1.12), and import blocks work inside modules (1.16). `terraform query` can generate import config (1.14) — [v1.5](https://github.com/hashicorp/terraform/blob/v1.5/CHANGELOG.md), [v1.6](https://github.com/hashicorp/terraform/blob/v1.6/CHANGELOG.md), [v1.12](https://github.com/hashicorp/terraform/blob/v1.12/CHANGELOG.md), [v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md), [v1.14](https://github.com/hashicorp/terraform/blob/v1.14/CHANGELOG.md). Verified output: when config matches, `# random_string.legacy will be imported`, `Plan: 1 to import, …`; when it doesn't, `must be replaced … Warning: this will destroy the imported resource`. (verified locally)
10. **Drift and `-refresh-only`:** this mode updates state to match reality without changing infrastructure (available since TF 0.15.4) — [plan.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/commands/plan.mdx). Verified output is in key question 1. New in 1.17: `-minimal-refresh`, which refreshes only resources with proposed changes — [v1.17](https://github.com/hashicorp/terraform/blob/v1.17/CHANGELOG.md)
11. **Sensitive values:** `sensitive = true` redacts values in the CLI and UI but they still sit in state. Ephemeral values are "available at runtime, but Terraform omits them from state and plan files entirely." Version requirements: `sensitive` 0.15+, `ephemeral` 1.10+, write-only arguments 1.11+ — [manage-sensitive-data/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/index.mdx)
12. **Ephemeral resources and write-only arguments:** the doc example is `ephemeral "random_password" "db" { length = 16 … }` feeding `aws_db_instance` `password_wo = …` with `password_wo_version = 1`. Bump the version number to rotate — [write-only.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/write-only.mdx). Misuse gives "Ephemeral values are not valid for "content", because it is not a write-only attribute and must be persisted to state." (verified locally) TF 1.16 adds the `terraform_data` `store` block for ephemeral or sensitive values across plan and apply — [v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md). OpenTofu docs: [opentofu.org/docs/language/ephemerality](https://opentofu.org/docs/language/ephemerality/) (URL appears in the opened v1.11 CHANGELOG)
13. **OpenTofu state encryption (1.7+):**
    - Configured in `terraform { encryption { key_provider "pbkdf2" "x" { passphrase = … } method "aes_gcm" "y" { keys = key_provider.pbkdf2.x } state { method = method.aes_gcm.y } } }`.
    - The passphrase must be at least 16 characters; iterations at least 200,000, default 600,000.
    - To migrate existing state, use a `method "unencrypted"` with a `fallback {}` block, apply, then remove the fallback and optionally set `enforced = true`.
    - Key providers include AWS KMS, GCP KMS, OpenBao, Azure Key Vault and external programs.

    Sources: [pbkdf2.tf example](https://github.com/opentofu/opentofu/blob/main/website/docs/language/state/examples/encryption/pbkdf2.tf), [fallback_from_unencrypted.tf](https://github.com/opentofu/opentofu/blob/main/website/docs/language/state/examples/encryption/fallback_from_unencrypted.tf), [encryption.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/language/state/encryption.mdx), [OpenTofu v1.13 CHANGELOG (AWS KMS encryption_context, OpenBao)](https://github.com/opentofu/opentofu/blob/v1.13/CHANGELOG.md)

#### Small HCL examples
S3 backend, current form (adapted from the s3.mdx example plus the `use_lockfile` argument):
```hcl
terraform {
  backend "s3" {
    bucket       = "mybucket"
    key          = "path/to/my/key"
    region       = "us-east-1"
    use_lockfile = true
  }
}
```
Rename via `moved`, verified:
```hcl
resource "random_pet" "name" { length = 2 }   # was "server"
moved {
  from = random_pet.server
  to   = random_pet.name
}
```
The plan shows `# random_pet.server has moved to random_pet.name`.

Import, verified:
```hcl
import {
  to = random_string.legacy
  id = "abc123"
}
resource "random_string" "legacy" {
  length  = 6
  special = true   # with false, the plan wants to destroy and recreate the imported object
}
```
The plan shows `Plan: 1 to import, ...`.

### Inferences
#### Misconceptions to address
- "State is a cache I can delete": deleting it orphans everything. Terraform will try to create duplicates.
- "`state rm` deletes the resource": it only makes Terraform forget. In the cloud the object keeps running and costing money.
- "`terraform refresh` / `-refresh-only` fixes drift": it accepts reality into state. A normal apply is what pushes config back onto reality.
- "Import writes my config": it doesn't (`-generate-config-out` and `terraform query` help). Iterate until the plan shows no changes.
- "DynamoDB is required for S3 locking": not since 1.11.
- "`sensitive = true` encrypts": no. Use ephemeral/write-only values, remote backends with encryption at rest, or OpenTofu encryption.

#### Hands-on exercise ideas
All local and tested unless marked.
1. Open `terraform.tfstate` with `jq` and find the serial, lineage and an attribute. Run apply again and watch `serial` increase.
2. `state list` and `state show`, then `state mv` and `state rm`, and observe the next plan.
3. Rename a resource without `moved` (see the destroy/create) and then with it (see the move).
4. Drift: delete a managed file or `docker rm -f` the container, then run `plan -refresh-only` and then a normal `plan`.
5. Import: run `docker run -d --name legacy nginx:alpine`, then write an `import` block for `docker_container`. **Not tested; check the docker provider's import ID format (likely the container id).** The random_string import is the tested fallback.
6. Lock contention: run `apply` in one terminal and `plan -lock-timeout=0s` in another.
7. Ephemeral error: put an `ephemeral "random_password"` result into `local_file.content` and read the error.
8. Optional, OpenTofu: add pbkdf2/aes_gcm encryption, then `cat terraform.tfstate` to see ciphertext. **Not run here.**
9. Optional, cloud: an S3 bucket with versioning plus `use_lockfile`, migrated from local state with `terraform init -migrate-state`. **Not run here.**

#### Resources (3–8)
- S3 backend docs (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/backend/s3.mdx (opened; public path, derived: developer.hashicorp.com/terraform/language/backend/s3)
- Manage sensitive data, ephemeral and write-only (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/index.mdx and https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/manage-sensitive-data/write-only.mdx (opened)
- moved and import block references (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/block/moved.mdx and https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/block/import.mdx (files checked out; contents only partly read)
- OpenTofu state encryption (source): https://github.com/opentofu/opentofu/blob/main/website/docs/language/state/encryption.mdx (checked out; examples read)
- Video: DevOps Directive course module 03 "Basics" covers remote backends with Terraform Cloud and AWS: https://www.youtube.com/watch?v=7xngnjfIlK4 (repo README, opened). It predates `use_lockfile`; warn learners that DynamoDB in older videos is deprecated.
- Video (German, Docker-based) on state and backends: https://www.youtube.com/watch?v=lj9MCWCETQU (search result; not reviewed)

### Gaps
- `moved.mdx`/`import.mdx` were checked out but not read in full. Behaviour was verified by running instead.
- No HashiCorp video specifically about ephemeral values or write-only arguments was found.

---

## Lesson 4 pack: Modules, environments and testing

### Takeaway
A module is just a directory of .tf files. The directory you run in is the root module; anything it calls with `module {}` is a child. Teach the inputs-in/outputs-out contract, local modules at `./modules/<name>`, registry modules pinned by version, and composition (small modules wired together in a thin root). Use separate root directories per environment rather than CLI workspaces. Test modules with `terraform test`: plan-mode asserts, `expect_failures` for validation, and `mock_provider` for cloud-free tests.

### Cited Findings
#### Concepts in teaching order
1. **Root vs child module:** child modules receive inputs as arguments from the parent — [values/variables.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/values/variables.mdx). The style guide says "Store local modules at `./modules/<module_name>`", and registry module repos should be named `terraform-<PROVIDER>-<NAME>` — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
2. **Inputs and outputs:** the module's variables are its API and its outputs are return values. A parent can use `for_each` on a module: `module.greeting["grace"].path`. (verified locally)
3. **Module sources and versions:** local paths, registry (`terraform-aws-modules/vpc/aws` with `version`), git `?ref=`.
   - Variables and locals in `source`/`version`: TF 1.15 and OpenTofu 1.8 — [v1.15](https://github.com/hashicorp/terraform/blob/v1.15/CHANGELOG.md), [OpenTofu modules/sources.mdx](https://github.com/opentofu/opentofu/blob/main/website/docs/language/modules/sources.mdx)
   - OpenTofu can also install modules from OCI registries (1.10) — [OpenTofu v1.10](https://github.com/opentofu/opentofu/blob/v1.10/CHANGELOG.md)
   - Example registry module: [terraform-aws-modules/terraform-aws-vpc](https://github.com/terraform-aws-modules/terraform-aws-vpc) (README opened)
4. **Version pinning for modules:** "Pin modules to a specific major and minor version" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
5. **Composition:** a docs page exists at [modules/develop/composition.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/modules/develop/composition.mdx) (checked out, not quoted). To share data between separate configurations, the style guide recommends `tfe_outputs` or provider-specific data sources — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
6. **Environments: workspaces vs directories:**
   - Workspaces "can be helpful for specific use cases".
   - "We recommend using alternative approaches for complex deployments requiring separate credentials and access controls."
   - The recommendation: reusable modules plus a separate root configuration per deployment, each with its own backend.

   Source: [cli/workspaces/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/workspaces/index.mdx). The S3 backend puts workspaces at `env:/<ws>/<key>` in the same bucket — [s3.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/backend/s3.mdx). Stacks (HCP Terraform) are HashiCorp's newer answer for repeating deployments — [stacks/index.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/stacks/index.mdx)
7. **`terraform test`:**
   - GA in 1.6 with `.tftest.hcl` files and `run` blocks (`command = plan|apply`, `assert`, `variables`, `expect_failures`, `module { source = ... }`) — [v1.6](https://github.com/hashicorp/terraform/blob/v1.6/CHANGELOG.md)
   - Mocks (`mock_provider`, `override_resource`/`override_data`/`override_module`) in 1.7 — [v1.7](https://github.com/hashicorp/terraform/blob/v1.7/CHANGELOG.md)
   - JUnit XML in 1.11 and `-parallelism` in 1.12 — [v1.11](https://github.com/hashicorp/terraform/blob/v1.11/CHANGELOG.md), [v1.12](https://github.com/hashicorp/terraform/blob/v1.12/CHANGELOG.md)
   - Mocked ephemeral resources in 1.17 — [v1.17](https://github.com/hashicorp/terraform/blob/v1.17/CHANGELOG.md)
   - The style guide says "Write tests for your modules" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
   - OpenTofu's `tofu test` has had mocks since 1.8 — [OpenTofu v1.8](https://github.com/opentofu/opentofu/blob/v1.8/CHANGELOG.md)

#### Small HCL examples with expected output (verified locally)
`modules/greeting/main.tf`:
```hcl
variable "name" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,20}$", var.name))
    error_message = "name must be lowercase letters, digits or dashes, 2-21 chars."
  }
}
variable "loud" {
  type    = bool
  default = false
}
locals {
  message = var.loud ? upper("hello ${var.name}!") : "hello ${var.name}"
}
resource "local_file" "this" {
  filename = "${path.root}/out/${var.name}.txt"
  content  = "${local.message}\n"
}
output "path" { value = local_file.this.filename }
```
Root `main.tf`:
```hcl
variable "people" {
  type    = map(object({ loud = optional(bool, false) }))
  default = { ada = {}, grace = { loud = true } }
}
module "greeting" {
  source   = "./modules/greeting"
  for_each = var.people
  name     = each.key
  loud     = each.value.loud
}
output "files" { value = { for k, m in module.greeting : k => m.path } }
```
The plan shows `# module.greeting["ada"].local_file.this will be created` and `# module.greeting["grace"].local_file.this will be created`.

`tests/greeting.tftest.hcl`:
```hcl
run "loud_person_is_uppercased" {
  command = plan
  assert {
    condition     = module.greeting["grace"].path == "./out/grace.txt"
    error_message = "unexpected path"
  }
}
run "rejects_bad_names" {
  command = plan
  module { source = "./modules/greeting" }
  variables { name = "Bad Name" }
  expect_failures = [var.name]
}
```
`terraform test` output:
```
tests/greeting.tftest.hcl... in progress
  run "loud_person_is_uppercased"... pass
  run "rejects_bad_names"... pass
tests/greeting.tftest.hcl... tearing down
tests/greeting.tftest.hcl... pass
Success! 2 passed, 0 failed.
```
Two gotchas came up in the verified runs:
- `expect_failures = [module.greeting["Bad Name"].var.name]` is rejected: "You can only expect failures from checkable objects such as input variables, output values, check blocks, managed resources and data sources." Fix it by testing the module directly with a `module {}` block in the run.
- Adding a `module {}` source in a test requires re-running `terraform init` ("Error: Module not installed").

### Inferences
#### Misconceptions to address
- "Modules are like classes with methods": they are closer to pure functions over inputs that also own resources.
- "One module per resource is good design": thin wrappers add indirection. Make modules around a unit of ownership (a service, a network).
- "Workspaces = environments": fine for throwaway copies, risky for prod isolation. The docs agree.
- "`version = "latest"`": registry modules take constraints like `~> 5.1`, and git sources pin with `?ref=v1.2.3`.
- "Tests need a cloud account": not with `command = plan` or `mock_provider`.

#### Hands-on exercise ideas
1. Extract a `web_container` module from the lesson 1 nginx config (inputs `name` and `external_port`, output the URL). Call it with `for_each` over `{ blue = 8081, green = 8082 }`.
2. Move existing resources into the module without recreation using `moved { from = docker_container.web  to = module.web["blue"].docker_container.this }`. **Not tested; verify the plan shows a move.**
3. Create `envs/dev` and `envs/prod` roots calling the same module with different ports. Compare this with `terraform workspace new dev`.
4. Write `terraform test` with one plan-mode assert and one `expect_failures`. Bonus: `mock_provider "docker" {}` with `command = apply`. **Not tested here.**
5. Use a public registry module (e.g. `terraform-aws-modules/vpc/aws`) with `terraform init` only, then read `.terraform/modules`. This needs network access to the registry.

#### Resources (3–8)
- Workspaces guidance (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/cli/workspaces/index.mdx (opened; public path, derived: developer.hashicorp.com/terraform/cli/workspaces)
- Module development and composition (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/modules/develop/composition.mdx (checked out)
- Tests docs (source): https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/tests/index.mdx and mocking: https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/tests/mocking.mdx (paths seen in the repo tree; not read)
- Anton Babenko, terraform-best-practices (free book): https://www.terraform-best-practices.com (URL from the opened README at https://github.com/antonbabenko/terraform-best-practices). His terraform-aws-modules org: https://github.com/terraform-aws-modules/terraform-aws-vpc (opened)
- Video: DevOps Directive course modules on modules and on managing multiple environments: https://www.youtube.com/watch?v=7xngnjfIlK4 (module list per repo README; later modules were not read)
- Video, possibly relevant: "Terraform Module Best Practices", https://www.youtube.com/watch?v=2XO-uh198KY (search result; the search summary also labels it "Complete Terraform Course with AWS Projects in 2025", so the title is uncertain; channel unverified)

### Gaps
- `composition.mdx` and `tests/*.mdx` were not read in full. The test syntax above was verified by running it.
- No Anton Babenko YouTube URL appeared in search results, so none is listed.

---

## Lesson 5 pack: Terraform on a real cloud and in CI

### Takeaway
Use the AWS provider (v6.x) with short-lived credentials: SSO or `aws login` locally, GitHub OIDC in CI. Never use long-lived access keys in repos or CI secrets. Start with a cheap, safe first project: a versioned S3 bucket with tags and `use_lockfile` state, with an AWS Budget set first. In CI, run plan on the pull request (posted as a comment) and apply on merge to main behind an environment approval. Add tflint (lint), `trivy config` (tfsec's successor) and/or checkov (policy) as gates. Pin GitHub Actions to commit SHAs, given the March 2026 Trivy action compromise.

### Cited Findings
#### Concepts in teaching order
1. **AWS provider auth order:** "1. Parameters in the provider configuration 2. Environment variables 3. Shared credentials files 4. Shared configuration files 5. Container credentials 6. Instance profile credentials and Region". This "matches the precedence used by the AWS CLI".
   - Supports `AWS_PROFILE`, `assume_role`, and web identity/OIDC "using environment variables or in a named profile".
   - `default_tags` applies tags to all resources.

   Source: [AWS provider docs index](https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown). Current version: 6.71.0 — [AWS CHANGELOG](https://github.com/hashicorp/terraform-provider-aws/blob/main/CHANGELOG.md)
2. **Credentials hygiene:** "Protect credentials by using dynamic provider credentials or a secrets manager such as HashiCorp Vault" — [style.mdx](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/language/style.mdx)
3. **Plan on PR, apply on merge.** HashiCorp's official tutorial uses separate plan and apply workflows driven by HCP Terraform, with an API token stored as a GitHub secret — [Automate Terraform with GitHub Actions (search result)](https://developer.hashicorp.com/terraform/tutorials/automation/github-actions). Community guides use a `pull_request`-triggered plan (posting the plan as a PR comment via `actions/github-script`, which needs `pull-requests: write`) and a `push`-to-`main` apply, gated by GitHub Environments with required reviewers. They warn against `AdministratorAccess` roles and suggest separate read-only plan roles — [OneUptime guide, Feb 2026 (search result; third-party)](https://oneuptime.com/blog/post/2026-02-12-terraform-cicd-github-actions-for-aws/view)
4. **Setup actions:**
   - `hashicorp/setup-terraform@v4` (inputs `terraform_version`, `terraform_wrapper`; the wrapper exposes stdout/stderr/exitcode and can be disabled) — [setup-terraform README](https://github.com/hashicorp/setup-terraform)
   - `opentofu/setup-opentofu@v2` (`tofu_version`, `tofu_wrapper`) — [setup-opentofu README](https://github.com/opentofu/setup-opentofu)
5. **GitHub OIDC to AWS:**
   - The workflow needs `permissions: id-token: write`, then `aws-actions/configure-aws-credentials@v6.3.0` with `role-to-assume` and `aws-region`.
   - The IAM trust policy uses `sts:AssumeRoleWithWebIdentity` with conditions `token.actions.githubusercontent.com:aud = sts.amazonaws.com` and `…:sub = repo:<ORG>@<ORG_ID>/<REPO>@<REPO_ID>:ref:refs/heads/<BRANCH>`.
   - **New in 2026:** repositories created after 15 July 2026 get immutable subject claims with `@ORG_ID`/`@REPO_ID` suffixes, and workflows running in environments get `environment:<NAME>` in `sub`.

   Sources: [configure-aws-credentials README](https://github.com/aws-actions/configure-aws-credentials), [GitHub changelog, immutable subject claims (linked from that README)](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/)
6. **Linting with tflint:**
   - Install with `brew install --cask terraform-linters/tap/tflint` (as written in the README).
   - The Terraform-language ruleset is bundled. Cloud rulesets exist for AWS, Azure and Google; run `tflint --init` to install plugins.

   Source: [tflint README](https://github.com/terraform-linters/tflint)
7. **Security scanning with Trivy:** tfsec says "Going forward we want to encourage the tfsec community to transition over to Trivy" — [tfsec README](https://github.com/aquasecurity/tfsec). Trivy scans "IaC issues and misconfigurations" (`brew install trivy`; e.g. `trivy fs --scanners vuln,secret,misconfig`) — [Trivy README](https://github.com/aquasecurity/trivy). Secondary sources say the usual swap is replacing `tfsec` with `trivy config`, and that TFLint is not a security scanner — [AppSec Santa (search result)](https://appsecsanta.com/iac-security-tools/tfsec-vs-trivy), [env0 (search result)](https://env0.com/blog/top-infrastructure-as-code-security-tools)
8. **Policy scanning with checkov:** "Over 1000 built-in policies", graph-based context-aware scanning, inline suppression; it also scans GitHub Actions workflow files. Install with `pip3 install checkov` or `brew install checkov` — [checkov README](https://github.com/bridgecrewio/checkov)
9. **Terraform Policy (native):** the `-policies` flag on `plan`/`apply`/`query` is GA in 1.17 — [v1.17 CHANGELOG](https://github.com/hashicorp/terraform/blob/v1.17/CHANGELOG.md). HCP Terraform shows a summary of policy evaluation outcomes (1.16) — [v1.16](https://github.com/hashicorp/terraform/blob/v1.16/CHANGELOG.md)
10. **Supply-chain hygiene:** the trivy-action tag hijack (19–20 Mar 2026, CVE-2026-33634). Remediation is to pin to full SHAs and rotate secrets. One analysis argues SHA pinning alone isn't complete protection — [Snyk (search result)](https://snyk.io/articles/trivy-github-actions-supply-chain-compromise/), [BoostSecurity (search result)](https://labs.boostsecurity.io/tactical-guides/2026-03-aquasecurity-trivy-supply-chain-compromise-incident-response-guide)

#### Small examples
OIDC permissions and auth step, from the configure-aws-credentials README:
```yaml
permissions:
  id-token: write
  contents: read
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4            # pin to a SHA in real use
      - uses: hashicorp/setup-terraform@v4   # pin to a SHA in real use
      - uses: aws-actions/configure-aws-credentials@v6.3.0
        with:
          role-to-assume: arn:aws:iam::<ACCOUNT_ID>:role/<plan-role>
          aws-region: us-east-1
      - run: terraform init -input=false
      - run: terraform plan -input=false -out=tfplan
```
(The `contents: read` permission and the `checkout` step are standard additions, not from that README. The `actions/checkout` version was not checked this session.)

Safe first cloud project, sketched from the docs but **not applied** here:
```hcl
provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = { project = "devops-from-zero", owner = "me" }
  }
}
resource "random_pet" "suffix" {}
resource "aws_s3_bucket" "state" { bucket = "tfstate-${random_pet.suffix.id}" }
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}
```
The expected plan pattern is `Plan: 3 to add, 0 to change, 0 to destroy.` (inferred from the resource count; not run).

### Inferences
#### Misconceptions to address
- "CI should run `apply -auto-approve` on every push": apply the reviewed saved plan, or at least require environment approval.
- "Store AWS keys as GitHub secrets": prefer OIDC. There is no static secret to leak.
- "A green scanner means secure": scanners check patterns, not intent. tflint finds mistakes, trivy and checkov find misconfigurations, and none of them replace reading the plan.
- "`@v4` tags are immutable": they're not (the Trivy incident).
- "The free tier means free": S3, KMS, NAT gateways, and EC2 outside the free tier all cost money. Set an AWS Budget alert before the first apply and run `terraform destroy` at the end of each session.

#### Hands-on exercise ideas
1. Offline: run `tflint --init && tflint`, `trivy config .` and `checkov -d .` on the lesson 4 Docker module, then fix or suppress one finding. **Not run here;** trivy may need to download its check bundle.
2. Offline: write `.github/workflows/terraform-plan.yml` that runs `fmt -check`, `validate`, `tflint` and `terraform test` (with the Docker provider mocked) on `pull_request`. No cloud is needed.
3. Optional cloud (cost warning): create a versioned S3 bucket, then migrate lesson 3's state into it with `use_lockfile = true`, then destroy. Expect a few cents or less if destroyed the same day. **This estimate was not verified against AWS pricing.**
4. Optional cloud: create a GitHub OIDC IAM role scoped to `repo:<org>/<repo>:pull_request` for plan only, and a separate apply role scoped to `ref:refs/heads/main` or an environment.

#### Resources (3–8)
- HashiCorp tutorial, "Automate Terraform with GitHub Actions": https://developer.hashicorp.com/terraform/tutorials/automation/github-actions (search result; HCP Terraform-centric)
- aws-actions/configure-aws-credentials README (OIDC setup and trust policy): https://github.com/aws-actions/configure-aws-credentials (opened)
- AWS provider docs, authentication (source): https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown (opened)
- hashicorp/setup-terraform: https://github.com/hashicorp/setup-terraform (opened)
- tflint: https://github.com/terraform-linters/tflint, Trivy: https://github.com/aquasecurity/trivy, checkov: https://github.com/bridgecrewio/checkov (all opened)
- Snyk write-up on the trivy-action compromise, as a "why pin by SHA" case study: https://snyk.io/articles/trivy-github-actions-supply-chain-compromise/ (search result)
- Video: DevOps Directive course, whose final module deploys to AWS with GitHub Actions: https://www.youtube.com/watch?v=7xngnjfIlK4 (search-result description plus repo README)
- Video, unverified channel: "Terraform Course – Automate your AWS cloud infrastructure", https://www.youtube.com/watch?v=lqot1dIOTrs (search result). An aggregator lists a video with the same title under a different ID (SLB_c_ayRMo) and attributes it to freeCodeCamp, so check the channel and ID before linking it.

### Gaps
- No youtube.com URLs for **TechWorld with Nana** or **freeCodeCamp/Andrew Brown** Terraform courses appeared in search results.
  - Nana's course appears only as a dev.to post title, "Complete Terraform Course – Beginner to Advanced [2021]".
  - Andrew Brown's course appears only as Class Central listings, e.g. https://classcentral.com/classroom/freecodecamp-hashicorp-terraform-associate-certification-course-003-pass-the-exam-205805.
  - So neither has a verified video link here.
- The AWS Free Tier rules and S3 pricing in 2026 were not checked, so cost claims are hedged.
- `trivy config` subcommand syntax and offline behaviour weren't verified from Trivy's docs; only the README's `trivy fs --scanners … misconfig` form was seen.
- The HCP Terraform GitHub Actions tutorial content wasn't opened (blocked), so its exact workflow files are unknown.
