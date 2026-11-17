"""te: plain-voice rewrite of the part fields of p8 and p9 (intro, recap, flashcards, resource why, quiz q and why)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]


def apply(part, intro, recap, cards, res_why, quiz):
    path = ROOT / "content" / f"p{part}.json"
    P = json.loads(path.read_text())
    P["intro"], P["recap"] = intro, recap
    assert len(cards) == len(P["flashcards"]) and len(res_why) == len(P["resources"]) and len(quiz) == len(P["quiz"])
    for c, (f, b) in zip(P["flashcards"], cards):
        c["front"], c["back"] = f, b
    for r, w in zip(P["resources"], res_why):
        r["why"] = w
    for q, (qq, why) in zip(P["quiz"], quiz):
        q["q"], q["why"] = qq, why
    path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
    print("wrote", path)


apply(
    8,
    "Up to now you made containers by typing commands, and nothing remembered what you typed. In this part you describe your setup in files, the way an architect draws a plan, and Terraform makes the real world match the drawing. The first four lessons run on Docker on your laptop and cost nothing. They go slowly through the language, the state and modules, with real plans to read. Day 35 takes the same skills to AWS and GitHub Actions, and you can skip it.",
    [
        "Infrastructure as Code keeps your setup in files that people review and git remembers. Terraform is declarative, so a second apply changes nothing.",
        "The loop is init, plan, apply, destroy. Read every plan, and look for `forces replacement` before you type yes.",
        "HCL has types, variables with validation, locals, outputs, for expressions and functions. Try any expression in `terraform console`.",
        "`for_each` names copies by key, and `count` numbers them by position, so removing an item shifts and replaces the later copies.",
        "The state links addresses to real objects and holds secrets in plain text, so it lives in a locked remote backend and never in git.",
        "`moved`, `import` and `removed` blocks change the state through plans you review. Refresh-only mode shows drift and copies it into the state.",
        "A module packages a shape you use many times. Each long-lived environment gets its own root folder, and `terraform test` checks the modules.",
        "In CI: cheap checks first, a plan on pull requests, apply on main after approval, OIDC instead of stored keys, and scanners pinned by digest or SHA.",
    ],
    [
        ("What does `-/+` mean in a Terraform plan?", "Replace: destroy the object, then create a new one."),
        ("What does `terraform init` do?", "It downloads providers and modules, sets up the backend, and writes the lock file."),
        ("Which do you commit: `.terraform.lock.hcl`, `.terraform/` or `terraform.tfstate`?", "Only the lock file. Never the `.terraform/` folder or the state."),
        ("Why does OpenTofu exist?", "HashiCorp moved Terraform to the BSL license in 2023, so part of the community copied the last open source version and carried it on."),
        ("Where can a variable get its value, from weakest to strongest?", "Default, `TF_VAR_` environment variable, `terraform.tfvars`, `*.auto.tfvars`, then `-var` and `-var-file`."),
        ("How do you try out an expression quickly?", "`terraform console`, or `echo 'EXPR' | terraform console` for one expression."),
        ("What does `for_each` accept?", "A map, or a set of strings. Wrap a list in `toset()`."),
        ("Why prefer `for_each` over `count` for things with names?", "Copies are known by name, so removing one destroys only that copy. `count` copies shift and get replaced."),
        ("Does `sensitive = true` keep a value out of the state?", "No. It only hides the value in the output. The state still holds it in plain text."),
        ("How do you rename a resource without rebuilding it?", "Add a `moved` block with `from` (the old address) and `to` (the new address)."),
        ("Does `terraform state rm` delete the real object?", "No. Terraform forgets it, and the object keeps running."),
        ("What two arguments does an `import` block need?", "`to`, the resource address, and `id`, the provider's ID for the object."),
        ("What does `terraform apply -refresh-only` change?", "Only the state. No real object changes, and the code still wins on the next normal apply."),
        ("What does `use_lockfile = true` do in the S3 backend?", "It writes a `.tflock` file next to the state, so only one run can change the state at a time."),
        ("What is the address of resource `docker_container.app` inside `module \"dev\"`?", "`module.dev.docker_container.app`."),
        ("Why are CLI workspaces a poor way to separate dev and prod?", "They share one backend, so the environments cannot have separate credentials and access rules."),
        ("How does a `terraform test` run avoid creating real resources?", "With `command = plan`, or with a `mock_provider` block."),
        ("What must a GitHub Actions job have to ask GitHub for an OIDC token?", "The `id-token: write` permission."),
    ],
    [
        "The official reference. Every block, expression and function in this part has a page here.",
        "HashiCorp's own short hands-on track, with the same Docker provider you used here.",
        "HashiCorp's rules for layout, naming, version pinning and what never to commit.",
        "A short whiteboard talk by HashiCorp's co-founder on what Terraform is for.",
        "A quick tour of how Terraform is built and of the basic commands. Watch it if Day 31 needs a second explanation.",
        "About two and a half hours on AWS: variables, modules, environments, testing and CI. It is from 2022, so it still locks the state with DynamoDB, which is now deprecated.",
        "A longer AWS project for more cloud practice after Day 35. Destroy what you build as you go.",
        "A HashiCorp engineer walks through ways to test Terraform and the built-in test tool from Day 34.",
        "The standard Terraform book (paid). Chapter 5 goes deep on loops and conditions, and the ways they go wrong.",
        "A free book on laying out code, modules and environments, from the maintainer of the terraform-aws-modules project.",
        "Read this before you move a real state between the two tools. Its first step is a backup of the state.",
    ],
    [
        ("A plan line ends with `# forces replacement`. What will apply do to that resource?",
         "Terraform cannot change that setting on the existing object, so it destroys the object and creates a new one."),
        ("Which statement about Terraform state is true?",
         "The state stores every setting, passwords and tokens included, so protect it and keep it in a proper backend."),
        ("Two pipeline runs try to apply against the same state in S3 at the same moment. What stops them from damaging it?",
         "With `use_lockfile = true`, the first run holds a lock file and the second is refused. `.terraform.lock.hcl` has nothing to do with it: that file fixes provider versions."),
        ("What does `[for s in [\"a\", \"b\", \"c\"] : upper(s) if s != \"b\"]` give?",
         "The `if` drops \"b\", `upper` turns the rest into capitals, and square brackets build a list."),
        ("You move three resources into `module.dev`, and the plan says 3 to add and 3 to destroy. What is missing?",
         "Without `moved` blocks, Terraform sees the old addresses vanish and new ones appear. With them, the plan shows three moves and 0 to destroy."),
        ("Which `terraform test` setup checks a module without creating any real resources?",
         "Plan-mode runs create nothing, and a mock provider makes even apply-mode runs pretend."),
        ("In the lab, the CI role may not change IAM. So how do changes to the role itself get applied?",
         "You apply IAM changes from your laptop, with your own login. Keeping them out of CI means a pull request cannot give the pipeline more power."),
        ("You applied with `-var host_port=9000` yesterday. Today you run `terraform plan` with no flags and no tfvars file. What do you see?",
         "Terraform does not remember `-var` values, so today's plan uses the default and proposes to change the port back."),
        ("In `infra/local`, the app reaches Redis at the host name `hello-redis`. Which Docker feature makes that work?",
         "Containers on the same user-defined network find each other by container name, through Docker's built-in DNS (the name-to-address lookup)."),
        ("A job uses `environment: production`, and that environment has a required reviewer. What happens when the job is triggered?",
         "Required reviewers are a protection rule: the job waits before it starts until someone approves."),
    ],
)

apply(
    9,
    "Terraform gave you servers. The next question is what runs on them, and who keeps it that way. Ansible works like a careful house sitter with a checklist: it logs in over SSH, makes each server match what your files describe, and leaves alone whatever already matches. Both lessons run against three small practice servers in Docker on your Mac, so nothing costs money. Day 37 ends by letting Ansible find EC2 servers by tag, which you can also try against a local AWS emulator.",
    [
        "Configuration management keeps servers matching what your files say. Terraform makes servers, and Ansible sets them up.",
        "Ansible is agentless: it logs in over SSH, runs a Python module, reads the JSON result and cleans up.",
        "An inventory lists hosts in groups, and the ansible.cfg in your project folder holds the defaults.",
        "Modules describe a result and report ok or changed, so a second run should show changed=0.",
        "--check --diff previews a run against the real servers, since Ansible keeps no state file.",
        "Precedence runs from role defaults up through group_vars, host_vars, play vars and role vars to -e, which always wins.",
        "Roles package tasks, handlers, templates and defaults. Collections package modules and come from requirements.yml.",
        "Vault keeps secrets encrypted in git, and the vault password never goes into the repo.",
        "ansible-lint and --syntax-check run in CI, and Molecule tests roles from start to finish on throwaway servers.",
        "The aws_ec2 dynamic inventory finds cloud servers by tag instead of a hand-written list.",
    ],
    [
        ("What does Ansible do that Terraform does not?", "It sets up what runs inside existing servers (packages, files, services) over SSH, and can repeat that any time."),
        ("What does a Linux server need before Ansible can manage it?", "An SSH login, usually with sudo, and Python 3. No Ansible agent."),
        ("ansible-core or ansible: which package is smaller?", "ansible-core: the engine plus ansible.builtin. The ansible package adds many community collections."),
        ("In which order does Ansible look for its config file?", "ANSIBLE_CONFIG, then ./ansible.cfg, ~/.ansible.cfg and /etc/ansible/ansible.cfg. The first one found is used."),
        ("Why does `ansible web1 -a 'cat f | grep x'` fail?", "The default command module runs no shell, so cat receives the pipe as a file name. Use the shell module."),
        ("What do ok and changed count in PLAY RECAP?", "ok counts tasks that succeeded. changed counts the ones that also changed something on the server."),
        ("When does a handler run?", "Once, at the end of the play, and only if a task that notified it reported changed."),
        ("What do --check and --diff do?", "--check predicts changes without making them. --diff shows the lines a task changes in a file."),
        ("Order these from weakest to strongest: host_vars, role defaults, -e, group_vars.", "Role defaults, group_vars, host_vars, -e."),
        ("Role defaults/ or vars/ for a setting users may change?", "defaults/. Role vars beat inventory variables, so nobody could override them from group_vars or host_vars."),
        ("What is an FQCN?", "A module's full name, namespace.collection.module, such as ansible.builtin.copy."),
        ("How do you install the collections a project needs?", "ansible-galaxy collection install -r requirements.yml"),
        ("encrypt or encrypt_string for a secret in group_vars?", "encrypt_string. One encrypted value is decrypted only when used, while a whole encrypted file needs the password for every command."),
        ("Where should the vault password live?", "Outside git: in a password manager, a CI secret, or a mode-600 file listed in .gitignore."),
        ("What does the aws_ec2 inventory plugin do?", "It asks AWS which EC2 instances exist, filtered by tags and state, and turns them into hosts and groups."),
        ("What does Molecule test?", "A role or playbook from start to finish: it creates test servers, applies it twice to check that the second run changes nothing, checks the result and deletes everything."),
    ],
    [
        "The official tour of control nodes, inventories and playbooks, with a quick start you can follow on the lab servers.",
        "How the docs suggest laying out a real project: inventories per environment, group_vars, host_vars and roles.",
        "The full list of 22 precedence levels, for when the short ladder from Day 37 is not enough.",
        "Vault IDs, password scripts and the limits of what Vault protects, beyond the two commands the lab uses.",
        "Every rule with an example of good and bad code, and the profiles from min up to production.",
        "Guides for testing a role, a playbook or a collection, when you want the Day 37 checks to run by themselves.",
        "Every option of the dynamic inventory: filters, hostnames, keyed_groups, compose and caching.",
        "A live-streamed course from 2020 that goes from ad-hoc commands to roles, Vault and Molecule. Some module names have changed since.",
        "A calm beginner course in short episodes, useful if you want a second explanation of each step.",
        "The book the Ansible 101 videos follow, kept up to date by its author, with full real-world examples.",
        "How to run your roles inside a Packer build, so new servers start with everything already installed.",
    ],
    [
        ("Someone edits nginx.conf by hand on one of twenty servers that a template task manages. What happens on the next playbook run?",
         "Each host is checked on its own, and only the server whose file differs from the filled-in template gets changed."),
        ("Why does Ansible need no agent on the servers it manages?",
         "The module runs, prints JSON and is deleted, so nothing of Ansible stays running on the server."),
        ("`ansible web -a 'ls /var/log/*.log'` prints `No such file or directory`, although .log files exist. Why?",
         "A shell is what expands patterns like *. Use the shell module, or the find module, for this."),
        ("A role default sets `app_port: 8000`, the play's vars set `8080`, and you run with `-e app_port=9090`. Which port is used?",
         "Extra vars sit at the top of the precedence list."),
        ("Which command encrypts one value, so you can paste it into an otherwise readable vars file?",
         "encrypt_string prints a `!vault |` block for one variable, and the rest of the file stays plain text."),
        ("An instance has the tag `Project=hello-devops` but is stopped. Does the lab's aws_ec2 inventory list it?",
         "Both filters must match, and the second one keeps only running instances."),
        ("A role should let users change its listen port. Where does `nginx_port: 80` belong?",
         "Defaults have the lowest precedence, so group_vars, host_vars or -e can override them."),
        ("Terraform and Ansible both describe servers in files. Which one keeps a record of what it created, so that it can delete those things later?",
         "Terraform's state links code to real resources (Day 33). Ansible keeps no state, so deleting a task never removes what it installed."),
        ("A playbook uses `ansible.builtin.systemd_service` with `state: started` but no `enabled: true`. What happens after the server reboots?",
         "started is about now and enabled is about boot, the same split as systemctl start and systemctl enable on Day 6."),
    ],
)
