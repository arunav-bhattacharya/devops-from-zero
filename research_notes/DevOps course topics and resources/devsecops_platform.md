# DevSecOps, platform engineering and AI in DevOps (course Part 6, 4 lessons), as of 30 October 2026

How the sources were checked (so the lesson writer knows which links are solid):
- **[git]**: version tags read with `git ls-remote` or `git fetch` from github.com on 2026-10-30. Dates are the tagged commit dates.
- **[raw]**: file read in full from raw.githubusercontent.com this session. The link given is the matching `github.com/.../blob/...` page for the same file.
- **[search]**: the URL appeared in a WebSearch result, and only the snippet or summary was seen. The page itself was not opened.
- **Blocked here**: WebFetch/DNS failed for training.linuxfoundation.org, www.finops.org and www.aquasec.com. Those hosts must be allowed in the session's network settings before their figures can be confirmed first-hand. api.github.com was also refused, so release dates come from git tag commits.
- **No YouTube URLs** appeared in any search result. Talks below are linked through the listing pages that did appear (Class Central and similar). The lesson writer should search YouTube for the exact titles before linking them.

---

## Lesson 1: The software supply chain. What should a beginner learn, in what order, and what is current?

### Takeaway
Teach the chain as "know what's in it (SBOM), check it for known holes (scan), prove who built it and how (sign plus provenance/attestation), then verify before you run it". Anchor the lesson in three real incidents. xz-utils (2024) was a malicious maintainer. tj-actions/changed-files (2025) was a hijacked CI dependency. Trivy (March 2026) was a security scanner turned into an attack tool. Current tools as of October 2026: syft v1.55.0, grype v0.121.0, trivy v0.76.1, cosign v3.1.4, SLSA spec v1.2, and GitHub's `actions/attest@v4`.

### Cited Findings

**Concepts in teaching order (one line each, with an intuition)**
1. *Software supply chain*: everything that touches your code between the keyboard and production: dependencies, base images, CI actions, build machines and registries. Intuition: a restaurant depends on its farms, trucks and kitchen, not only its recipe. All three incidents below hit a link other than the app's own code ([CISA tj-actions alert](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066) [search]; [Datadog xz write-up](https://securitylabs.datadoghq.com/articles/xz-backdoor-cve-2024-3094/) [search]).
2. *SBOM (software bill of materials)*: a machine-readable list of every package inside an artifact. Intuition: the ingredient list on a food label. syft writes SBOMs in CycloneDX and SPDX, and can write both at once: `syft <image> -o spdx-json=./spdx.json -o cyclonedx-json=./cdx.json` ([syft README](https://github.com/anchore/syft/blob/main/README.md) [raw]).
   - SPDX and CycloneDX are the two standard formats. GitHub's SBOM attestation verify example uses predicate type `https://spdx.dev/Document/v2.3` ([GitHub docs source: use artifact attestations](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]).
3. *Vulnerability scanning*: matching that ingredient list against databases of known CVEs. Intuition: checking the label against the food-recall list. grype can scan an image, a directory or a saved SBOM: `grype alpine:latest`, `grype ./my-project`, `grype sbom:./sbom.json` ([grype README](https://github.com/anchore/grype/blob/main/README.md) [raw]). Trivy has "scanners" (SBOM/packages, CVEs, IaC misconfigurations, secrets) and "targets": `trivy image python:3.4-alpine`, `trivy fs --scanners vuln,secret,misconfig myproject/`, `trivy k8s --report summary cluster` ([trivy README](https://github.com/aquasecurity/trivy/blob/main/README.md) [raw]).
4. *Signing*: attaching a cryptographic signature so consumers can detect tampering and see who signed. Intuition: a tamper-evident seal on a medicine bottle. Cosign "keyless" signing is the default. It uses the Sigstore public-good Fulcio certificate authority and the Rekor transparency log ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]).
   - How keyless works: cosign makes ephemeral keys, you log in with OIDC, Fulcio issues a short-lived certificate whose subject is your identity, and the signature and certificate go into Rekor and the registry. Verification checks the expected identity and issuer: `cosign verify $IMAGE --certificate-identity=$IDENTITY --certificate-oidc-issuer=$OIDC_ISSUER` ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]).
   - The README warns: "always sign images based on their digest (`@sha256:...`) rather than a tag (`:latest`)". It also warns that your email goes into a public transparency log "and cannot be removed later" ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]).
   - Cosign v3.0.0 turned on by default the newer standardized bundle format, `--trusted-root`/`--signing-config`, and storing signatures as OCI 1.1 referring artifacts. The announcement post is [blog.sigstore.dev/cosign-3-0-available/](https://blog.sigstore.dev/cosign-3-0-available/), linked from the [cosign CHANGELOG](https://github.com/sigstore/cosign/blob/main/CHANGELOG.md) [raw]. The latest tag is v3.1.4 (2026-10-20) [git].
5. *Provenance and attestations*: a signed statement of *how* an artifact was built (which repo, commit, workflow and builder). Intuition: the seal plus a signed delivery note saying which factory and production line made it. `actions/attest-build-provenance` binds a subject (name plus digest) to a SLSA provenance predicate in in-toto format, signed with a short-lived Sigstore certificate ([attest-build-provenance README](https://github.com/actions/attest-build-provenance/blob/main/README.md) [raw]).
6. *SLSA levels*: a checklist ladder for build integrity. Build L0 has no guarantees. L1 means provenance exists, which guards against mistakes. L2 means signed provenance from a hosted build platform, which guards against tampering after the build. L3 means a hardened build platform, which guards against tampering during the build ([SLSA build-track basics source](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md) [raw]).
   - SLSA v1.2 (tag dated 2025-11-24 [git]) is the latest release. It added the **Source Track**, and since RC1, Source L2 focuses on history and provenance while L3 focuses on continuously enforced controls ([SLSA v1.2 "What's new"](https://github.com/slsa-framework/slsa/blob/releases/v1.2/spec/whats-new.md) [raw]). The main branch also drafts a Build Environment track and a Dependency track. Those are not in v1.2 ([SLSA tracks, main](https://github.com/slsa-framework/slsa/blob/main/spec/tracks.md) [raw]).
7. *GitHub artifact attestations*: GitHub's built-in way to make and verify provenance and SBOM attestations, built on Sigstore. On their own they give **SLSA v1.0 Build Level 2**. Building inside a shared **reusable workflow** adds the isolation needed for **Build Level 3** ([GitHub docs source: artifact attestations concept](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]; [GitHub docs: achieve SLSA v1 Build Level 3](https://docs.github.com/actions/security-guides/using-artifact-attestations-and-reusable-workflows-to-achieve-slsa-v1-build-level-3) [search]; [GitHub blog](https://github.blog/enterprise-software/devsecops/enhance-build-security-and-reach-slsa-level-3-with-github-artifact-attestations/) [search]).
   - Public repos use the Sigstore Public Good Instance, so entries land in a public transparency log. Private repos use GitHub's own Sigstore instance, which has no transparency log ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).
   - GitHub's own warning: "Generating attestations alone doesn't provide any security benefit, the attestations must be verified". It adds that attestations "are not a guarantee that an artifact is secure". Sign releases people will run, not every test build ([same](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).
   - **Change to note:** the October 2026 docs use `actions/attest@v4` with `subject-path`, or `subject-name` plus `subject-digest`, and an optional `sbom-path` ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]). The older `actions/attest-build-provenance` (latest v4.2.2 [git]) is described as "internally powered by" `@actions/attest` ([README](https://github.com/actions/attest-build-provenance/blob/main/README.md) [raw]). `actions/attest` latest tag: v4.2.2 [git]; it has a `push-to-registry` input ([actions/attest README](https://github.com/actions/attest/blob/main/README.md) [raw]).

**Real incidents (teach as case studies)**
- **xz-utils backdoor, CVE-2024-3094 (disclosed March 2024).** Malicious code shipped in xz/liblzma releases 5.6.0 and 5.6.1 and targeted `sshd`. CVSS score 10. Andres Freund found it after noticing unusual sshd CPU usage while benchmarking. It is attributed to a contributor known as "Jia Tan" who gained maintainer trust over time. Check with `xz --version` ([Picus](https://www.picussecurity.com/resource/blog/cve-2024-3094-a-backdoor-in-xz-utils-leads-to-remote-code-execution) [search]; [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/xz-backdoor-cve-2024-3094/) [search]; [Uptycs](https://www.uptycs.com/blog/xz-utils-backdoor-vulnerability-cve-2024-3094) [search]). Lesson: an SBOM tells you *whether* you shipped xz 5.6.x. Scanning only helps once a CVE exists.
- **tj-actions/changed-files, CVE-2025-30066 (March 2025).** Attackers moved the action's version tags to a malicious commit (`0e58ed8`, on 2025-03-14 per SentinelOne). The payload dumped CI secrets into workflow logs. Versions before 46 were affected ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-30066) [search]; [CISA alert, 2025-03-18](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066) [search]). StepSecurity Harden-Runner detected it through an unexpected outbound endpoint. It was likely enabled by an earlier compromise of `reviewdog/action-setup@v1` (CVE-2025-30154), and CISA added both CVEs to its KEV catalog ([WaterISAC](https://www.waterisac.org/node/19354) [search]; [The Hacker News, CVSS 8.6](https://thehackernews.com/2025/03/github-action-compromise-puts-cicd.html) [search]; [Wiz](https://threats.wiz.io/all-incidents/tj-actionschanged-files-supply-chain-attack) [search]). Fix: pin actions to full commit SHAs and rotate any exposed secrets.
- **Trivy compromise, CVE-2026-33634 (March 2026; new since most courses were written).** Attackers used credentials that were still valid to publish a malicious Trivy **v0.69.4** binary and to rewrite GitHub Action tags on 19 March 2026. The trivy-action exposure window ran from about 17:43 UTC on 19 March to 05:40 UTC on 20 March. 75 of 76 (or 76 of 77, depending on the count) `trivy-action` tags and all 7 `setup-trivy` tags were replaced. The attack is attributed to "TeamPCP" ([Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]; [Wiz](https://wiz.io/blog/trivy-compromised-teampcp-supply-chain-attack) [search]; [Snyk](https://snyk.io/de/articles/trivy-github-actions-supply-chain-compromise/) [search]; [Aqua blog](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know) [search, fetch blocked]). Root cause: Aqua disclosed an earlier breach on 1 March, but the credential rotation was not atomic. Malicious Docker Hub images v0.69.5 and v0.69.6 followed on 22 March, and `kics-github-action` was also hit ([Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]; [Wiz](https://wiz.io/blog/trivy-compromised-teampcp-supply-chain-attack) [search]; [Legit Security playbook](https://www.legitsecurity.com/blog/the-trivy-supply-chain-compromise-what-happened-and-playbooks-to-respond) [search]). The `v0.69.4` tag no longer resolves in aquasecurity/trivy, while later releases such as v0.76.1 (2026-10-21) do [git].

**Misconceptions (lesson 1)**
- "Scan once at build time and you're done." New CVEs are published against software you have already shipped. xz was only detectable *after* disclosure ([Datadog](https://securitylabs.datadoghq.com/articles/xz-backdoor-cve-2024-3094/) [search]). Keep the SBOM and re-scan it on a schedule: `grype sbom:./sbom.json` ([grype README](https://github.com/anchore/grype/blob/main/README.md) [raw]).
- "Signed means safe." Attestations and signatures prove origin, not quality. GitHub states they "are not a guarantee that an artifact is secure" ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).
- "Generating signatures is enough." Without a verification step (`cosign verify ...`, `gh attestation verify ... -R owner/repo`) they add nothing ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).
- "A version tag like `@v4` is immutable." In both tj-actions and Trivy, attackers repointed existing tags ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-30066) [search]; [Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]).
- "Security tools are trusted by default." The Trivy compromise turned a scanner into the attack tool ([DEV post "Your security scanner was the weapon"](https://dev.to/mateenali66/your-security-scanner-was-the-weapon-inside-the-trivy-supply-chain-attack-2gc) [search]).
- "Sign `:latest`." Sign by digest ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]).

**Example commands and workflow (Mac, all free)**
```bash
brew install syft grype trivy cosign          # each README documents Homebrew install
syft hello-devops:local -o spdx-json=sbom.spdx.json -o cyclonedx-json=sbom.cdx.json
grype sbom:./sbom.spdx.json                   # scan the saved SBOM later, without the image
trivy image hello-devops:local
trivy fs --scanners vuln,secret,misconfig .   # also finds secrets and IaC mistakes
cosign sign-blob app.tar.gz --bundle app.sigstore.json --yes     # keyless; opens browser OIDC
cosign verify-blob app.tar.gz --bundle app.sigstore.json \
  --certificate-identity you@example.com --certificate-oidc-issuer <issuer-url>
gh attestation verify oci://ghcr.io/OWNER/hello-devops:TAG -R OWNER/hello-devops
```
Sources: [syft](https://github.com/anchore/syft/blob/main/README.md), [grype](https://github.com/anchore/grype/blob/main/README.md), [trivy](https://github.com/aquasecurity/trivy/blob/main/README.md) and [cosign](https://github.com/sigstore/cosign/blob/main/README.md) READMEs [raw]; [GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]. Gate flags such as grype `--fail-on high` and trivy `--exit-code 1 --severity HIGH,CRITICAL` are widely used but were **not re-verified this session**.

GitHub Actions step (from GitHub docs, Oct 2026):
```yaml
permissions:
  id-token: write      # OIDC token for keyless Sigstore signing
  contents: read
  attestations: write
  packages: write      # only when pushing images to GHCR
steps:
  - name: Generate artifact attestation
    uses: actions/attest@v4          # course should pin a full commit SHA instead of @v4
    with:
      subject-name: ghcr.io/OWNER/hello-devops   # no tag
      subject-digest: sha256:...                 # digest from the build/push step
  - name: Generate SBOM attestation
    uses: actions/attest@v4
    with:
      subject-path: dist/app
      sbom-path: sbom.spdx.json
```
([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw])

**Hands-on exercise ideas (free and local)**
- Make an SBOM for the course's `hello-devops` image in both formats with syft, then `grep` the JSON for a package name. That is the "ingredient list" made concrete ([syft README](https://github.com/anchore/syft/blob/main/README.md) [raw]).
- Scan the same image with grype and trivy and compare the counts. Then change the base image (for example `python:3.x-slim` to an older tag) and watch the counts move ([grype](https://github.com/anchore/grype/blob/main/README.md), [trivy](https://github.com/aquasecurity/trivy/blob/main/README.md) [raw]).
- Keyless `cosign sign-blob` on a tarball, then tamper with one byte and watch `verify-blob` fail ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]). This needs network access to Sigstore but no account beyond an OIDC login.
- In a GitHub repo (free for public repos), add `actions/attest@v4`, then `gh attestation verify` locally ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]).
- "Pin by SHA" drill: rewrite the course workflow's `uses:` lines from tags to full SHAs. Discuss the tj-actions and Trivy timelines ([CISA](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066) [search]).
- Browser lab: iximiuz "Kubelings" module on SBOM plus cosign ([labs.iximiuz.com](https://labs.iximiuz.com/courses/kubelings-dbd840c8/module-06/sbom-cosign) [search]).

**Curated resources (lesson 1)**
- SLSA build levels (spec): [slsa.dev/spec/v1.0/levels](https://slsa.dev/spec/v1.0/levels) (linked from GitHub docs [raw]); v1.2 changes: [whats-new.md](https://github.com/slsa-framework/slsa/blob/releases/v1.2/spec/whats-new.md) [raw].
- GitHub: [Achieve SLSA v1 Build Level 3 with attestations and reusable workflows](https://docs.github.com/actions/security-guides/using-artifact-attestations-and-reusable-workflows-to-achieve-slsa-v1-build-level-3) [search]; [GitHub blog on SLSA L3 attestations](https://github.blog/enterprise-software/devsecops/enhance-build-security-and-reach-slsa-level-3-with-github-artifact-attestations/) [search].
- Cosign README (keyless sign and verify walkthrough): [github.com/sigstore/cosign](https://github.com/sigstore/cosign/blob/main/README.md) [raw]; [Cosign 3.0 announcement](https://blog.sigstore.dev/cosign-3-0-available/) (linked from CHANGELOG [raw]).
- OpenSSF on the Sigstore public-good instance: [openssf.org blog 2023-10-03](https://openssf.org/blog/2023/10/03/running-sigstore-as-a-managed-service-a-tour-of-sigstores-public-good-instance/) (linked from GitHub docs [raw]); [SigstoreCon 2024 recap](https://openssf.org/blog/2024/12/16/sigstorecon-2024-advancing-software-supply-chain-security/) [search].
- Talk (video): "Life of a Sigstore Signature", Jed Salazar and Zack Newman (Chainguard), about 28 minutes, listing at [Class Central](https://classcentral.com/course/youtube-life-of-a-sigstore-signature-jed-salazar-zack-newman-chainguard-237612) [search]. Also "Make the secure Kubernetes supply chain work for you", Adolfo García Veytia, [Class Central](https://classcentral.com/course/youtube-make-the-secure-kubernetes-supply-chain-work-for-you-adolfo-garcia-veytia-chainguard-237900) [search].
- Incidents: [CISA tj-actions alert](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066) [search]; [Wiz on the Trivy compromise](https://wiz.io/blog/trivy-compromised-teampcp-supply-chain-attack) [search]; [Datadog on xz](https://securitylabs.datadoghq.com/articles/xz-backdoor-cve-2024-3094/) [search].

### Inferences
- The Trivy incident fits this course well. It ties lesson 1 (scanning), CI hygiene (SHA pinning, least-privilege `permissions:`) and lesson 2 (secret rotation) into one story, and it happened after most beginner material was written.
- With `actions/attest@v4` in the docs, new lessons should teach `actions/attest` and mention `attest-build-provenance` only as the older name seen in many blog posts.
- A beginner-friendly order is: SBOM (concrete artifact) → scan (immediate payoff) → sign (seal) → provenance/SLSA (why the seal matters) → verify (the step people skip).

### Gaps
- No primary-source (NVD/GitHub advisory) page was opened for CVE-2025-30066 or CVE-2026-33634. The details come from search summaries of CISA and vendor pages, and the aquasec.com fetch was blocked.
- Grype `--fail-on` and trivy `--exit-code/--severity` flags were not confirmed in the READMEs fetched (they are in each tool's CLI help/docs).
- No YouTube URL surfaced in search for any Sigstore, SBOM or SLSA talk, so the video links are listing pages only.
- The exact "keyless in GitHub Actions" verify values (certificate identity = workflow ref URL, issuer = GitHub's OIDC token issuer) were not re-read from a doc this session. Take them from cosign's or GitHub's docs when writing.

---

## Lesson 2: Secrets, access and policy. What should a beginner learn, and what is current?

### Takeaway
Order the lesson as: Kubernetes Secrets are only base64 → keep secrets out of Git (gitleaks, push protection) → where real secrets live (Vault/OpenBao, cloud secret managers) → how they reach the cluster (External Secrets Operator, Sealed Secrets, SOPS) → who may touch what (RBAC, least privilege) → guardrails at the door (admission control and policy as code with Kyverno or Gatekeeper). 2026 changes to note: Vault 2.x is still BSL with IBM as licensor, while OpenBao is the MPL-2.0 fork under the OpenSSF. Kyverno graduated in the CNCF (March 2026) and **deprecated ClusterPolicy in v1.19 (Aug 2026), with removal planned for v1.20**, so teach the CEL-based `ValidatingPolicy`.

### Cited Findings

**Concepts in teaching order**
1. *A Kubernetes Secret is not encrypted by default.* Secrets are "stored unencrypted in the API server's underlying data store (etcd). Anyone with API access can retrieve or modify a Secret". Anyone who can create a Pod (or a Deployment) in a namespace can read every Secret there. The fixes are encryption at rest, least-privilege RBAC, limiting Secret access to specific containers, and external secret stores ([Kubernetes docs source: Secrets](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]). The same page says a base64 value "is obscured but not secret" (same source). Intuition: base64 is a different alphabet, not a lock. Anyone can `base64 -d`.
2. *Secret scanning*: stop secrets before they enter history. gitleaks scans git history (`gitleaks git -v`), directories (`gitleaks dir -v path`) and stdin. It ships a pre-commit hook (`repo: https://github.com/gitleaks/gitleaks`), supports baselines (`--baseline-path`), and can be skipped with `SKIP=gitleaks git commit ...` ([gitleaks README](https://github.com/gitleaks/gitleaks/blob/master/README.md) [raw]). Latest tag v8.30.1 (2026-03-12) [git].
   - GitHub **push protection** "blocks pushes that contain secrets before they reach your repository". It covers partner (provider) patterns, generic patterns (private keys, connection strings), custom regex patterns, and, in public preview, "generic secrets found with AI". Surfaces include CLI pushes, web UI commits, file uploads, REST API and GitHub MCP server interactions on public repos ([GitHub docs source: push protection](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
   - Push protection *for users* "is enabled by default" and stops you pushing secrets to public repos. Repository-level push protection is off by default, needs GitHub Secret Protection, and by default anyone with write access can bypass it by giving a reason ([same](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
3. *Secrets managers*: one audited place that issues, rotates and revokes secrets. Intuition: a bank vault with a sign-in sheet, instead of keys under doormats.
   - **HashiCorp Vault**: the license is the Business Source License, the licensor is now **IBM**, and it covers "Vault Version 1.15.0 or later". Production use is allowed unless you offer Vault to third parties hosted or embedded "to compete with IBM Corp's paid version(s)" ([Vault LICENSE](https://github.com/hashicorp/vault/blob/main/LICENSE) [raw]). **Vault 2.0.0 shipped 14 April 2026**. 2.2.0 (15 Oct 2026) removed `cap_ipc_lock` from the container build, so operators must set `disable_mlock = true`. 2.2.1 shipped 22 Oct 2026 ([Vault CHANGELOG](https://github.com/hashicorp/vault/blob/main/CHANGELOG.md) [raw]). IBM completed its HashiCorp acquisition in early 2025 ([WZ-IT comparison](https://wz-it.com/en/blog/openbao-vs-vault-comparison/) [search]).
   - **OpenBao**: an MPL-2.0 fork ([OpenBao LICENSE](https://github.com/openbao/openbao/blob/main/LICENSE) [raw]) of Vault 1.14, the last MPL release, made after the 2023 BSL switch ([jorijn.com](https://jorijn.com/en/blog/hashicorp-vault-vs-openbao/) [search]). It is governed under the **OpenSSF**: security contact on lists.openssf.org and OpenSSF-named chat channels ([OpenBao README](https://github.com/openbao/openbao/blob/main/README.md) [raw]). Secondary sources say it joined the OpenSSF as a sandbox project in June 2025 and is not a CNCF project ([jorijn.com](https://jorijn.com/en/blog/hashicorp-vault-vs-openbao/) [search]). Latest v2.7.2 (2026-10-26) [git]. Website: www.openbao.org (from README [raw]).
   - **Cloud secret managers** (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault) are all providers that SOPS can encrypt with via KMS/Key Vault ([SOPS README](https://github.com/getsops/sops/blob/main/README.rst) [raw]) and that ESO can sync from (ESO's purpose is syncing provider secrets through `SecretStore` resources: [ESO getting started](https://github.com/external-secrets/external-secrets/blob/main/docs/introduction/getting-started.md) [raw]).
4. *Getting secrets into the cluster without Git leaks.* Three patterns:
   - **External Secrets Operator (ESO)**: a `SecretStore`/`ClusterSecretStore` describes the provider, and an `ExternalSecret` says which keys to copy into a normal Kubernetes Secret on a `refreshInterval`. Intuition: a courier who fetches the key from the bank each hour. API `external-secrets.io/v1`. A built-in **`fake` provider** returns static values, which suits laptop practice ([ESO fake provider docs](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md) [raw]). ESO hit v1.0.0 on 2025-11-07 and is at v2.14.0 (2026-10-23) [git].
   - **Sealed Secrets**: `kubeseal` encrypts with the cluster controller's public key so "only the controller can decrypt". The `SealedSecret` is safe to commit, and the controller creates the real Secret (`kubeseal -f mysecret.json -w mysealedsecret.json`; `kubectl create -f mysealedsecret.json`; `brew install kubeseal`) ([Sealed Secrets README](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md) [raw]). Intuition: a one-way mailbox slot. Latest v0.41.2 (2026-10-26) [git].
   - **SOPS**: "an editor of encrypted files" for YAML, JSON, ENV, INI and binary. It encrypts values (keys stay readable) with AWS KMS, GCP KMS, Azure Key Vault, HuaweiCloud KMS, **age** or PGP ([SOPS README](https://github.com/getsops/sops/blob/main/README.rst) [raw]). Latest v3.13.3 (2026-07-23) [git].
5. *Kubernetes RBAC basics*: Role/ClusterRole (verbs on resources) bound to users or ServiceAccounts with a RoleBinding/ClusterRoleBinding. The official good-practice rules: assign at namespace level with RoleBindings where possible; "avoid providing wildcard permissions ... providing wildcard access gives rights not just to all object types that currently exist in the cluster, but also to all object types which are created in the future"; don't use `cluster-admin` except where needed ([Kubernetes docs source: RBAC good practices](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]). The same page warns that `get` on `nodes/proxy` is not read-only. Intuition: hotel key cards that open only your floor, not a master key.
6. *Least privilege* across the board: CI `permissions:` blocks (lesson 1), RBAC, cloud IAM, and agent and MCP tokens (lesson 3). The Kubernetes RBAC page frames it as "minimal RBAC rights ... only permissions explicitly required" ([source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
7. *Admission control*: the API server's last checkpoint, which can reject or modify objects before they are stored. Intuition: a bouncer at the door checking every object against house rules. Kubernetes has built-in `ValidatingAdmissionPolicies` and `MutatingAdmissionPolicies`. Kyverno "does not replace" these but adds reporting, exceptions and background scans. It also does not replace RBAC: "RBAC controls access while Kyverno enforces policy compliance" ([Kyverno README](https://github.com/kyverno/kyverno/blob/main/README.md) [raw]).
8. *Policy as code*: rules in version-controlled files, tested in CI and enforced by an admission controller.
   - **Kyverno**: the CNCF announced its **graduation on 24 March 2026** at KubeCon EU Amsterdam (TOC vote 16 March), as the 35th graduated project ([CNCF announcement](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/) [search]; [jorijn.com](https://jorijn.com/en/blog/kyverno-cncf-graduation-kubernetes-policy/) [search]). Note: the repo README still says "CNCF Incubating" ([README](https://github.com/kyverno/kyverno/blob/main/README.md) [raw]), which is stale text. 1.17 (2 Feb 2026) promoted CEL policy types to `v1` and marked `ClusterPolicy`/`CleanupPolicy` deprecated ([Kyverno 1.17 post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.17/index.md) [raw]). **1.19 (20 Aug 2026) reached full CEL feature parity and officially deprecated `ClusterPolicy`, `Policy`, `CleanupPolicy`, `ClusterCleanupPolicy` and the legacy PolicyException. "v1.19 is the final release with full support". Removal is planned for v1.20 (est. Nov 2026)** ([Kyverno 1.19 post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]). The 1.17 post had estimated removal in Oct 2026, so the date has slipped once. Latest tag v1.19.2 (2026-10-21), and no v1.20 tag yet [git].
   - **OPA Gatekeeper**: writes policies in Rego via `ConstraintTemplate` CRDs and instantiates them as "constraints". It also offers mutation, audit, external data and a shared policy library ([Gatekeeper README](https://github.com/open-policy-agent/gatekeeper/blob/master/README.md) [raw]; library at [open-policy-agent.github.io/gatekeeper-library](https://open-policy-agent.github.io/gatekeeper-library/website/), linked from README). Latest Gatekeeper v3.23.1 (2026-08-27); OPA v1.22.0 [git].

**Misconceptions (lesson 2)**
- "base64 is encryption." It is "obscured but not secret" ([K8s Secret docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]). Sealed Secrets' README even annotates `foo: YmFy  # <- base64 encoded "bar"` ([README](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md) [raw]).
- "Deleting the secret in a later commit removes it." gitleaks scans *history* (`gitleaks git`) precisely because old commits keep it ([gitleaks README](https://github.com/gitleaks/gitleaks/blob/master/README.md) [raw]). The tj-actions advice was to rotate exposed secrets, not only remove them ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-30066) [search]).
- "Only people with `get secrets` can read Secrets." Anyone who can create a Pod or Deployment in the namespace can read them ([K8s docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]).
- "`*` in RBAC is a harmless shortcut." It also grants future resource types ([RBAC good practices source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
- "Kyverno or Gatekeeper replaces RBAC." No: RBAC controls access and policy engines enforce compliance ([Kyverno README](https://github.com/kyverno/kyverno/blob/main/README.md) [raw]).
- "Push protection means I'm covered." Users can bypass with a reason, and repo-level protection is off by default ([GitHub docs source](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
- "Copy a 2024 Kyverno tutorial." Many use `kind: ClusterPolicy`, which is deprecated as of 1.19 ([1.19 post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]).

**Example commands and manifests**
```bash
# The base64 "aha" moment (standard kubectl syntax; not re-verified this session)
kubectl create secret generic db --from-literal=password=hunter2
kubectl get secret db -o jsonpath='{.data.password}' | base64 -d     # prints hunter2

# Secret scanning
brew install gitleaks
gitleaks git -v .                  # whole history
gitleaks dir -v ./k8s              # files only

# Sealed Secrets
brew install kubeseal
kubeseal -f mysecret.json -w mysealedsecret.json && kubectl create -f mysealedsecret.json

# RBAC check (standard kubectl; not re-verified this session)
kubectl auth can-i --list --as=system:serviceaccount:dev:hello-devops -n dev
```
Sources: [gitleaks](https://github.com/gitleaks/gitleaks/blob/master/README.md) and [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md) READMEs [raw]; [K8s Secret docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) (shows `... -o jsonpath='{.data.*}' | base64 -d`) [raw].

ESO with the fake provider (works on kind with no cloud account):
```yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata: { name: fake }
spec:
  provider:
    fake:
      data:
      - key: "/foo/bar"
        value: "HELLO1"
        version: "v1"
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata: { name: example }
spec:
  refreshInterval: 1h0m0s
  secretStoreRef: { name: fake, kind: ClusterSecretStore }
  target: { name: secret-to-be-created }
  data:
  - secretKey: foo_bar
    remoteRef: { key: /foo/bar, version: v1 }
```
([ESO fake provider snippets](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md) [raw])

Kyverno (CEL, the current style) from the official quick start:
```bash
helm repo add kyverno https://kyverno.github.io/kyverno/ && helm repo update
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```
```yaml
apiVersion: policies.kyverno.io/v1
kind: ValidatingPolicy
metadata:
  name: require-labels
spec:
  validationActions: [Deny]
  autogen:
    podControllers:
      controllers: [deployments]
  matchConstraints:
    resourceRules:
      - apiGroups: ['']
        apiVersions: ['v1']
        operations: ['CREATE', 'UPDATE']
        resources: ['pods']
  validations:
    - message: "label 'team' is required"
      expression: "has(object.metadata.labels) && has(object.metadata.labels.team) && object.metadata.labels.team != ''"
```
Then `kubectl create deployment nginx --image=nginx` is denied with `label 'team' is required` ([Kyverno quick start source](https://github.com/kyverno/website/blob/main/src/content/docs/docs/introduction/quick-start.md) [raw]). The browser playground at [playground.kyverno.io](https://playground.kyverno.io/) supports the new policy types (linked from the 1.19 post [raw]).

**Hands-on exercise ideas**
- Plant a fake AWS-style key in a throwaway repo, run `gitleaks git -v`, then add the pre-commit hook and watch it block the commit ([gitleaks README](https://github.com/gitleaks/gitleaks/blob/master/README.md) [raw]). Optionally push to a public GitHub repo and watch push protection, which is on by default for users ([GitHub docs source](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
- Create a Secret, decode it with `base64 -d`, then show that a user who can only create Pods can still read it, using a Pod that mounts it ([K8s docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]).
- Compare three ways to get one DB password into kind: ESO fake provider, Sealed Secrets, SOPS plus age. Which file is safe to commit in each? ([ESO](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md), [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md), [SOPS](https://github.com/getsops/sops/blob/main/README.rst) [raw]).
- RBAC: give the app's ServiceAccount a Role that can only `get` one ConfigMap. Check with `kubectl auth can-i`, then try `*` and discuss the "future resource types" warning ([RBAC good practices source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
- Install Kyverno with Helm on kind, apply the `require-labels` ValidatingPolicy, and fix the course Deployment to pass ([Kyverno quick start source](https://github.com/kyverno/website/blob/main/src/content/docs/docs/introduction/quick-start.md) [raw]).
- Optional local Vault/OpenBao dev server, just to read and write one secret. Exact dev-mode commands were not re-verified this session.

**Curated resources (lesson 2)**
- Kubernetes docs: Secrets ([source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md)) and RBAC good practices ([source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md)) [raw].
- GitHub push protection ([docs source](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md)) [raw]; gitleaks README ([GitHub](https://github.com/gitleaks/gitleaks/blob/master/README.md)) [raw].
- External Secrets Operator ([README](https://github.com/external-secrets/external-secrets/blob/main/README.md), [fake provider](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md)) [raw]; Sealed Secrets ([README](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md)) [raw]; SOPS ([README](https://github.com/getsops/sops/blob/main/README.rst)) [raw].
- Kyverno: [quick start source](https://github.com/kyverno/website/blob/main/src/content/docs/docs/introduction/quick-start.md), [1.19 release post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]; [CNCF graduation announcement](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/) [search]; [The New Stack interview on graduation](https://thenewstack.io/kyverno-cncf-graduation-interview/) [search].
- Gatekeeper: [README](https://github.com/open-policy-agent/gatekeeper/blob/master/README.md) [raw]; [install docs](https://open-policy-agent.github.io/gatekeeper/website/docs/install) (linked from README).
- Vault vs OpenBao: [Vault LICENSE](https://github.com/hashicorp/vault/blob/main/LICENSE), [OpenBao README](https://github.com/openbao/openbao/blob/main/README.md) [raw]; [jorijn.com comparison](https://jorijn.com/en/blog/hashicorp-vault-vs-openbao/) [search].

### Inferences
- For a beginner course in late 2026, Kyverno's CEL `ValidatingPolicy` is the better teaching choice. It is YAML-only, its CEL matches Kubernetes' own ValidatingAdmissionPolicy, and `ClusterPolicy` is about to be removed. Mention Gatekeeper/Rego as "the other major option, especially where OPA is already used".
- ESO's `fake` provider gives the "secrets manager" pattern a fully local exercise. A local Vault/OpenBao dev server can be an optional stretch.
- For licensing, the plain-language teaching point is: Vault is "source-available (BSL)" and free for most internal use, while OpenBao is "open source (MPL-2.0)". Avoid legal advice.

### Gaps
- No source was opened for Gatekeeper's 2026 project status or OPA governance changes. OPA is CNCF-graduated per general knowledge, but this was not verified this session.
- ESO's and SOPS's CNCF maturity level was not verified. ESO uses CNCF mailing lists and the SOPS README shows a CNCF logo, but no level is stated.
- No exact Vault/OpenBao dev-mode command text was re-read this session.
- The version in which Kubernetes ValidatingAdmissionPolicy went GA was not re-checked (the Kyverno README confirms VAP and MAP exist).

---

## Lesson 3: Platform engineering, developer experience, FinOps and AI in DevOps. What is the consensus and what is current?

### Takeaway
A platform is an internal product. It succeeds when developers *choose* it (golden paths and self-service), not when it is mandated. The CNCF maturity model gives a 5-aspect by 4-level self-check. Backstage is still the main open-source portal framework (CNCF incubating, v1.56.2). FinOps keeps Inform → Optimize → Operate and has widened to "Scopes" and "Cloud+", with a 2026 framework refresh. For AI, DORA 2025 calls AI an "amplifier" of existing strengths and weaknesses. GitHub's agent docs and the official MCP servers all build guardrails in: read-only by default, opt-in writes, and humans reviewing PRs.

### Cited Findings

**Concepts in teaching order**
1. *Platform engineering and the internal developer platform (IDP)*: "the practice of planning and providing such computing platforms to developers and users", covering their people, processes, policies and technology ([CNCF maturity model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). Read the CNCF Platforms White Paper first ([tag-app-delivery.cncf.io/whitepapers/platforms/](https://tag-app-delivery.cncf.io/whitepapers/platforms/), linked from the model [raw]). Intuition: an internal "cloud" that your own team runs for your developers.
2. *Golden paths / paved roads*: "'Paved roads' or 'golden paths', in the form of documentation and templates, are provided. These ... define how to provision and manage typical capabilities using compliant and tested patterns" ([CNCF maturity model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). Intuition: a paved road through a field. You *can* walk through the mud, but most people take the road because it's faster.
3. *Platform as a product*: at the "Scalable" investment level, "Product management and user experience are explicitly considered and invested in". At the "Scalable" adoption level ("Intrinsic pull"), teams gather user feedback, share roadmaps and hold open forums ([same](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). CNCF TAG App Delivery also publishes "platform-as-a-product" research material (interview scripts and survey data) ([repo listing](https://github.com/cncf/tag-app-delivery) [git]).
4. *CNCF Platform Engineering Maturity Model*: published October 2023 (v1) at [tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model) ([repo README](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/README.md) [raw]). Aspects and levels (Provisional → Operational → Scalable → Optimizing):
   - Investment: Voluntary or temporary → Dedicated team → As product → Enabled ecosystem
   - Adoption: Erratic → Extrinsic push → Intrinsic pull → Participatory
   - Interfaces: Custom processes → Standard tooling → Self-service solutions → Integrated services
   - Operations: By request → Centrally tracked → Centrally enabled → Managed services
   - Measurement: Ad hoc → Consistent collection → Insights → Quantitative and qualitative

   ([model table source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). A Sept 2026 CNCF blog says many teams stall at level 2 for Interfaces and that the model diagnoses where you are rather than prescribing next steps ([CNCF blog 2026-09-01](https://www.cncf.io/blog/2026/09/01/platform-engineering-maturity-from-toolchain-to-self-service/) [search]). Each aspect is scored separately, and you need not aim for level 4 everywhere ([heise](https://heise.de/-10397214) [search]).
   - Caution: a KodeKloud study note lists different "dimensions" (Provisioning, Development, Security…), which contradicts the official table ([KodeKloud notes](https://notes.kodekloud.com/docs/Prep-Course-Certified-Cloud-Native-Platform-Engineering-Associate-CNPA/Domain-6-Measuring-Your-Platform/Platform-Maturity-Models/page) [search]). Use the official table.
5. *Backstage*: "an open source framework for building developer portals" with a Software Catalog, Software Templates (golden-path scaffolding), TechDocs ("docs like code") and plugins. Created by Spotify, it is a CNCF **Incubation** project ([Backstage README](https://github.com/backstage/backstage/blob/master/README.md) [raw]). Latest v1.56.2 (2026-10-22) [git]. There is now a **Certified Backstage Associate (CBA)** exam curriculum ([cncf/curriculum README](https://github.com/cncf/curriculum/blob/master/README.md) [raw]). Intuition: Backstage is the shop front, not the shop. The platform is the capabilities behind it.
6. *Developer experience (DevEx)*: measured through the model's Measurement aspect. At "Provisional", "users believe their feedback isn't considered" ([maturity model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). DORA 2025 finds AI gains depend on platform quality and fast feedback loops ([DORA AI research page](https://www.dora.dev/research/ai) [search]; [Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) [search]).
7. *FinOps*: the FinOps Foundation framework keeps three iterative phases, **Inform** (visibility and allocation), **Optimize** (rates and usage) and **Operate** (continuous improvement). The phases are not a strict sequence ([finops.org lifecycle](https://www.finops.org/framework/lifecycle/) [search]; [Microsoft Learn FinOps framework](https://learn.microsoft.com/cloud-computing/finops/framework/finops-framework) [search]). **Scopes** were approved as a framework element in Oct 2024 (Public Cloud was an initial Scope), extending FinOps to "Cloud+". The **2026 framework refresh (March 2026)** updated the FinOps definition and added one Capability, **"Executive Strategy Alignment"**, in the "Manage the FinOps Practice" domain ([finops.org 2026 framework post](https://www.finops.org/insights/2026-finops-framework/) [search; fetch blocked]). Intuition: an itemised phone bill shared with whoever runs up the charges.
8. *AI in DevOps: the evidence.* The DORA 2025 "State of AI-assisted Software Development" report surveyed nearly 5,000 technology professionals. It reports about 90% AI adoption, a median of about 2 hours a day spent with AI tools, and 65% relying "heavily" on AI. Its main framing: AI "is an amplifier", strengthening high performers and worsening dysfunction. AI adoption is now linked to higher delivery *throughput*, but instability remains. The report also offers seven team profiles and a "DORA AI Capabilities Model" of seven foundational practices ([Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) [search]; [Google blog](https://blog.google/technology/developers/dora-report-2025/) [search]; [dora.dev report page](https://dora.dev/dora-report-2025/) [search]; [research.google](https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/) [search]; [TechRepublic](https://www.techrepublic.com/article/news-dora-ai-report-2025/) [search]). One blogger reads it as "only two of seven profiles benefit". That is his interpretation, not DORA's headline ([Rob Bowley](https://blog.robbowley.net/2025/10/01/dora-2025-ai-assisted-dev-report-some-benefit-most-dont/) [search]).
9. *AI coding agents in pull requests*: GitHub's docs define an agent as a system that can "plan a task, use tools to take action, inspect the results, and adjust its approach". It runs in collaborative, asynchronous or automated modes. "In every case, you remain responsible for defining the goal and constraints, granting appropriate access, and reviewing the agent's work" ([GitHub docs source: about Copilot agents](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) [raw]). GitHub also documents third-party coding agents ([file listing](https://github.com/github/docs/tree/main/content/copilot/concepts/agent-capabilities/about-agents) [git]).
   - **GitHub Agentic Workflows**: repository automations written in Markdown that run as GitHub Actions. Guardrails go in frontmatter (triggers, permissions, "safe outputs"). Agents run "in firewalled containers with read-only tokens by default". Write actions are limited to declared safe outputs and checked by "agentic threat detection". Engines include Copilot, Claude, OpenAI Codex and Gemini. Use cases: issue triage, investigating CI failures, status reports, doc updates, test coverage ([GitHub docs source: agentic workflows](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows.md) [raw]).
10. *MCP servers for DevOps tools* (MCP, Model Context Protocol, lets an AI assistant call tools). Intuition: giving an intern a badge. Decide which doors it opens before handing it over.
    - **GitHub MCP Server** (latest v2.0.3 [git]): `--read-only` (or `GITHUB_READ_ONLY=1`) "will only offer read-only tools". Read-only "takes priority" even if write tools are requested. `--toolsets repos,issues,...` limits capability groups. "Lockdown mode" limits public-repo content to authors with push access ([README](https://github.com/github/github-mcp-server/blob/main/README.md) [raw]). Push protection also scans GitHub MCP server interactions on public repos ([GitHub docs source](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
    - **HashiCorp Terraform MCP Server** (v1.4.1 [git]): `ENABLE_TF_OPERATIONS` ("Enable tools that require explicit approval") defaults to `false`, and `MCP_ORGANIZATION_ALLOWLIST` restricts HCP Terraform orgs. The README cautions that outputs "may vary" and should be reviewed thoroughly ([README](https://github.com/hashicorp/terraform-mcp-server/blob/main/README.md) [raw]).
    - **Kubernetes MCP server** (`containers/kubernetes-mcp-server`, a community/Red Hat-led project, not an official Kubernetes SIG project; v0.1.1 [git]): config `read_only = true`, `toolsets = [...]`. It uses your kubeconfig, and for production the README points to a "dedicated ServiceAccount and read-only access" ([README](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) [raw]). Read-only flags don't shrink the server's credentials: it inherits your kubectl context's rights, so RBAC still matters ([Tailscale on Kubernetes MCP](https://tailscale.com/learn/kubernetes-mcp) [search]; [Stacklok ToolHive guide](https://docs.stacklok.com/toolhive/guides-mcp/k8s) [search]).
11. *AI-assisted incident response*: practitioner consensus, mostly from vendor blogs, so treat it as opinion. AI speeds up investigation (log, metric and runbook correlation, timeline and summary drafts). Humans approve production mutations, rollbacks, severity changes, customer updates and final root-cause conclusions ([Rootly](https://rootly.com/blog/ai-driven-incident-response-best-practices-for-sres) [search]; [DZone guardrails](https://dzone.com/articles/ai-sre-agents-guardrails) [search]; [SoftwareSeni](https://www.softwareseni.com/what-ai-sre-agents-actually-do-in-an-incident-and-when-you-should-not-deploy-one) [search]). DZone's line: agents should not merge PRs, deploy, rotate secrets, change IAM, delete infrastructure or suppress alerts in production. "Human approval is not a temporary limitation. It is part of the architecture" ([DZone](https://dzone.com/articles/ai-sre-agents-guardrails) [search]).

**Misconceptions (lesson 3)**
- "Build the portal and they'll come." The model calls mandated, pushed adoption level 2 ("Extrinsic push"). Maturity is "Intrinsic pull", backed by feedback, roadmaps and forums ([model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
- "Platform engineering = installing Backstage." Backstage is a *framework for building portals* ([README](https://github.com/backstage/backstage/blob/master/README.md) [raw]). The model's Interfaces aspect is about self-service capabilities, not a UI ([model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
- "Golden path = the only allowed path." The model describes paved roads as documentation and templates of "compliant and tested patterns". They make the safe path the easy one, not the only one ([model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
- "Aim for level 4 in everything." Not required ([heise](https://heise.de/-10397214) [search]; [CNCF blog](https://www.cncf.io/blog/2026/09/01/platform-engineering-maturity-from-toolchain-to-self-service/) [search]).
- "FinOps = cutting costs." It is a continuous, iterative practice of visibility, optimization and operation, now beyond public cloud ([finops.org lifecycle](https://www.finops.org/framework/lifecycle/) [search]).
- "AI will fix a weak delivery process." DORA: AI amplifies what is there, and gains depend on loosely coupled systems and fast feedback ([Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) [search]; [dora.dev/research/ai](https://www.dora.dev/research/ai) [search]).
- "An agent's PR is reviewed by the agent." GitHub says you remain responsible for reviewing it ([GitHub docs source](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) [raw]).
- "A read-only MCP flag means the AI can't do damage." The server inherits whatever the credentials allow ([Tailscale](https://tailscale.com/learn/kubernetes-mcp) [search]). Scope the token and kubeconfig too ([k8s MCP README](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) [raw]).

**Example commands and config**
```bash
# GitHub MCP server, read-only and narrowed (from README)
github-mcp-server --read-only --toolsets repos,issues,pull_requests,actions
# or env: GITHUB_READ_ONLY=1  GITHUB_TOOLSETS="repos,issues,pull_requests"

# Terraform MCP server: approval-requiring tools stay off unless ENABLE_TF_OPERATIONS=true (default false)
```
```toml
# kubernetes-mcp-server config (TOML), from README
read_only = true
toolsets = ["core", "config", "helm"]
```
Sources: [github-mcp-server README](https://github.com/github/github-mcp-server/blob/main/README.md), [terraform-mcp-server README](https://github.com/hashicorp/terraform-mcp-server/blob/main/README.md), [kubernetes-mcp-server README](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) [raw].

**Hands-on exercise ideas**
- Score the course's own setup (or a past employer's) on the 5 aspects × 4 levels table, then name one change that moves one aspect up a level ([model table source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
- Write a "golden path" for `hello-devops`: a template repo with Dockerfile, CI (SBOM, scan, sign), Kubernetes manifests that pass the Kyverno policy, and a README. Optionally register it as a Backstage `catalog-info.yaml` entity and Software Template ([Backstage README](https://github.com/backstage/backstage/blob/master/README.md) [raw]; the Backstage local quick-start commands were not re-verified this session).
- FinOps "Inform" on kind: require a `team` label (lesson 2's Kyverno policy), then total CPU and memory *requests* per team with kubectl. Discuss allocation, the first FinOps capability ([finops.org lifecycle](https://www.finops.org/framework/lifecycle/) [search]).
- AI guardrails lab: run the Kubernetes MCP server with `read_only = true` against kind under a ServiceAccount bound to the `view` ClusterRole. Ask an assistant "why is my pod CrashLooping?" and confirm it can read but not delete ([k8s MCP README](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) [raw]).
- PR review drill: give learners an AI-generated PR with a subtle wildcard RBAC or `:latest` image, and have them catch it with the lesson 2 policy before merge ([GitHub agents docs source](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) [raw]).
- Incident drill: give an assistant logs from a broken deploy and have it draft a timeline and hypotheses. The learner decides on the rollback and writes the final root cause ([Rootly](https://rootly.com/blog/ai-driven-incident-response-best-practices-for-sres) [search]).

**Curated resources (lesson 3)**
- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) and [Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model) (both linked from TAG repo files [raw]); [CNCF blog, Sept 2026, "Platform engineering maturity: from toolchain to self-service"](https://www.cncf.io/blog/2026/09/01/platform-engineering-maturity-from-toolchain-to-self-service/) [search].
- Backstage: [README](https://github.com/backstage/backstage/blob/master/README.md) [raw]; [Software Catalog docs](https://backstage.io/docs/features/software-catalog/), [Software Templates docs](https://backstage.io/docs/features/software-templates/) and [roadmap](https://backstage.io/docs/overview/roadmap) (linked from README).
- FinOps: [2026 FinOps Framework post](https://www.finops.org/insights/2026-finops-framework/) [search]; [FinOps lifecycle/phases](https://www.finops.org/framework/lifecycle/) [search]; [Microsoft Learn FinOps framework explainer](https://learn.microsoft.com/cloud-computing/finops/framework/finops-framework) [search].
- DORA 2025 AI report: [dora.dev/dora-report-2025](https://dora.dev/dora-report-2025/) and [dora.dev/research/ai](https://www.dora.dev/research/ai) [search]; [Google blog summary](https://blog.google/technology/developers/dora-report-2025/) [search].
- GitHub: [About Copilot agents](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) and [Agentic Workflows](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows.md) (docs sources) [raw].
- MCP servers: [github-mcp-server](https://github.com/github/github-mcp-server), [terraform-mcp-server](https://github.com/hashicorp/terraform-mcp-server), [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server) [raw/git].
- AI SRE guardrails (opinion): [DZone, AI SRE agents guardrails](https://dzone.com/articles/ai-sre-agents-guardrails) [search].

### Inferences
- The best single frame for lesson 3 is "same guardrails, new actor". The least privilege, policy-as-code and review gates from lessons 1–2 apply unchanged to AI agents: read-only tokens, scoped kubeconfig/RBAC, safe outputs, and humans merging. GitHub Agentic Workflows and all three MCP servers ship with that model.
- For an engineer new to DevOps, the platform-engineering takeaway is the *user* lens, not tooling. Learners already use "platforms" (GitHub, Heroku-style PaaS), so the lesson can ask "what would make you choose an internal one?"
- FinOps fits the course as one cost-allocation exercise (labels → per-team requests) more than as theory.

### Gaps
- finops.org was blocked, so the FinOps principles text, personas, maturity terms (Crawl/Walk/Run) and the exact 2026 domain names were not confirmed first-hand. Third-party claims of "four domains" were not verified.
- OpenCost/Kubecost (cost visibility on Kubernetes) were not researched this session. Their CNCF status and versions are unverified.
- No independent, non-vendor outcome data was found on AI-assisted incident response (MTTR effects etc.). The available sources are vendor blogs.
- The DORA 2025 figures come from search summaries of Google/DORA pages. The full report PDF was not opened.
- Backstage's local quick-start command (`npx @backstage/create-app`) and new-frontend-system status were not re-verified.

---

## Lesson 4: The capstone and career. What should the project checklist cover, and what are the current certifications (formats, providers, costs)?

### Takeaway
The capstone should take `hello-devops` through the whole secure path: clean repo → pinned, least-privilege CI → SBOM + scan + sign + attest → policy-checked deploy → secrets from a store → observable, labelled and cost-attributed → AI helpers that are read-only. Certifications: the CNCF/Linux Foundation track (KCNA → KCSA → CKAD/CKA → CKS) has open, versioned curricula on GitHub (CKA/CKAD now on Kubernetes v1.37). The newer CNPA/CNPE and CBA cover platform engineering. HashiCorp's Terraform Associate is version **004**. Prices were found only on third-party pages, except Terraform's (from HashiCorp's page via search). The LF training site was blocked here.

### Cited Findings

**End-to-end capstone checklist (each item maps to a lesson source)**
1. Repo hygiene: gitleaks pre-commit hook plus a history scan; push protection on ([gitleaks README](https://github.com/gitleaks/gitleaks/blob/master/README.md); [GitHub push protection source](https://github.com/github/docs/blob/main/content/code-security/concepts/secret-security/push-protection.md) [raw]).
2. CI: every third-party action pinned to a full commit SHA (the tj-actions/Trivy lesson) ([Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]). Minimal `permissions:` (only `id-token: write`/`attestations: write`/`packages: write` where needed) ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]).
3. Build → SBOM in SPDX and CycloneDX with syft ([syft README](https://github.com/anchore/syft/blob/main/README.md) [raw]).
4. Scan with grype or trivy and fail on agreed severities. Re-scan the stored SBOM on a schedule ([grype README](https://github.com/anchore/grype/blob/main/README.md) [raw]).
5. Sign the image by digest with cosign keyless, attest provenance and the SBOM with `actions/attest@v4`, and verify with `gh attestation verify` / `cosign verify` ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md); [GitHub docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]). Stretch: move the build into a reusable workflow for SLSA Build L3 ([GitHub docs](https://docs.github.com/actions/security-guides/using-artifact-attestations-and-reusable-workflows-to-achieve-slsa-v1-build-level-3) [search]).
6. Secrets: no plaintext Secret in Git. Use ESO (fake provider locally), Sealed Secrets or SOPS+age ([ESO](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md), [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md), [SOPS](https://github.com/getsops/sops/blob/main/README.rst) [raw]).
7. Access: a dedicated ServiceAccount, a namespaced Role with no wildcards, and no `cluster-admin` ([RBAC good practices source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
8. Admission policy: a Kyverno `ValidatingPolicy` requiring a `team` label (and optionally signed images). Test the policies in CI with the Kyverno CLI ([Kyverno quick start](https://github.com/kyverno/website/blob/main/src/content/docs/docs/introduction/quick-start.md); [1.19 post: CLI tests reusable](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]).
9. Platform touch: the repo itself is a "golden path" template (docs plus template) ([CNCF maturity model](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
10. FinOps: `team` labels enable per-team cost allocation (Inform phase) ([finops.org lifecycle](https://www.finops.org/framework/lifecycle/) [search]).
11. AI: any MCP server used is in read-only mode with narrowed toolsets and a scoped ServiceAccount, and every AI PR gets human review ([github-mcp-server](https://github.com/github/github-mcp-server/blob/main/README.md), [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) READMEs; [GitHub agents doc source](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) [raw]).

**Certifications: what the sources say**

*Official curricula (CNCF, CC-BY 4.0, repo updated 2026-10-15)*: [cncf/curriculum](https://github.com/cncf/curriculum) [raw]. It lists CKA, CKAD, CKS, CGOA, CAPA, **CBA (Backstage)**, **CNPA**, **CNPE**, CCA (Cilium), ICA (Istio), **KCA (Kyverno)**, KCNA, KCSA, OTCA (OpenTelemetry) and PCA ([README](https://github.com/cncf/curriculum/blob/master/README.md) [raw]). Curriculum version numbers match the Kubernetes version. Current files: `CKA_Curriculum_v1.37.pdf`, `CKAD_Curriculum_v1.37.pdf`, `CKS_Curriculum v1.34.pdf` [git listing].

| Cert | Provider | Domains and weights (official curriculum) | Format / cost (source and caveat) |
|---|---|---|---|
| **KCNA** (Kubernetes and Cloud Native Associate) | Linux Foundation / CNCF | K8s Fundamentals 44%, Container Orchestration 28%, Cloud Native App Delivery 16%, Cloud Native Architecture 12% ([kcna/README](https://github.com/cncf/curriculum/blob/master/kcna/README.md) [raw]) | 60 multiple-choice questions, 90 min, 75% to pass, online proctored via PSI, US$250, cert valid 2 years. **Third-party only** ([open-exam-prep](https://open-exam-prep.com/blog/kubernetes-cloud-native-associate-kcna-exam-guide-2026) [search]; [sailor.sh](https://www.sailor.sh/blog/kcna-exam-format) [search]). Sources disagree on the retake wording. |
| **KCSA** (Security Associate) | LF / CNCF | README: Cloud Native Fundamentals 16%, K8s Security Fundamentals 20%, Container Security Fundamentals 20%, Secure Software Supply Chain 16%, Monitoring/Logging/Runtime Security 12%, General Security Knowledge 16% ([kcsa/README](https://github.com/cncf/curriculum/blob/master/kcsa/README.md) [raw]). **Conflict:** the PDF in the same repo shows an older split (Overview 14, Cluster Component Security 22, Security Fundamentals 22, Threat Model 16, Platform Security 16, Compliance 10) ([KCSA PDF](https://github.com/cncf/curriculum/blob/master/KCSA%20Curriculum.pdf) [raw]). | Price/format not verified (LF site blocked). |
| **CKAD** | LF / CNCF | App Design & Build 20, App Deployment 20, Observability & Maintenance 15, Environment/Config/Security 25, Services & Networking 20 ([ckad/README](https://github.com/cncf/curriculum/blob/master/ckad/README.md) [raw]); curriculum v1.37 | Performance-based (hands-on command line), 2 h, US$445 list since a 10% rise on 4 Feb 2025, with frequent promos (one June 2026 promo showed $267). **Third-party** ([SFEIR](https://institute.sfeir.com/en/kubernetes-training/cost-certification-cka/) [search]; [hakia](https://hakia.com/skills/kubernetes-certifications/) [search]). One blog's $395 looks wrong. |
| **CKA** | LF / CNCF | Cluster Arch/Install/Config 25, Workloads & Scheduling 15, Services & Networking 20, Storage 10, **Troubleshooting 30** ([cka/README](https://github.com/cncf/curriculum/blob/master/cka/README.md) [raw]); curriculum v1.37 | Same as CKAD (third-party): 2 h, $445 list. |
| **CKS** | LF / CNCF | README: Cluster Setup 10, Cluster Hardening 15, System Hardening 15, Minimize Microservice Vulns 20, **Supply Chain Security 20** (SBOM, permitted registries, sign and validate artifacts, static analysis), Monitoring/Logging/Runtime 20 ([cks/README](https://github.com/cncf/curriculum/blob/master/cks/README.md) [raw]). The PDF v1.34 swaps Cluster Setup and System Hardening (15/10) ([CKS PDF](https://github.com/cncf/curriculum/blob/master/CKS_Curriculum%20v1.34.pdf) [raw]). | Requires a valid CKA; $445 list (third-party: [SFEIR CKS](https://institute.sfeir.com/en/kubernetes-training/cost-certification-cks/) [search]). |
| **CNPA** (Cloud Native Platform Engineering Associate) | LF / CNCF | Platform Eng Core Fundamentals 36, Observability/Security/Conformance 20, CD & Platform Eng 16, Platform APIs & Provisioning 12, IDPs & DevEx 8, Measuring Your Platform 8 ([cnpa/README](https://github.com/cncf/curriculum/blob/master/cnpa/README.md) [raw]) | Not verified. |
| **PCA** (Prometheus Certified Associate) | LF / CNCF | PromQL 28, Prometheus Fundamentals 20, Observability Concepts 18, Alerting & Dashboarding 18, Instrumentation & Exporters 16 ([PCA PDF](https://github.com/cncf/curriculum/blob/master/PCA_Curriculum.pdf) [raw]) | Not verified. |
| **Terraform Associate (004)** | HashiCorp (IBM) | — | Multiple choice (incl. true/false, multi-answer), online proctored, English, **1 hour**, **US$70.50 + taxes/fees**, valid 2 years, no prerequisites. From HashiCorp's certification page via search ([developer.hashicorp.com/certifications/infrastructure-automation](https://developer.hashicorp.com/certifications/infrastructure-automation) [search]). Question count and passing score are not published by HashiCorp; third-party "57 questions / ~70%" is unverified ([open-exam-prep](https://open-exam-prep.com/study-guides/terraform-associate/introduction/exam-facts) [search]). |
| **AWS Certified Cloud Practitioner (CLF-C02)** | AWS | — | US$100 (Foundational tier). **Third-party** ([examcert.app](https://www.examcert.app/blog/aws-clf-c02-exam-cost-2026/) [search]). |
| **AWS Solutions Architect – Associate (SAA-C03)** | AWS | — | US$150 (Associate tier), paid per attempt including retakes. **Third-party** ([examcert.app](https://www.examcert.app/blog/aws-saa-c03-exam-cost-2026/) [search]). One outlier page says $300. |
| **GitHub Actions** certification | GitHub | Exam covers "Streamlining workflows, Automating tasks, Optimizing software pipelines". Other GitHub certs: Foundations, Advanced Security, Administration, Copilot ([GitHub docs source: about certifications](https://github.com/github/docs/blob/main/content/get-started/showcase-your-expertise-with-github-certifications/about-github-certifications.md) [raw]) | Register via [learn.github.com/credentials](https://learn.github.com/credentials) (linked from that doc). Format/price/duration **not found**. |
| **Dynatrace Associate** | Dynatrace | — | Old (2017 blueprint): 70 questions, 75 min, 72% pass ([blueprint PDF](https://www.kasolution.com.br/cp/ExamBluePrint.pdf) [search], likely outdated). Newer "Associate Managed" exam, per community users: a closed-book multiple-choice part, then about 5–6 hands-on tasks in a Dynatrace environment with docs allowed ([Dynatrace Community thread](https://community.dynatrace.com/t5/Start-with-Dynatrace/Associate-Managed-Exam-Structure/m-p/300258) [search]). No official current format or price found. |

**Misconceptions (lesson 4)**
- "Certs before projects." Inference from the curricula: CKA is 30% troubleshooting and CKS is 20% supply chain, so the capstone *is* exam practice ([cka](https://github.com/cncf/curriculum/blob/master/cka/README.md), [cks](https://github.com/cncf/curriculum/blob/master/cks/README.md) READMEs [raw]).
- "KCNA is hands-on like CKA." Third-party sources say KCNA is multiple choice, while CKA/CKAD/CKS are performance-based ([sailor.sh](https://www.sailor.sh/blog/kcna-exam-format) [search]; [SFEIR](https://institute.sfeir.com/en/kubernetes-training/cost-certification-cka/) [search]).
- "You can go straight to CKS." It requires a valid CKA ([SFEIR CKS](https://institute.sfeir.com/en/kubernetes-training/cost-certification-cks/) [search]).
- "Prep sites that sell dumps are fine." Many KCNA search results were dump vendors with conflicting claims. Use the official curriculum ([cncf/curriculum](https://github.com/cncf/curriculum) [raw]).

**Hands-on and career exercise ideas**
- Capstone "release gate" demo: a PR that adds a `:latest` image and a wildcard Role. Show CI (scan), admission (Kyverno) and review catching each one (lessons 1–2 sources above).
- Map the capstone checklist against the CKS "Supply Chain Security" and KCSA "Secure Software Supply Chain" domains to show coverage ([cks](https://github.com/cncf/curriculum/blob/master/cks/README.md), [kcsa](https://github.com/cncf/curriculum/blob/master/kcsa/README.md) READMEs [raw]).
- Write a one-page portfolio README: what the pipeline proves (SBOM, signature, provenance at SLSA Build L2, or L3 with a reusable workflow) ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).

**"What to learn next" path (sequence is an inference built on the curricula above)**
1. KCNA (broad, multiple choice) → 2. CKAD (developer-friendly, hands-on) → 3. CKA (operations, 30% troubleshooting) → 4. KCSA or straight to CKS (needs CKA). In parallel: Terraform Associate 004 (cheap, 1 hour), one cloud (AWS CLF-C02 → SAA-C03), and the GitHub Actions cert for CI. Specialize by interest: PCA/OTCA (observability), CNPA → CNPE plus CBA (platform engineering), KCA (policy). Sources: the curriculum and price rows above.

**Curated resources (lesson 4)**
- [cncf/curriculum](https://github.com/cncf/curriculum) (official domains for all CNCF exams) [raw].
- [HashiCorp infrastructure automation certifications](https://developer.hashicorp.com/certifications/infrastructure-automation) [search].
- [About GitHub Certifications](https://github.com/github/docs/blob/main/content/get-started/showcase-your-expertise-with-github-certifications/about-github-certifications.md) (docs source) [raw]; [learn.github.com/credentials](https://learn.github.com/credentials) (linked from it).
- LF exam pages (named in the curriculum READMEs, not opened here, site blocked): [CKA](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/), [CKAD](https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/), [CKS](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist-cks/), [KCSA](https://training.linuxfoundation.org/certification/kubernetes-and-cloud-native-security-associate-kcsa/), [CNPA](https://training.linuxfoundation.org/certification/certified-cloud-native-platform-engineering-associate-cnpa/); KCNA prep course [LFS250](https://training.linuxfoundation.org/training/kubernetes-and-cloud-native-essentials-lfs250/) (from kcna/README [raw]).
- Video prep: KodeKloud KCNA learning path ([kodekloud.com/learning-path/kcna](https://kodekloud.com/learning-path/kcna) [search]). No YouTube URL surfaced in search.

### Inferences
- Since the LF site couldn't be reached, the lesson should give prices as "about US$250 (KCNA) and US$445 (CKA/CKAD/CKS) list, with frequent discounts. Check the official page", and avoid exact retake rules.
- The cncf/curriculum README files appear to be newer than some PDFs (KCSA and CKS weights differ). The lesson should link the repo and say "check the current curriculum" rather than freeze a table.

### Gaps
- Official LF pages (prices, durations, retake policy, validity) were not opened (DNS-blocked). KCNA/CKA/CKAD/CKS figures are third-party.
- No official AWS pricing page was opened. AWS figures are third-party.
- No source found for the GitHub Actions exam format, duration, question count or price (GH-200 code, Pearson VUE delivery and price are unverified).
- No official current Dynatrace Associate format or price was found. Also unclear whether the brief means "Dynatrace Associate" (classic) or the newer "Associate Managed"/platform-focused exam.
- KCSA, PCA and CNPA exam formats and prices were not verified.

---

## Cross-cutting key question: what intuitions help?

### Takeaway
Physical metaphors work when each one maps to a specific check the learner can run. Pair every analogy with its command.

### Cited Findings
- **SBOM = ingredient list** → `syft img -o spdx-json` ([syft README](https://github.com/anchore/syft/blob/main/README.md) [raw]). **Scanning = checking that list against the recall notices** → `grype sbom:./sbom.json` ([grype README](https://github.com/anchore/grype/blob/main/README.md) [raw]).
- **Signing = tamper-evident seal; Rekor = the public notary's ledger** (keyless signatures and certs are recorded in the Rekor transparency log, entries "cannot be removed later") ([cosign README](https://github.com/sigstore/cosign/blob/main/README.md) [raw]).
- **Provenance = signed delivery note naming the factory and production line**. SLSA L1 → L3 moves from "a note exists" to "signed by a hosted factory" to "made on a hardened line" ([SLSA build-track basics](https://github.com/slsa-framework/slsa/blob/main/spec/build-track-basics.md) [raw]).
- **Version tag = a street sign anyone with access can move; commit SHA = GPS coordinates** (tags were repointed in tj-actions and Trivy) ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-30066) [search]; [Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]).
- **base64 = writing in a different alphabet, not a lock** ("obscured but not secret") ([K8s Secret docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]).
- **Sealed Secret = a one-way mailbox slot** (anyone can drop in; only the controller can open) ([Sealed Secrets README](https://github.com/bitnami-labs/sealed-secrets/blob/main/README.md) [raw]).
- **RBAC = hotel key cards; wildcard = a master key that also opens floors not yet built** ([RBAC good practices source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
- **Admission control = bouncer at the door with the house rules; RBAC = whether you're on the guest list** ([Kyverno README](https://github.com/kyverno/kyverno/blob/main/README.md) [raw]).
- **Golden path = paved road** (the CNCF model's own words: "Paved roads" or "golden paths") ([maturity model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]). **Backstage = shop front / mall directory** ([Backstage README](https://github.com/backstage/backstage/blob/master/README.md) [raw]).
- **AI = amplifier** (DORA's own framing) ([Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) [search]). **MCP read-only mode = visitor badge**: it limits doors, but the badge holder's underlying credentials still matter ([github-mcp-server README](https://github.com/github/github-mcp-server/blob/main/README.md) [raw]; [Tailscale](https://tailscale.com/learn/kubernetes-mcp) [search]).

### Inferences
- The "seal" and "notary" pair helps learners see why keyless signing needs no private key file. Identity plus a public ledger replaces the long-lived key.

### Gaps
- None material. These are teaching framings anchored to sourced behaviour.

---

## Cross-cutting key question: what do beginners get wrong?

### Takeaway
Most beginner errors are one-time actions mistaken for ongoing controls (scan once, sign without verifying, delete the leaked secret), weak protection mistaken for strong (base64, tags, `*`), or tools mistaken for outcomes (Backstage = platform, AI = productivity).

### Cited Findings
- Scanning once and forgetting: new CVEs appear after release. Re-scan stored SBOMs ([grype README](https://github.com/anchore/grype/blob/main/README.md) [raw]; [Datadog on xz](https://securitylabs.datadoghq.com/articles/xz-backdoor-cve-2024-3094/) [search]).
- Signing without verifying: "attestations must be verified for the benefit to be realized" ([GitHub docs source](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) [raw]).
- Trusting mutable tags and trusting security tools blindly: tj-actions (2025) and Trivy (2026) ([CISA](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066) [search]; [Wiz](https://wiz.io/blog/trivy-compromised-teampcp-supply-chain-attack) [search]).
- Storing secrets in Git and "fixing" them by deleting: history keeps them, so rotate ([gitleaks README](https://github.com/gitleaks/gitleaks/blob/master/README.md) [raw]; [SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-30066) [search]).
- base64 as encryption, and assuming etcd is encrypted: it isn't by default ([K8s Secret docs source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md) [raw]).
- Wildcard RBAC and daily `cluster-admin` use ([RBAC good practices source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/security/rbac-good-practices.md) [raw]).
- Following outdated policy tutorials (`ClusterPolicy`) ([Kyverno 1.19 post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]).
- Platforms built without users: "Extrinsic push" adoption and feedback that users believe "isn't considered" are low-maturity signs ([maturity model source](https://github.com/cncf/tag-app-delivery/blob/main/platforms-maturity-model/v1/index.md) [raw]).
- Expecting AI to fix a broken process: DORA's "amplifier" finding ([dora.dev/research/ai](https://www.dora.dev/research/ai) [search]). Letting agents act unreviewed: GitHub says you remain responsible for review ([GitHub agents doc source](https://github.com/github/docs/blob/main/content/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents.md) [raw]).

### Inferences
- A "misconception check" quiz per lesson can reuse these one-liners directly. Each has a command or doc line that disproves it.

### Gaps
- No survey data on how common each misconception is among beginners was found.

---

## Cross-cutting key question: what is current in 2026 (versions, licensing, project status)?

### Takeaway
Everything below was checked on 2026-10-30. Big changes since 2024–25 material: cosign v3, `actions/attest@v4`, SLSA v1.2 with a Source Track, Vault 2.x (still BSL, IBM), OpenBao under the OpenSSF, ESO past v1.0 (now v2.x), Kyverno graduated with ClusterPolicy deprecated, Kubernetes v1.37, a CKA/CKAD curriculum on v1.37, Terraform Associate 004, and the March 2026 Trivy compromise.

### Cited Findings

| Project | Latest release tag (date) [git] | Status / notes |
|---|---|---|
| syft | v1.55.0 (2026-10-19) | SPDX + CycloneDX output ([README](https://github.com/anchore/syft/blob/main/README.md) [raw]) |
| grype | v0.121.0 (2026-10-19) | scans images, dirs, SBOMs ([README](https://github.com/anchore/grype/blob/main/README.md) [raw]) |
| trivy | v0.76.1 (2026-10-21) | v0.69.4 was the malicious March 2026 release; its tag no longer resolves ([Endor Labs](https://www.endorlabs.com/vulnerability/cve-2026-33634) [search]) |
| cosign | v3.1.4 (2026-10-20) | v3.0 made the new bundle format and OCI 1.1 referrers the default ([CHANGELOG](https://github.com/sigstore/cosign/blob/main/CHANGELOG.md) [raw]) |
| actions/attest | v4.2.2 | used in GitHub docs as `actions/attest@v4` ([docs source](https://github.com/github/docs/blob/main/content/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations.md) [raw]) |
| actions/attest-build-provenance | v4.2.2 | wraps `@actions/attest` ([README](https://github.com/actions/attest-build-provenance/blob/main/README.md) [raw]) |
| slsa-github-generator | v2.1.0 | — |
| SLSA spec | v1.2 (2025-11-24) | adds Source Track; Build Env and Dependency tracks are drafts on main ([whats-new](https://github.com/slsa-framework/slsa/blob/releases/v1.2/spec/whats-new.md) [raw]) |
| HashiCorp Vault | v2.2.1 (CHANGELOG: 22 Oct 2026); 2.0.0 on 14 Apr 2026 | BSL 1.1, licensor IBM, covers ≥1.15.0 ([LICENSE](https://github.com/hashicorp/vault/blob/main/LICENSE), [CHANGELOG](https://github.com/hashicorp/vault/blob/main/CHANGELOG.md) [raw]) |
| OpenBao | v2.7.2 (2026-10-26) | MPL-2.0, OpenSSF-hosted ([LICENSE](https://github.com/openbao/openbao/blob/main/LICENSE), [README](https://github.com/openbao/openbao/blob/main/README.md) [raw]) |
| External Secrets Operator | v2.14.0 (2026-10-23); v1.0.0 was 2025-11-07 | API `external-secrets.io/v1` ([fake provider docs](https://github.com/external-secrets/external-secrets/blob/main/docs/provider/fake.md) [raw]) |
| Sealed Secrets | v0.41.2 (2026-10-26) | — |
| SOPS | v3.13.3 (2026-07-23) | age/PGP/cloud KMS ([README](https://github.com/getsops/sops/blob/main/README.rst) [raw]) |
| Kyverno | v1.19.2 (2026-10-21) | CNCF Graduated (Mar 2026); ClusterPolicy deprecated, removal planned v1.20 ([CNCF](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/) [search]; [1.19 post source](https://github.com/kyverno/website/blob/main/src/content/blog/announcing-kyverno-release-1.19/index.md) [raw]) |
| OPA Gatekeeper | v3.23.1 (2026-08-27) | Rego ConstraintTemplates ([README](https://github.com/open-policy-agent/gatekeeper/blob/master/README.md) [raw]) |
| OPA | v1.22.0 | — |
| gitleaks | v8.30.1 (2026-03-12) | `git`/`dir`/`stdin` subcommands ([README](https://github.com/gitleaks/gitleaks/blob/master/README.md) [raw]) |
| Backstage | v1.56.2 (2026-10-22) | CNCF Incubation ([README](https://github.com/backstage/backstage/blob/master/README.md) [raw]) |
| Kubernetes | v1.37.2 (2026-10-27) | CKA/CKAD curricula at v1.37 ([cncf/curriculum](https://github.com/cncf/curriculum) [raw]) |
| github-mcp-server | v2.0.3 | `--read-only`, `--toolsets`, lockdown ([README](https://github.com/github/github-mcp-server/blob/main/README.md) [raw]) |
| terraform-mcp-server | v1.4.1 | `ENABLE_TF_OPERATIONS=false` default ([README](https://github.com/hashicorp/terraform-mcp-server/blob/main/README.md) [raw]) |
| kubernetes-mcp-server | v0.1.1 | `read_only`, toolsets ([README](https://github.com/containers/kubernetes-mcp-server/blob/main/README.md) [raw]) |

- Notable 2026 dates: Kyverno 1.17 (2 Feb), CNCF Kyverno graduation (announced 24 Mar), Trivy compromise (19–22 Mar), FinOps Framework 2026 refresh (Mar), Vault 2.0.0 (14 Apr), Kyverno 1.19 (20 Aug), CNCF maturity-model blog (1 Sep), Vault 2.2.0 (15 Oct) (sources as cited in the sections above).

### Inferences
- Pin versions in the lesson text only where behaviour matters (cosign ≥3, Kyverno ≥1.17 for `policies.kyverno.io/v1`, `actions/attest@v4`). Otherwise say "latest via Homebrew". These tools ship monthly or faster (syft, grype and trivy all released in the week of 19–21 Oct 2026 [git]).

### Gaps
- Release dates for OPA v1.22.0, actions/attest v4.2.2, slsa-github-generator v2.1.0 and the three MCP servers were not fetched.
- Whether Homebrew formulae for every tool are current on Apple Silicon was not checked (each README lists Homebrew as an install method: syft, grype, trivy, gitleaks, kubeseal).
