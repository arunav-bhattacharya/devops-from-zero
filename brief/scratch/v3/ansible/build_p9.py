#!/usr/bin/env python3
"""Build content/p9.json (Part 9, Ansible: Days 36 and 37).

Re-run any time: python3 brief/scratch/v3/ansible/build_p9.py
Code blocks are read from labs/ansible, so the lesson always shows the tested files.
Console output in the worked examples was captured from real runs against the
practice containers (ansible-core 2.22.0, ansible-lint 26.11.0) on 2026-11-07.
"""
import json
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAB = ROOT / "labs" / "ansible"
OUT = ROOT / "content" / "p9.json"


def t(s):
    """Dedent a triple-quoted block and strip the outer blank lines."""
    return textwrap.dedent(s).strip("\n")


def lab(path):
    return (LAB / path).read_text().rstrip("\n")


def code(lang, path, run, title=None):
    return {"lang": lang, "title": title or path, "src": lab(path), "run": run}


# ---------------------------------------------------------------- links
D = "https://docs.ansible.com/projects/ansible/latest/"
L = {
    "start": ("Getting started with Ansible", D + "getting_started/index.html"),
    "install": ("Installing Ansible", D + "installation_guide/intro_installation.html"),
    "inventory": ("How to build your inventory", D + "inventory_guide/intro_inventory.html"),
    "config": ("Ansible configuration settings", D + "reference_appendices/config.html"),
    "adhoc": ("Introduction to ad hoc commands", "https://docs.ansible.com/projects/ansible-core/devel/command_guide/intro_adhoc.html"),
    "check": ("Validating tasks: check mode and diff mode", D + "playbook_guide/playbooks_checkmode.html"),
    "playbooks": ("Ansible playbooks", D + "playbook_guide/playbooks_intro.html"),
    "handlers": ("Handlers: running operations on change", D + "playbook_guide/playbooks_handlers.html"),
    "vars": ("Using variables", D + "playbook_guide/playbooks_variables.html"),
    "facts": ("Discovering variables: facts and magic variables", D + "playbook_guide/playbooks_vars_facts.html"),
    "templating": ("Templating (Jinja2)", D + "playbook_guide/playbooks_templating.html"),
    "loops": ("Loops", D + "playbook_guide/playbooks_loops.html"),
    "tags": ("Tags", D + "playbook_guide/playbooks_tags.html"),
    "roles": ("Roles", D + "playbook_guide/playbooks_reuse_roles.html"),
    "collections": ("Installing collections", D + "collections_guide/collections_installing.html"),
    "vault": ("Ansible Vault", D + "vault_guide/vault.html"),
    "vault_enc": ("Encrypting content with Ansible Vault", D + "vault_guide/vault_encrypting_content.html"),
    "sample": ("Sample Ansible setup", D + "tips_tricks/sample_setup.html"),
    "aws_ec2": ("amazon.aws.aws_ec2 inventory plugin", D + "collections/amazon/aws/aws_ec2_inventory.html"),
    "lint": ("Ansible Lint documentation", "https://docs.ansible.com/projects/lint/"),
    "molecule": ("Ansible Molecule", "https://docs.ansible.com/projects/molecule/"),
    "packer": ("Packer Ansible provisioner", "https://developer.hashicorp.com/packer/integrations/hashicorp/ansible/latest/components/provisioner/ansible"),
    "ep1": ("Ansible 101, episode 1: Introduction to Ansible (Jeff Geerling)", "https://www.youtube.com/watch?v=goclfp6a2IQ"),
    "ep2": ("Ansible 101, episode 2: Ad-hoc tasks and inventory (Jeff Geerling)", "https://www.youtube.com/watch?v=7kVfqmGtDL8"),
    "ep3": ("Ansible 101, episode 3: Introduction to playbooks (Jeff Geerling)", "https://www.youtube.com/watch?v=WNmKjtWtqIc"),
    "ep5": ("Ansible 101, episode 5: Handlers, environment vars and variables (Jeff Geerling)", "https://www.youtube.com/watch?v=HU-dkXBCPdU"),
    "ep6": ("Ansible 101, episode 6: Ansible Vault and roles (Jeff Geerling)", "https://www.youtube.com/watch?v=JFweg2dUvqM"),
    "ep7": ("Ansible 101, episode 7: Molecule testing, linting and Galaxy (Jeff Geerling)", "https://www.youtube.com/watch?v=FaXVZ60o8L8"),
    "playlist": ("Ansible 101 series (Jeff Geerling)", "https://www.youtube.com/playlist?list=PL2_OBreMn7FqZkvMYt6ATmgC0KAGGJNAN"),
    "lltv": ("Getting started with Ansible (Learn Linux TV)", "https://www.youtube.com/playlist?list=PLT98CRl2KxKEUHie1m24-wkyHpEsa4Y70"),
    "book": ("Ansible for DevOps (Jeff Geerling)", "https://ansiblefordevops.com/"),
}


def ref(key, kind):
    title, url = L[key]
    return {"title": title, "url": url, "kind": kind}


def src(key):
    title, url = L[key]
    return {"title": title, "url": url}


# ---------------------------------------------------------------- diagrams
SVG36 = (
    '<svg viewBox="0 0 560 270" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-label="Your Mac logs in to web1 over SSH, copies a module, python3 runs it, and a JSON result comes back as ok or changed; web2 and lb1 get the same steps in parallel">'
    '<text class="ts" x="96" y="20" font-size="11" text-anchor="middle">control node</text>'
    '<text class="ts" x="464" y="20" font-size="11" text-anchor="middle">managed node</text>'
    '<rect class="bxo" x="16" y="30" width="160" height="48" rx="10"/>'
    '<text class="tk" x="96" y="59" font-size="13" text-anchor="middle">Your Mac</text>'
    '<rect class="bxt" x="384" y="30" width="160" height="48" rx="10"/>'
    '<text class="tk" x="464" y="59" font-size="13" text-anchor="middle">web1</text>'
    '<line class="ln" x1="176" y1="42" x2="380" y2="42" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="36" font-size="11" text-anchor="middle">1. SSH login</text>'
    '<line class="ln" x1="176" y1="68" x2="380" y2="68" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="62" font-size="11" text-anchor="middle">2. copy module</text>'
    '<line class="ln" x1="464" y1="78" x2="464" y2="112" marker-end="url(#ar)"/>'
    '<rect class="bxt" x="384" y="116" width="160" height="44" rx="10"/>'
    '<text class="tk" x="464" y="143" font-size="13" text-anchor="middle">python3 runs it</text>'
    '<rect class="bxg" x="16" y="116" width="160" height="44" rx="10"/>'
    '<text class="tk" x="96" y="143" font-size="13" text-anchor="middle">ok or changed</text>'
    '<line class="ln" x1="384" y1="138" x2="180" y2="138" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="132" font-size="11" text-anchor="middle">3. JSON result</text>'
    '<text class="ts" x="96" y="184" font-size="11" text-anchor="middle">then the next task</text>'
    '<rect class="bx" x="384" y="196" width="74" height="40" rx="10"/>'
    '<text class="t" x="421" y="221" font-size="13" text-anchor="middle">web2</text>'
    '<rect class="bx" x="470" y="196" width="74" height="40" rx="10"/>'
    '<text class="t" x="507" y="221" font-size="13" text-anchor="middle">lb1</text>'
    '<line class="lnd" x1="176" y1="216" x2="380" y2="216" marker-end="url(#ar)"/>'
    '<text class="ts" x="280" y="210" font-size="11" text-anchor="middle">same steps</text>'
    '<text class="ts" x="464" y="256" font-size="11" text-anchor="middle">in parallel</text>'
    "</svg>"
)

LADDER = [
    ("bxo", "-e extra vars", "Hi from -e"),
    ("bxp", "role vars", "fixed by the role"),
    ("bxt", "play vars", ""),
    ("bxt", "host_vars/web2", "web2, the canary"),
    ("bxt", "group_vars/web", "Hello from Ansible"),
    ("bxt", "group_vars/all", ""),
    ("bxg", "role defaults", "Hello, DevOps!"),
]


def svg37():
    parts = [
        '<svg viewBox="0 0 560 290" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Variable precedence from weakest to strongest: role defaults, group_vars/all, group_vars/web, host_vars/web2, play vars, role vars, extra vars">',
        '<text class="ts" x="64" y="36" font-size="11" text-anchor="middle">strongest</text>',
        '<text class="ts" x="64" y="264" font-size="11" text-anchor="middle">weakest</text>',
        '<line class="ln" x1="120" y1="266" x2="120" y2="24" marker-end="url(#ar)"/>',
    ]
    y = 16
    for cls, label, note in LADDER:
        parts.append(f'<rect class="{cls}" x="150" y="{y}" width="240" height="30" rx="10"/>')
        parts.append(f'<text class="tk" x="270" y="{y + 20}" font-size="13" text-anchor="middle">{label}</text>')
        if note:
            parts.append(f'<text class="ts" x="404" y="{y + 19}" font-size="11" text-anchor="start">{note}</text>')
        y += 38
    parts.append("</svg>")
    return "".join(parts)


# ================================================================ Day 36
d36 = {
    "id": "d36",
    "title": "Ansible from zero: inventory, modules and your first playbook",
    "minutes": 50,
    "goal": "By the end you can say what Ansible does that Terraform does not, list servers in an inventory, run ad-hoc commands and a first playbook against three practice servers, and explain why a second run changes nothing.",
    "guess": {
        "q": "A playbook installs nginx and writes its config file. It succeeds. You run the same playbook again a minute later. What does Ansible do?",
        "options": [
            "Installs nginx again and rewrites the file, because tasks always run",
            "Refuses to run, because these servers were already set up",
            "Checks each server, finds it already right, and reports ok",
            "Reads a state file from the first run and skips every task",
        ],
        "answer": 2,
        "why": "Each module looks at the server first and acts only when something differs, so the second run reports ok everywhere. Ansible keeps no state file like Terraform's: it checks the real server every time.",
    },
    "terms": [
        {"term": "Configuration management", "plain": "Keeping the packages, files and services on many servers in a state you wrote down as code."},
        {"term": "Control node", "plain": "The machine you run Ansible from. In this course, your Mac."},
        {"term": "Managed node", "plain": "A server that Ansible configures. It needs SSH and Python, but no Ansible."},
        {"term": "Inventory", "plain": "A file that lists your servers, sorts them into groups and says how to reach them."},
        {"term": "Module", "plain": "A small program Ansible sends to a server to do one job, such as installing a package."},
        {"term": "Idempotent", "plain": "Safe to repeat: running it again when nothing needs to change changes nothing."},
        {"term": "Playbook", "plain": "A YAML file of plays. Each play runs a list of tasks on a group of servers."},
        {"term": "Handler", "plain": "A task that runs only when another task reports a change, usually a restart or a reload."},
    ],
    "sections": [
        {
            "h": "Terraform made the server. Something still has to set it up",
            "body": t("""
                On Day 35 Terraform created resources in AWS, and on Day 14 a user data script installed hello-devops on one EC2 server. That works for one server. It gets hard with twenty, and harder a year later, when nobody remembers which ones got last month's fix.

                **Configuration management** is the answer to that problem. You write down what each server should have: packages, files, users and services. A tool then makes every server match, and keeps doing it. Terraform is good at creating machines through a cloud API. Ansible is good at what happens inside them after they boot.

                How much of this you need depends on how you run servers:
                - Mutable infrastructure: servers live for months, and you change them in place. Ansible was built for this.
                - Immutable infrastructure: you never change a running server. You build a new image, start new servers from it and delete the old ones. Docker images (Day 18) and Kubernetes (Part 10) work this way.

                Most new apps ship as containers, so you may write little Ansible for your own service. It still has plenty of work:
                - VMs that will not move to containers, such as databases, build agents or old Java apps
                - bootstrapping fresh machines, including the nodes a Kubernetes cluster runs on
                - network devices such as switches and routers
                - fleet-wide changes, like a security patch on every server this afternoon
            """),
            "refs": [ref("start", "docs"), ref("ep1", "watch")],
        },
        {
            "h": "Agentless: everything happens over SSH",
            "body": t("""
                Ansible runs on one machine, the **control node**, which is your Mac. The servers it manages are called managed nodes. Nothing of Ansible is installed on them, and no Ansible process waits there for orders. That is what agentless means. Older tools such as Puppet and Chef install an agent on every server, and the agent pulls its config from a central server.

                A managed node needs two things: an SSH login (Day 7) and Python 3. For every task, Ansible does this on each server:
                1. It opens an SSH connection, or reuses an open one.
                2. It copies a small Python program, the module, into a temporary folder.
                3. It runs the module with the server's python3. The module checks the server and fixes what differs.
                4. It reads the JSON result the module prints, then deletes the temporary folder.

                That result has a `changed` field, and it is where the green ok and the yellow changed in Ansible's output come from. Ansible works on five servers at a time by default, and the `-f` option raises that number.

                Network switches are the exception to the Python rule. Their modules run on the control node and talk to the device over SSH or an API.
            """),
            "refs": [ref("install", "docs"), ref("ep2", "watch")],
        },
        {
            "h": "Install Ansible, and start three practice servers",
            "body": t("""
                Ansible comes as two Python packages:
                - `ansible-core` is the engine, the commands and the built-in modules, called `ansible.builtin`.
                - `ansible` is ansible-core plus a large set of community collections, such as `amazon.aws`. It is much bigger, and its current release still ships ansible-core 2.21.

                Start with ansible-core, installed as a tool with its own Python. Pick one way:
                - `uv tool install ansible-core`
                - `pipx install ansible-core`
                - `brew install ansible`, for the big package

                ansible-core 2.22, the current version, needs Python 3.13 or newer on the control node. The `python3` that comes with macOS is older, so do not run plain `pip install` with it. uv downloads a suitable Python by itself. Check the current docs for the install command, then run `ansible --version`.

                The lab's `compose.yaml` starts three Ubuntu 24.04 containers: web1 and web2 for the app, and lb1 for nginx. Each runs sshd and has python3, like a fresh cloud server. The script `./setup.sh` makes an SSH key for the lab in `.keys/`, builds the image with only the public key inside, starts the servers and waits until SSH answers.

                These servers run systemd as PID 1, so `systemctl` works as it did on Day 6. A plain container has no systemd, and systemd inside Docker needs extra rights: `privileged: true`, the host's cgroup tree and some tmpfs mounts. Those rights are fine on your laptop and wrong anywhere else. Other differences from a real server:
                - All three share the kernel of Docker's VM, so `uptime` shows that VM's uptime.
                - There is no real boot or disk setup, and the network is IPv4 only.
                - They all live on 127.0.0.1 and differ by SSH port: 2201, 2202 and 2203.
            """),
            "refs": [ref("install", "docs")],
        },
        {
            "h": "The inventory says which servers exist",
            "body": t("""
                An inventory lists your servers and sorts them into groups. The lab's `inventory.ini` has three groups:
                - `[web]` holds web1 and web2.
                - `[lb]` holds lb1.
                - `[lab:children]` is a group of groups: everything in web and lb.

                A host line can carry host variables, settings for that host only. `web1 ansible_host=127.0.0.1 ansible_port=2201` names the host web1 and tells Ansible where its SSH really answers. Every inventory also has two groups you never write: `all`, with every host, and `ungrouped`, for hosts in no group. The file `inventory.yml` is the same inventory in YAML, which nests well and is easy for a program to write. The command `ansible-inventory --graph` prints the tree, and both files give the same one.

                Ansible reads its settings from the first config file it finds, in this order:
                1. The file named in the `ANSIBLE_CONFIG` environment variable.
                2. `ansible.cfg` in the current folder.
                3. `~/.ansible.cfg` in your home folder.
                4. `/etc/ansible/ansible.cfg`.

                So run Ansible from the lab folder. Its `ansible.cfg` picks the inventory, logs in as `ubuntu` with the lab key and says where roles live. It also gives SSH a known_hosts file of the lab's own. The option `StrictHostKeyChecking=accept-new` trusts a new server the first time and refuses a changed key later, the same rule as Day 7. The setting `interpreter_python = auto_silent` hides a warning about which Python Ansible found on each server.
            """),
            "refs": [ref("inventory", "docs"), ref("config", "docs")],
        },
        {
            "h": "Ad-hoc commands: one module on many servers",
            "body": t("""
                An ad-hoc command runs one module once, straight from the terminal. Its shape is `ansible PATTERN -m MODULE -a ARGUMENTS`, and the pattern is a host or a group from the inventory, such as `all`, `web` or `web1`.

                `ansible all -m ansible.builtin.ping` logs in to every server and runs the ping module. It answers `pong` when SSH and Python work. `ansible.builtin.ping` is the module's full name: the ping module from the builtin collection inside ansible-core. Day 37 explains the naming.

                Without `-m`, Ansible uses the command module, which runs a program directly, with no shell. Pipes, `>`, `;` and `&&` do not work there. `ansible web1 -a 'cat /etc/os-release | grep PRETTY'` failed with `cat: '|': No such file or directory`, because cat got the pipe as a file name. The shell module runs the same line through `/bin/sh`, and it printed the one line we wanted.

                Add `-b` (become) to run as root through sudo: `ansible web1 -a whoami` printed `ubuntu`, and with `-b` it printed `root`. Modules you will use all the time:
                - `ansible.builtin.apt`, or the generic `package`, installs packages.
                - `ansible.builtin.copy` puts a file on the server.
                - `ansible.builtin.service` starts, stops, restarts and enables services.

                Our first `apt` call taught us something. jq installed on web1 but failed on web2 with `No package matching 'jq' is available`. Ubuntu's container image ships with no package list, and an earlier command of ours had refreshed it on web1 only. Adding `update_cache=true` runs `apt-get update` first.
            """),
            "refs": [ref("adhoc", "docs"), ref("ep2", "watch")],
        },
        {
            "h": "Idempotence: ok, changed, and a preview with --check --diff",
            "body": t("""
                A module describes the result you want. `name=jq state=present` means "jq must be installed". The apt module checks first. If jq is there, it does nothing and reports ok. If not, it installs jq and reports changed. So running a task twice is safe, and the second run tells you whether anything had drifted. This property is called idempotence, and it is the main thing Ansible gives you over a shell script.

                The command and shell modules cannot know what your command did, so they report changed every time. Treat them as a last resort. `ansible-doc -l` lists every module you have, and `ansible-doc ansible.builtin.apt` shows one module's options and examples.

                Two flags show what a run would do before it does it:
                - `--check` runs every task in a dry mode. Modules report what they would change, and change nothing.
                - `--diff` prints the lines a task changes in a file, like `git diff`.

                Together they work like Terraform's plan from Day 31, with one difference. Ansible has no state file, so the preview comes from the real servers at that moment. Check mode is still a prediction. A task that depends on an earlier task's result can guess wrong, because the earlier task did not really run.
            """),
            "refs": [ref("check", "docs")],
        },
        {
            "h": "A first playbook: plays, tasks, handlers and the recap",
            "body": t("""
                A playbook is a YAML file with a list of plays. A play names its hosts and lists its tasks, and each task calls one module with arguments: an ad-hoc command, written down. The lab's `first-playbook.yml` has two plays:
                1. "Basics on every server" installs tree and htop and writes `/etc/motd` on the whole lab group.
                2. "Web server on the load balancer" installs nginx on lb1, gives it a site config and a page, and starts it.

                Ansible runs the first task on every host of the play, then the second task, and so on from top to bottom. Setting `become: true` on a play makes every task use sudo. Each play starts with Gathering Facts, where Ansible collects details about each server. Day 37 puts them to use.

                A handler waits until something notifies it. The site config task has `notify: Reload nginx`. When that task reports changed, the handler runs once, at the end of the play. When the file was already right, nginx is left alone. Ten tasks can notify the same handler, and it still runs once.

                The run ends with PLAY RECAP, one line per host:
                - `ok` counts every task that succeeded, changed or not.
                - `changed` counts the tasks that changed something.
                - `unreachable` means SSH failed, and `failed` means a task failed.

                A failed task stops the play for that host only. Its notified handlers do not run, which is how a restart gets lost. The hands-on brings Day 6 back: `ansible.builtin.systemd_service` with `enabled: true` does what `systemctl enable` did.
            """),
            "refs": [ref("playbooks", "docs"), ref("handlers", "docs"), ref("ep3", "watch")],
        },
    ],
    "analogy": "Ansible works like a house sitter with a checklist: heating at 20 degrees, plants watered, back door locked. She checks each line and acts only where the house does not match it, so a second round through a tidy house changes nothing. A shell script is a list of chores instead, and it waters the plants again even when the soil is wet. A good house sitter would also notice a broken window that no line mentions. Ansible never does: a package someone installed by hand stays, because nothing on the list talks about it.",
    "diagram": SVG36,
    "diagram_caption": "For each task, Ansible logs in over SSH, runs a small Python module on the server and reads back ok or changed.",
    "worked": {
        "title": "Run a playbook twice, then change one thing",
        "steps": [
            {
                "say": "Start the practice servers from the lab folder, then check that Ansible can reach one. The first `setup.sh` takes a minute or two while Docker builds the image. `pong` means SSH, the key and Python all work.",
                "code": t("""
                    $ cd ~/code/ansible-lab
                    $ ./setup.sh
                    port 2201: SSH is ready
                    port 2202: SSH is ready
                    port 2203: SSH is ready
                    All three servers are up. Next: ansible all -m ping
                    $ ansible web1 -m ansible.builtin.ping
                    web1 | SUCCESS => {
                        "ansible_facts": {
                            "discovered_interpreter_python": "/usr/bin/python3.12"
                        },
                        "changed": false,
                        "ping": "pong"
                    }
                """),
                "lang": "console",
            },
            {
                "say": "Run the first playbook. Every task that installs or writes something reports changed, and the handler runs because the site config changed. Output trimmed to the second play and the recap, and the rows of stars after each banner are cut.",
                "code": t("""
                    $ ansible-playbook first-playbook.yml
                    PLAY [Web server on the load balancer] *****************************************
                    TASK [Install nginx] ***********************************************************
                    changed: [lb1]
                    TASK [Replace the default site with ours] **************************************
                    changed: [lb1]
                    TASK [Put a page in the web folder] ********************************************
                    changed: [lb1]
                    TASK [Start nginx now and at every boot] ***************************************
                    changed: [lb1]
                    RUNNING HANDLER [Reload nginx] *************************************************
                    changed: [lb1]
                    PLAY RECAP *********************************************************************
                    lb1                        : ok=9    changed=7    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web1                       : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web2                       : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                """),
                "lang": "console",
            },
            {
                "say": "Run it again without changing anything. Every task now reports ok, and the handler stays quiet because nothing notified it. lb1 shows ok=8 instead of 9 for the same reason. This run took about 10 seconds and changed nothing, which is what you want from a tool you may run every day.",
                "code": t("""
                    $ ansible-playbook first-playbook.yml
                    PLAY RECAP *********************************************************************
                    lb1                        : ok=8    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web1                       : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web2                       : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                """),
                "lang": "console",
            },
            {
                "say": "In `first-playbook.yml`, add a line `<p>Deployed by Ansible.</p>` under the h1 line of the page task. Preview it with `--check --diff`. Ansible shows the line it would add and counts the task as changed, but `curl` proves the page on lb1 is still the old one.",
                "code": t("""
                    $ ansible-playbook first-playbook.yml --check --diff
                    TASK [Put a page in the web folder] ********************************************
                    --- before: /var/www/html/index.html
                    +++ after: /var/www/html/index.html
                    @@ -1 +1,2 @@
                     <h1>Hello from lb1</h1>
                    +<p>Deployed by Ansible.</p>

                    changed: [lb1]
                    $ curl -s localhost:8180
                    <h1>Hello from lb1</h1>
                """),
                "lang": "console",
            },
            {
                "say": "Run it for real. Then change a server by hand, the way a quick fix often happens: append a line to `/etc/motd` on web2 over SSH. The next run with `--diff --limit web2` puts the file back and shows exactly what it removed. A difference between the code and the server is called drift, and a regular Ansible run finds it and undoes it.",
                "code": t("""
                    $ ansible-playbook first-playbook.yml
                    $ ssh -i .keys/id_ed25519 -p 2202 -o UserKnownHostsFile=.keys/known_hosts ubuntu@127.0.0.1 "echo 'edited by hand' | sudo tee -a /etc/motd >/dev/null"
                    $ ansible-playbook first-playbook.yml --diff --limit web2
                    TASK [Write a login message] ***************************************************
                    --- before: /etc/motd
                    +++ after: /etc/motd
                    @@ -1,2 +1 @@
                     web2 is managed by Ansible. Manual changes will be overwritten.
                    -edited by hand

                    changed: [web2]
                """),
                "lang": "console",
            },
            {
                "say": "Last, make the handler fire. In `files/nginx-site.conf`, add a comment and `add_header X-Served-By $hostname;` under `server_tokens off;`, then run against lb only. The config task changes, so the handler reloads nginx at the end of the play, and the new header appears. Undo both edits afterwards, or keep them: the next run makes the servers match whatever the files say.",
                "code": t("""
                    $ ansible-playbook first-playbook.yml --diff --limit lb
                    TASK [Replace the default site with ours] **************************************
                    --- before: /etc/nginx/sites-available/default
                    @@ -7,4 +7,7 @@

                         # Do not show the nginx version in headers and error pages.
                         server_tokens off;
                    +
                    +    # Say which server answered.
                    +    add_header X-Served-By $hostname;
                     }
                    changed: [lb1]
                    RUNNING HANDLER [Reload nginx] *************************************************
                    changed: [lb1]
                    $ curl -sI localhost:8180 | grep -i served
                    X-Served-By: lb1
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        code("dockerfile", "Dockerfile", "./setup.sh"),
        code("yaml", "compose.yaml", "./setup.sh"),
        code("bash", "setup.sh", "chmod +x setup.sh && ./setup.sh"),
        code("ini", "ansible.cfg", "ansible-config view"),
        code("ini", "inventory.ini", "ansible-inventory --graph"),
        code("yaml", "inventory.yml", "ansible-inventory -i inventory.yml --graph"),
        code("yaml", "first-playbook.yml", "ansible-playbook first-playbook.yml"),
        code("text", "files/nginx-site.conf", "ansible-playbook first-playbook.yml --diff --limit lb"),
    ],
    "commands": [
        {"cmd": "uv tool install ansible-core", "what": "Install ansible-core and its commands in their own Python environment."},
        {"cmd": "ansible --version", "what": "Show the ansible-core version, the config file in use and the Python it runs on."},
        {"cmd": "./setup.sh", "what": "Make the lab key, build the image and start web1, web2 and lb1; `./setup.sh down` removes them."},
        {"cmd": "ansible-inventory --graph", "what": "Print the groups and hosts of the inventory as a tree."},
        {"cmd": "ansible all -m ansible.builtin.ping", "what": "Log in to every server and check that Python works; prints pong."},
        {"cmd": "ansible web -a 'uptime'", "what": "Run one program on the web group with the command module (no shell)."},
        {"cmd": "ansible web1 -m ansible.builtin.shell -a 'cat /etc/os-release | grep PRETTY'", "what": "Run a line through /bin/sh, so pipes and redirects work."},
        {"cmd": "ansible web -b -m ansible.builtin.apt -a 'name=jq state=present update_cache=true'", "what": "Install a package as root on a group, refreshing the package list first."},
        {"cmd": "ansible lb -b -m ansible.builtin.service -a 'name=nginx state=restarted'", "what": "Restart a service on every host in a group."},
        {"cmd": "ansible-doc ansible.builtin.copy", "what": "Read a module's options and examples in the terminal; `ansible-doc -l` lists all modules."},
        {"cmd": "ansible-playbook first-playbook.yml --syntax-check", "what": "Check the YAML and the playbook structure without contacting any server."},
        {"cmd": "ansible-playbook first-playbook.yml", "what": "Run every play in the playbook and print a recap per host."},
        {"cmd": "ansible-playbook first-playbook.yml --check --diff", "what": "Preview a run: show what would change, line by line, and change nothing."},
        {"cmd": "ansible-playbook first-playbook.yml --limit web2", "what": "Run the playbook on one host or group only."},
        {"cmd": "ansible web1 -m ansible.builtin.ping -vvv", "what": "Show every SSH command Ansible sends, for debugging connections."},
    ],
    "mistake": "Writing tasks as `shell: apt-get install -y nginx` turns Ansible back into a slow shell script. The shell and command modules cannot tell whether anything changed, so they report changed on every run, `--check` cannot preview them, and any handler they notify fires every time. Look for a real module first with `ansible-doc -l | grep apt`, and keep `command` for jobs that no module covers.",
    "real_world": "OpenSSH ships a security fix, and every VM a team runs needs it the same day. With an Ansible repo, someone runs the patch playbook with `--check --diff` on two servers, then on the rest, and the PLAY RECAP lists the hosts that failed. The same playbooks also run on a schedule, so a change made by hand at 2 a.m. is found and reverted the next morning.",
    "task": {
        "title": "Run hello-devops as a systemd service with a playbook",
        "steps": [
            "Keep the lab folder next to your hello-devops repo (`~/code/ansible-lab` and `~/code/hello-devops`). Start the servers with `./setup.sh` and check them with `ansible all -m ansible.builtin.ping`.",
            "Create `my-hello.yml` with one play for the `web` group and `become: true`.",
            "Add tasks that install `python3-venv` and `python3-packaging` with apt, create a system user `hello` with no login shell, and create `/opt/hello-devops`.",
            "Copy `app.py` and `requirements.txt` from your hello-devops repo into `/opt/hello-devops`.",
            "Install the requirements into `/opt/hello-devops/venv` with the `ansible.builtin.pip` module.",
            "Write a systemd unit (Day 6) that runs gunicorn on `0.0.0.0:8000` as the `hello` user, keep it in `files/`, and copy it to `/etc/systemd/system/hello-devops.service`.",
            "Start and enable the service with `ansible.builtin.systemd_service`. Add a handler that restarts it, and notify it from the tasks that copy code or the unit.",
            "Run the playbook, then `curl -s localhost:8101` and `curl -s localhost:8102`. Run it a second time and read the recap.",
            "Add `Environment=\"GREETING=Hi from systemd\"` to the unit (the quotes keep the spaces), run again, and check that only that task and the handler changed. Then run `docker restart ansible-web1` and curl web1 again.",
            "Compare your playbook with the lab's `hello-devops.yml`, one possible answer.",
        ],
        "hints": [
            "If the pip task fails with `No module named 'packaging'`, the pip module needs the python3-packaging package on the server, not on your Mac.",
            "`src:` in a copy task can be a path on your Mac, such as `\"{{ playbook_dir }}/../hello-devops/app.py\"`.",
            "After a unit file changes, systemd must reload its files. `daemon_reload: true` on the systemd_service task and on the handler does that.",
        ],
        "done_when": "You are done when both curls return hello-devops JSON, a second run shows `changed=0` for web1 and web2, and web1 answers again after `docker restart ansible-web1`.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences what happens when you run a playbook against three servers. Mention SSH, modules, idempotence and handlers.",
        "answer": "Ansible reads the inventory, logs in to each server over SSH and runs the tasks in order. For each task it copies a small Python module to the server, runs it with python3 and reads back a JSON result. The module checks the server first and changes only what differs, so a second run reports ok and changes nothing. A handler, such as a reload, runs once at the end of the play, and only if a task that notified it reported a change.",
    },
    "recap": [
        "Terraform creates servers; Ansible configures what runs inside them, as often as you like.",
        "Ansible is agentless: a managed node needs only an SSH login and Python 3.",
        "The inventory lists hosts in groups; ansible.cfg in the current folder sets the defaults.",
        "Modules describe a result and report ok or changed; command and shell always say changed.",
        "--check --diff previews a run against the real servers, because there is no state file.",
        "Handlers run once at the end of a play, and only after a change.",
    ],
    "check": [
        {
            "q": "A nightly playbook has the task `ansible.builtin.shell: echo 'vm.swappiness=10' >> /etc/sysctl.conf`. What does the file look like after a week?",
            "options": [
                "One copy of the line, because Ansible tasks are idempotent",
                "Seven copies of the line, one from every run",
                "No copies, because shell tasks only run in check mode",
                "One copy, because Ansible remembers the first run",
            ],
            "answer": 1,
            "why": "The shell module runs its command every time and cannot know it already ran; `ansible.builtin.lineinfile` with `line:` would add the line once.",
        },
        {
            "q": "The inventory has `[db]` with db1 and db2, `[web]` with web1, and `[prod:children]` listing web and db. Which hosts does `ansible prod -m ansible.builtin.ping` reach?",
            "options": [
                "None, because no host is written under [prod] itself",
                "Only web1, because web is listed first",
                "Only db1 and db2",
                "web1, db1 and db2",
            ],
            "answer": 3,
            "why": "A :children group contains every host of each child group.",
        },
        {
            "q": "Three tasks in one play have `notify: Restart app`. On this run two of them report changed and one reports ok. What happens?",
            "options": [
                "The app restarts once, after the last task of the play",
                "The app restarts twice, right after each changed task",
                "The app restarts three times, once per notify line",
                "Nothing restarts, because one of the tasks reported ok",
            ],
            "answer": 0,
            "why": "A notified handler runs once, at the end of the play, however many tasks notified it.",
        },
    ],
    "interview": [
        {
            "q": "What does agentless mean for Ansible, and what does a server need before Ansible can manage it?",
            "a": "Ansible runs on a control node and leaves nothing running on the servers it manages. For each task it connects over SSH, copies a small Python module to a temporary folder, runs it and deletes it. So a Linux server needs an SSH login, usually with sudo rights, and Python 3. Network devices are the exception: their modules run on the control node and talk to the device over SSH or an API. You have nothing to install or upgrade on servers, but the control node must be able to reach every one of them.",
        },
        {
            "q": "What is idempotence, and how do you keep a playbook idempotent?",
            "a": "An idempotent task gives the same result however often it runs, so a second run with nothing to do changes nothing. Ansible modules do this by checking the current state first and acting only on a difference. I keep playbooks idempotent by using modules that describe a state, such as apt with state=present, copy or template. Where I must use command or shell, I add `creates:` or `changed_when:` so the task can report ok. The test is simple: run the playbook twice and expect changed=0 the second time.",
        },
        {
            "q": "When would you use the command or shell module?",
            "a": "Only when no module does the job, for example a vendor's CLI or a one-off migration command of your own app. The command module runs the program directly with no shell, which is safer, but pipes and redirects do not work. The shell module runs the line through /bin/sh, so pipes work, but you have to quote carefully. Both always report changed, so I add `changed_when` or `creates` to keep the recap honest and stop handlers from firing on every run.",
        },
    ],
    "deeper": {
        "minutes": 12,
        "body": t("""
            Run `ansible web1 -m ansible.builtin.ping -vvv` and read the lines that start with `SSH: EXEC`. Verbose mode shows every command Ansible sends. With pipelining switched off (`ANSIBLE_PIPELINING=False`), one ping took seven SSH or SFTP calls:
            1. Ask the server for the home folder of `ubuntu`.
            2. Make a private temporary folder under `~/.ansible/tmp`.
            3. Look for a Python, trying python3.15, python3.14 and so on down the list.
            4. Copy the module over SFTP as `AnsiballZ_ping.py`.
            5. Make it executable.
            6. Run it with `/usr/bin/python3.12`.
            7. Delete the temporary folder.

            With the lab's `pipelining = True`, the same ping took two calls. Ansible found Python, then sent the module through the open connection's standard input, so nothing was written to disk. The `ControlPersist=60s` option in `ansible.cfg` keeps one SSH connection open for a minute, so the next tasks skip the login. Pipelining needs sudo to work without a terminal, which is the default on Ubuntu.

            Three settings change how a run behaves on many servers:
            - `forks`, or `-f 20` on the command line, sets how many hosts Ansible works on at once. The default is 5.
            - `serial: 2` in a play finishes the whole play on two hosts before it starts the next two. That is how you roll a change through a fleet without touching every server at the same moment.
            - `ansible.builtin.raw` sends a plain command over SSH with no Python. Teams use it to install Python on a bare machine, then switch to real modules.

            Ansible pushes from a control node. `ansible-pull` turns that around: each server clones a git repo and runs a playbook on itself, often from a timer. It suits machines your control node cannot reach, such as laptops on home networks.
        """),
    },
    "sources": [src("start"), src("install"), src("inventory"), src("handlers")],
}

# ================================================================ Day 37
d37 = {
    "id": "d37",
    "title": "Ansible in practice: variables, templates, roles and Vault",
    "minutes": 50,
    "goal": "By the end you can turn a playbook into a role with defaults and templates, decide where each variable belongs, keep a secret in Vault, lint the code in CI, and let Ansible find EC2 servers by tag.",
    "guess": {
        "q": "A role's defaults/main.yml sets `hello_devops_greeting: Hello`. group_vars/web.yml sets it to `Hi`, and host_vars/web2.yml sets it to `Hey`. What does web2 get?",
        "options": [
            "Hello, because the role's own default is the real value",
            "Hey, because the most specific place wins",
            "Hi, because a group setting overrides single hosts",
            "An error, because one variable is set three times",
        ],
        "answer": 1,
        "why": "Role defaults have the lowest precedence of all, so the inventory can override them. Host variables beat group variables, because a value for one host is more specific than a value for its group.",
    },
    "terms": [
        {"term": "Variable precedence", "plain": "The rule that decides which value wins when one variable is set in several places."},
        {"term": "Fact", "plain": "Something Ansible learns about a server at the start of a play, such as its OS or IP address."},
        {"term": "Jinja2 template", "plain": "A text file with {{ variables }} and {% loops %} that Ansible fills in for each host."},
        {"term": "Role", "plain": "A folder with a fixed layout (tasks, handlers, templates, defaults) that packages one job for reuse."},
        {"term": "Collection", "plain": "A package of modules, plugins and roles, such as amazon.aws, installed with ansible-galaxy."},
        {"term": "FQCN", "plain": "A fully qualified collection name: namespace.collection.module, such as ansible.builtin.copy."},
        {"term": "Ansible Vault", "plain": "Encryption built into Ansible, so secrets can sit in git as unreadable text."},
        {"term": "Dynamic inventory", "plain": "An inventory plugin that asks an API, such as AWS, which servers exist right now."},
    ],
    "sections": [
        {
            "h": "Where variables live, and which value wins",
            "body": t("""
                Day 36 hard-coded everything: the port, the folder, the greeting. Variables let one playbook serve many servers that differ a little. You can set them in many places, and the rule for which value wins is called **variable precedence**. The docs list 22 levels. In practice you need seven, from weakest to strongest:
                1. Role defaults, in `roles/NAME/defaults/main.yml`.
                2. `group_vars/all.yml`, for every host.
                3. `group_vars/web.yml` or a `group_vars/web/` folder, for one group.
                4. `host_vars/web2.yml`, for one host.
                5. `vars:` in a play.
                6. Role vars, in `roles/NAME/vars/main.yml`.
                7. Extra vars on the command line, `-e name=value`, which always win.

                Ansible loads the `group_vars` and `host_vars` folders that sit next to the inventory file or the playbook, and it matches file names to group and host names. The lab sets the greeting twice. The file `group_vars/web/vars.yml` says `Hello from Ansible`, and `host_vars/web2.yml` gives web2, the canary, its own text. The command `ansible web -m ansible.builtin.debug -a var=hello_devops_greeting` asks each host what it sees. It printed exactly those two values. With `-e 'hello_devops_greeting="Hi from -e"'` added, both hosts printed `Hi from -e`.

                Look at where role vars sit: above group_vars and host_vars. A value in a role's `vars/` folder cannot be changed from the inventory at all. So `defaults/` is for every setting a user may want to change, and `vars/` for the role's own fixed details.

                My rule is to set each variable in one place, plus its role default. When the same name appears in four files, nobody can predict the result without running it.
            """),
            "refs": [ref("vars", "docs"), ref("ep5", "watch")],
        },
        {
            "h": "Facts and templates: one file, filled in per host",
            "body": t("""
                At the start of each play, the Gathering Facts step runs the setup module on every host. It collects facts: the OS and its version, IP addresses, memory, CPUs and a lot more. Running `ansible web1 -m ansible.builtin.setup -a 'filter=ansible_distribution*'` printed `Ubuntu`, `24.04` and `noble`. In a playbook you read them as `ansible_facts['distribution']`. A play that needs no facts can say `gather_facts: false` and save a few seconds per host.

                Ansible also sets some magic variables itself:
                - `inventory_hostname` is the host's name in the inventory, such as web1.
                - `groups['web']` is the list of hosts in the web group.
                - `hostvars['web1']` holds every variable of another host.

                Templates are where variables and facts pay off. The template module reads a Jinja2 file on your Mac, fills it in for each host and copies the result to the server. Jinja2 has two kinds of markers:
                - `{{ name }}` prints a value.
                - `{% if %}` and `{% for %}` blocks add conditions and loops.

                The role's `hello-devops.service.j2` is Day 36's systemd unit with variables for the user, folder, port and number of workers. The load balancer's `nginx-lb.conf.j2` loops over `groups['web']` and writes one `server` line per web host, with each host's `hello_devops_port` from `hostvars`. Add a third web server to the inventory, run the playbook, and nginx learns about it with no edit to the template. The line `{{ ansible_managed }}` at the top prints `Ansible managed`, a warning to anyone who opens the file on the server. Templates render on the control node, so servers do not need Jinja2.
            """),
            "refs": [ref("templating", "docs"), ref("facts", "docs")],
        },
        {
            "h": "Loops, conditions, handlers and tags",
            "body": t("""
                Four task keywords cover most of the logic you will write:
                - `loop:` runs a task once per item. The role copies `app.py` and `requirements.txt` with one task that loops over `hello_devops_files`, and `item` holds the current entry.
                - `when:` runs a task only if a condition is true. The apt task has `when: ansible_facts['os_family'] == "Debian"`, so the role would skip it on a Red Hat server instead of failing.
                - `notify:` names a handler, as on Day 36. The copy, pip and template tasks all notify `Restart hello-devops`, and the app still restarts once.
                - `tags:` labels tasks, so you can run part of a playbook.

                The role tags its tasks `install` or `config`. Running `ansible-playbook site.yml --list-tags` lists them, and `--tags config` ran only the settings file, the unit, the service and the nginx config. That is useful when you change one template and do not want to wait for apt and pip. The flag `--skip-tags install` does the opposite.

                Handlers have one trap. When a task fails, the play stops for that host, and handlers that were already notified do not run. Say the copy of `app.py` changed, and then the pip task failed. The restart never happens. On the next run the copy reports ok, so nothing notifies the handler again, and the old code keeps running with the new file on disk. The flag `--force-handlers` runs notified handlers even after a failure.
            """),
            "refs": [ref("loops", "docs"), ref("tags", "docs")],
        },
        {
            "h": "Roles and collections: packaging Ansible code",
            "body": t("""
                A role is a folder with a fixed layout, so Ansible knows where to look in it. `ansible-galaxy role init roles/hello_devops` makes the skeleton, and the lab's role uses these parts:
                - `tasks/main.yml` and `handlers/main.yml`, the tasks and their handlers.
                - `templates/`, the `.j2` files, which a template task in the role finds by name alone.
                - `defaults/main.yml`, settings meant to be overridden.
                - `vars/main.yml`, the role's own fixed values.
                - `meta/main.yml`, a description and the supported platforms.

                A play uses the role with `roles: [hello_devops]`, so `site.yml` is two short plays. Put the role's name in front of its variables, as in `hello_devops_port`. All variables of a host share one namespace, so a plain `port` in two roles would clash. ansible-lint enforces this rule.

                Modules come in collections, packages named `namespace.collection`. ansible-core ships `ansible.builtin`, with about 70 modules such as copy, template and apt. Everything else comes from collections such as `amazon.aws`, `community.general` or `community.docker`. A fully qualified name (FQCN) such as `ansible.builtin.copy` says exactly which collection a module comes from. Short names like `copy` still work, but two collections can ship a module with the same short name, so the lab writes full names everywhere.

                List the collections a project needs in `requirements.yml`, with version ranges, and install them with `ansible-galaxy collection install -r requirements.yml`. It is the same idea as `requirements.txt` in Python: your laptop and CI get the same code. The big `ansible` package from Homebrew already bundles amazon.aws and many more. Roles and collections that other people wrote come from Ansible Galaxy. Read one before you run it as root on your servers.
            """),
            "refs": [ref("roles", "docs"), ref("collections", "docs"), ref("ep6", "watch")],
        },
        {
            "h": "Ansible Vault: secrets you can commit",
            "body": t("""
                A playbook often needs a secret, such as a database password or an API token. Ansible Vault encrypts it with AES256 and a password, so the encrypted text can sit in git. You have two ways to use it:
                - `ansible-vault encrypt FILE` (or `create`) encrypts a whole file, names and values.
                - `ansible-vault encrypt_string --name NAME 'value'` encrypts one value and prints a YAML block to paste into a normal vars file.

                The difference showed up in the lab. With a whole encrypted file in `group_vars/web/`, even `ansible web -m ping` failed with `Attempting to decrypt but no vault secrets found`, because Ansible decrypts such files while it loads the inventory. A single encrypted value is decrypted only when a task uses it, so ping and Day 36's playbooks keep working without the password. That is why the lab's `group_vars/web/vault.yml` holds one `encrypt_string` value. The plain `vars.yml` next to it says `hello_devops_api_token: "{{ vault_hello_devops_api_token }}"`. The `vault_` prefix tells readers the real value is encrypted, and grep still finds the plain name.

                You give Ansible the password with `--ask-vault-pass` or `--vault-password-file .vault_pass`. Keep that file out of git, as the lab's `.gitignore` does, with mode 600. Teams keep the real password in a password manager or a CI secret. The lab's token is fake, and its practice password is `practice-only-password`.

                ansible-core 2.22 added **secret masking**: values decrypted from Vault print as `$REDACTED$`, even in `debug` output and in `--diff`. The same `debug` command on ansible-core 2.21, the version inside today's `ansible` package, printed the token in plain text. So the role also sets `diff: false` on the task that writes the secret, which keeps it out of the output on any version.
            """),
            "refs": [ref("vault", "docs"), ref("vault_enc", "docs")],
        },
        {
            "h": "Lint, test and run it from CI",
            "body": t("""
                Three checks catch most mistakes before a server sees them:
                1. `ansible-playbook --syntax-check site.yml` parses the playbook and stops at YAML or structure errors. It contacts no servers.
                2. `ansible-lint` checks style and known traps: short module names, `shell` where a module exists, tasks with no name, risky file modes. The lab's `.ansible-lint` picks the strictest profile, `production`.
                3. A real run against throwaway servers, done twice, where the second run must show `changed=0`.

                Molecule automates the third check. It is a test framework for roles, playbooks and collections, maintained by the Ansible project and released about once a month. A Molecule scenario creates test servers (often containers), applies your role, applies it again to prove idempotence, runs your checks and deletes everything. Its current setup uses ordinary Ansible playbooks and inventory to create and destroy the test servers. The lab skips Molecule, because the compose servers already play that part by hand.

                The lab's `.github/workflows/ansible.yml` runs the first two checks on every pull request. It installs ansible-core, ansible-lint and the collections, and it needs no servers and no secrets. Running playbooks from CI against real servers is the next step. That job needs an SSH key as a secret, a network path to the servers and the vault password.

                Teams that run Ansible a lot often move it to AWX or Red Hat Ansible Automation Platform. Both add a web UI, an API, schedules, access control and a log of every run. AWX is the open source upstream of the Red Hat product, but its releases have been paused since July 2024 during a large rewrite.
            """),
            "refs": [ref("lint", "docs"), ref("molecule", "docs"), ref("ep7", "watch")],
        },
        {
            "h": "Real servers: find them in AWS, and know when not to use Ansible",
            "body": t("""
                A static inventory goes stale on a cloud, where servers come and go. A dynamic inventory asks the cloud instead. The `amazon.aws.aws_ec2` inventory plugin reads a YAML file whose name must end in `aws_ec2.yml`. The lab's `aws/hello.aws_ec2.yml` asks one Region for running instances with the tag `Project=hello-devops`. That is the tag Day 35's `default_tags` puts on everything Terraform creates, so an `aws_instance` you add there shows up by itself. Tag a Day 14 instance the same way and it appears too. The file also:
                - names each host after its `Name` tag, or its instance ID,
                - turns tags into groups, so `Role=web` becomes the group `role_web`,
                - sets `ansible_host` to the public IP and `ansible_user` to `ubuntu`.

                It needs the amazon.aws collection, boto3 next to Ansible (`uv tool install ansible-core --with boto3`) and the AWS login from Day 13. Then `ansible-inventory -i aws/hello.aws_ec2.yml --graph` lists the servers, and two `-i` options combine it with `inventory.ini`. Go deeper runs the plugin against an AWS emulator, so you can try it with no account. Day 14 recommends instances with no open SSH port. Ansible can reach those through SSM Session Manager with the `amazon.aws.aws_ssm` connection plugin, which also needs an S3 bucket for file transfers.

                Ansible is one of several ways to get software onto a server:
                - cloud-init user data (Day 14) runs once, at first boot. It is enough for a server you never change.
                - Ansible changes long-lived servers again and again, and undoes drift.
                - Packer bakes an image with everything installed, often by running Ansible inside the build, so new servers boot ready.
                - Kubernetes replaces containers instead of changing them.

                For a fleet of long-lived VMs, I would pick Ansible. For anything that can be a container, the image is the configuration, and Ansible's part shrinks to preparing the machines underneath.
            """),
            "refs": [ref("aws_ec2", "docs"), ref("packer", "docs")],
        },
    ],
    "analogy": "Variables in Ansible behave like a recipe card in a restaurant chain. The card says two spoons of salt, which is the role default. A branch can write one spoon on its copy (group_vars). A regular guest can ask for no salt at one table (host_vars), and the chef's order on the night beats everything (-e). A real kitchen would notice two orders that disagree and ask. Ansible never asks: it picks the winner by its precedence list, silently, so a forgotten override in host_vars can hide your change for weeks.",
    "diagram": svg37(),
    "diagram_caption": "Higher wins: web2 gets its host_vars greeting unless -e overrides it, and role vars beat the whole inventory.",
    "worked": {
        "title": "Turn the playbook into a role, then steer it with variables",
        "steps": [
            {
                "say": "Let Ansible make the role's skeleton. Then move Day 36's tasks into `tasks/main.yml`, the restart into `handlers/main.yml`, and the unit file into `templates/` as a `.j2` file with variables. Delete `files/`, `tests/` and the README, which this role does not need.",
                "code": t("""
                    $ ansible-galaxy role init roles/hello_devops
                    - Role roles/hello_devops was created successfully
                    $ find roles -type d | sort
                    roles
                    roles/hello_devops
                    roles/hello_devops/defaults
                    roles/hello_devops/files
                    roles/hello_devops/handlers
                    roles/hello_devops/meta
                    roles/hello_devops/tasks
                    roles/hello_devops/templates
                    roles/hello_devops/tests
                    roles/hello_devops/vars
                """),
                "lang": "console",
            },
            {
                "say": "Lint before the first run. The first version of the role used short names like `hello_port`, and ansible-lint stopped with ten findings of one rule (one is shown). After renaming all ten to start with `hello_devops_`, the strictest profile passed. You will also see two deprecation warnings about the oneline and tree callbacks. They come from ansible-lint 26.11 running on ansible-core 2.22, not from your code.",
                "code": t("""
                    $ ansible-lint
                    WARNING  Listing 10 violation(s) that are fatal
                    var-naming[no-role-prefix]: Variables names from within roles should use hello_devops_ as a prefix. (vars: hello_port)
                    roles/hello_devops/defaults/main.yml:6:1
                    $ ansible-lint
                    Passed: 0 failure(s), 0 warning(s) in 21 files processed of 30 encountered. Profile 'production' was required, and it passed.
                """),
                "lang": "console",
            },
            {
                "say": "Write the practice vault password into `.vault_pass` and run `site.yml` over the servers from Day 36, with `--diff`. The template replaces Day 36's static unit, so the diff shows the new lines. The handler restarts the app once per host, and lb1 gets its load balancer config. Output trimmed to web1's unit and the recap.",
                "code": t("""
                    $ printf '%s\\n' 'practice-only-password' > .vault_pass && chmod 600 .vault_pass
                    $ ansible-playbook site.yml --vault-password-file .vault_pass --diff
                    TASK [hello_devops : Write the systemd unit] ***********************************
                    -Description=hello-devops web app
                    +Description=hello-devops 1.0.0
                    -Environment=APP_VERSION=1.0.0
                    +# APP_VERSION, GREETING and the token come from this file (mode 0640).
                    +EnvironmentFile=/etc/hello-devops.env
                    changed: [web1]
                    PLAY RECAP *********************************************************************
                    lb1                        : ok=5    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web1                       : ok=10   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                    web2                       : ok=10   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
                """),
                "lang": "console",
            },
            {
                "say": "Each web server answers with its own greeting, because web2 has a host_vars file. Through the load balancer, requests take turns between web1 and web2. The visit counter jumps around because each of gunicorn's two workers counts in its own memory: there is no Redis here.",
                "code": t("""
                    $ curl -s localhost:8101
                    {"host":"web1","message":"Hello from Ansible","version":"1.0.0","visits":1}
                    $ curl -s localhost:8102
                    {"host":"web2","message":"Hello from web2, the canary","version":"1.0.0","visits":1}
                    $ for i in 1 2 3 4; do curl -s localhost:8180; done
                    {"host":"web1","message":"Hello from Ansible","version":"1.0.0","visits":6}
                    {"host":"web2","message":"Hello from web2, the canary","version":"1.0.0","visits":2}
                    {"host":"web1","message":"Hello from Ansible","version":"1.0.0","visits":1}
                    {"host":"web2","message":"Hello from web2, the canary","version":"1.0.0","visits":3}
                """),
                "lang": "console",
            },
            {
                "say": "Before you trust a change, ask Ansible which value each host sees. `debug` prints a variable after all the precedence rules. Extra vars from `-e` beat everything, for this one command only.",
                "code": t("""
                    $ ansible web -m ansible.builtin.debug -a var=hello_devops_greeting
                    web1 | SUCCESS => {
                        "hello_devops_greeting": "Hello from Ansible"
                    }
                    web2 | SUCCESS => {
                        "hello_devops_greeting": "Hello from web2, the canary"
                    }
                    $ ansible web -m ansible.builtin.debug -a var=hello_devops_greeting -e 'hello_devops_greeting="Hi from -e"'
                    web2 | SUCCESS => {
                        "hello_devops_greeting": "Hi from -e"
                    }
                    web1 | SUCCESS => {
                        "hello_devops_greeting": "Hi from -e"
                    }
                """),
                "lang": "console",
            },
            {
                "say": "Preview a version bump on one server. The unit's diff is one line. The settings file reports changed with no diff, because the role sets `diff: false` on that task. The pip task also says changed, although a real run reports ok: with a requirements file, the pip module cannot tell in check mode. Output trimmed.",
                "code": t("""
                    $ ansible-playbook site.yml --vault-password-file .vault_pass -e hello_devops_version=1.0.1 --check --diff --limit web1
                    TASK [hello_devops : Install the Python packages into a virtual environment] ***
                    changed: [web1]
                    TASK [hello_devops : Write the settings file (holds a secret, so no diff in the output)] ***
                    changed: [web1]
                    TASK [hello_devops : Write the systemd unit] ***********************************
                    @@ -1,7 +1,7 @@
                     # Ansible managed
                     # Rendered for web1 (Ubuntu 24.04).
                     [Unit]
                    -Description=hello-devops 1.0.0
                    +Description=hello-devops 1.0.1
                    changed: [web1]
                """),
                "lang": "console",
            },
            {
                "say": "Last, the secret. ansible-core 2.22 masks values that came from Vault, so `debug` cannot leak the token. On the server the token is in plain text in `/etc/hello-devops.env`, with mode 0640, so only root and the app's `hello` group can read it.",
                "code": t("""
                    $ ansible web1 -m ansible.builtin.debug -a var=hello_devops_api_token --vault-password-file .vault_pass
                    web1 | SUCCESS => {
                        "hello_devops_api_token": "$REDACTED$"
                    }
                    $ ansible web1 -b -a 'ls -l /etc/hello-devops.env'
                    web1 | CHANGED | rc=0 >>
                    -rw-r----- 1 root hello 165 Nov  7 17:30 /etc/hello-devops.env
                """),
                "lang": "console",
            },
        ],
    },
    "code": [
        code("yaml", "site.yml", "ansible-playbook site.yml --vault-password-file .vault_pass"),
        code("yaml", "roles/hello_devops/defaults/main.yml", "ansible web -m ansible.builtin.debug -a var=hello_devops_workers"),
        code("yaml", "roles/hello_devops/vars/main.yml", "ansible-playbook site.yml --vault-password-file .vault_pass"),
        code("yaml", "roles/hello_devops/tasks/main.yml", "ansible-playbook site.yml --vault-password-file .vault_pass --list-tasks"),
        code("yaml", "roles/hello_devops/handlers/main.yml", "ansible-playbook site.yml --vault-password-file .vault_pass"),
        code("ini", "roles/hello_devops/templates/hello-devops.service.j2", "ansible-playbook site.yml --vault-password-file .vault_pass --check --diff"),
        code("text", "roles/hello_devops/templates/hello-devops.env.j2", "ansible-playbook site.yml --vault-password-file .vault_pass --tags config"),
        code("yaml", "roles/hello_devops/meta/main.yml", "ansible-lint"),
        code("text", "templates/nginx-lb.conf.j2", "ansible-playbook site.yml --vault-password-file .vault_pass --limit lb1 --diff"),
        code("yaml", "group_vars/all.yml", "ansible-inventory --host web1"),
        code("yaml", "group_vars/web/vars.yml", "ansible web -m ansible.builtin.debug -a var=hello_devops_greeting"),
        code("yaml", "group_vars/web/vault.yml", "ansible-vault encrypt_string --ask-vault-pass --name vault_hello_devops_api_token 'my-fake-token'"),
        code("yaml", "host_vars/web2.yml", "ansible-inventory --host web2"),
        code("yaml", "requirements.yml", "ansible-galaxy collection install -r requirements.yml"),
        code("yaml", ".ansible-lint", "ansible-lint"),
        code("yaml", "aws/hello.aws_ec2.yml", "ansible-inventory -i aws/hello.aws_ec2.yml --graph"),
        code("yaml", ".github/workflows/ansible.yml", "git push  # then open a pull request and watch the ansible check"),
    ],
    "commands": [
        {"cmd": "ansible-galaxy role init roles/hello_devops", "what": "Create the folders and main.yml files of a new role."},
        {"cmd": "ansible web -m ansible.builtin.debug -a var=hello_devops_greeting", "what": "Print the value each host sees after all precedence rules."},
        {"cmd": "ansible-inventory --host web2", "what": "Show every inventory variable of one host, from group_vars and host_vars."},
        {"cmd": "ansible web1 -m ansible.builtin.setup -a 'filter=ansible_distribution*'", "what": "Show the facts about one server whose names match a pattern."},
        {"cmd": "ansible-playbook site.yml --ask-vault-pass", "what": "Run a playbook that uses Vault, typing the vault password."},
        {"cmd": "ansible-playbook site.yml --vault-password-file .vault_pass --check --diff", "what": "Preview a run, reading the vault password from a file outside git."},
        {"cmd": "ansible-playbook site.yml -e hello_devops_version=1.0.1 --limit web1 --vault-password-file .vault_pass", "what": "Override one variable for this run only, on one host."},
        {"cmd": "ansible-playbook site.yml --list-tags", "what": "List the tags of every play and task."},
        {"cmd": "ansible-playbook site.yml --tags config --vault-password-file .vault_pass", "what": "Run only the tasks tagged config."},
        {"cmd": "ansible-vault encrypt_string --ask-vault-pass --name vault_db_password 'not-a-real-password'", "what": "Encrypt one value and print YAML to paste into a vars file."},
        {"cmd": "ansible-vault create secrets.yml", "what": "Create a new encrypted file in your editor; `view`, `edit`, `encrypt`, `decrypt` and `rekey` work on files too."},
        {"cmd": "ansible-galaxy collection install -r requirements.yml", "what": "Install the collections a project lists, in the versions it allows."},
        {"cmd": "ansible-galaxy collection list", "what": "List the collections installed on this machine and where they are."},
        {"cmd": "ansible-lint", "what": "Check every playbook, role and vars file in this folder against the configured profile."},
        {"cmd": "ansible-playbook --syntax-check site.yml", "what": "Parse a playbook and its roles without contacting any server."},
        {"cmd": "ansible-inventory -i aws/hello.aws_ec2.yml --graph", "what": "Ask AWS which instances match the dynamic inventory and print their groups."},
    ],
    "mistake": "Setting the same variable in a role's `vars/`, in group_vars and in a play's `vars:`, then wondering why a change in the inventory has no effect. Role vars beat group_vars and host_vars, so a greeting placed there cannot be overridden from the inventory, and Ansible gives no warning about it. Keep settings in `defaults/`, set each value in one place, and ask Ansible what it sees with `ansible web -m ansible.builtin.debug -a var=NAME`.",
    "real_world": "Teams that still run VMs usually keep one Ansible repo per platform, with an inventory folder per environment and the same roles for staging and production. Every change goes through a pull request where CI runs ansible-lint and a syntax check, and a reviewer reads the `--check --diff` output for one staging host. The real run happens from AWX, Ansible Automation Platform or a CI job with the SSH key as a secret, never from one person's laptop.",
    "task": {
        "title": "A role for the load balancer, a canary release and your own secret",
        "steps": [
            "Start the servers if needed, write the practice password into `.vault_pass`, and run `ansible-playbook site.yml --vault-password-file .vault_pass` once.",
            "Create a role `roles/lb` with `ansible-galaxy role init`, and delete the folders you will not use.",
            "Move the three tasks and the handler of the lb play into the role, and move `nginx-lb.conf.j2` into the role's `templates/`. Make the listen port a default called `lb_listen_port` and use it in the template.",
            "Change the lb play in `site.yml` to `roles: [lb]` and run with `--check --diff`. Nothing should change on lb1.",
            "Release version 1.1.0 to the canary first: set `hello_devops_version` in `host_vars/web2.yml`, run with `--limit web2`, and curl `localhost:8180` a few times.",
            "Make a vault password of your own. Encrypt a new fake token with `encrypt_string` and replace the value in `group_vars/web/vault.yml`. From now on, run with `--ask-vault-pass`.",
            "Run `ansible-lint` and fix what it finds.",
            "Move the version to `group_vars/all.yml` for everyone, remove it from host_vars, and run `site.yml` twice.",
        ],
        "hints": [
            "Inside a role, `ansible.builtin.template` with `src: nginx-lb.conf.j2` looks in the role's own templates/ folder first.",
            "ansible-lint wants a role's variables to start with the role's name, so `lb_` is right for a role called lb.",
            "`ansible-vault encrypt_string --ask-vault-pass --name vault_hello_devops_api_token 'my-fake-token'` prints a block you can paste into the file as it is.",
        ],
        "done_when": "You are done when ansible-lint passes, a second run of site.yml shows `changed=0` on all three servers, and `curl localhost:8180` shows version 1.1.0 from both web1 and web2.",
    },
    "explain_back": {
        "prompt": "Explain in 3 to 4 sentences how the lab's role gives web2 a different greeting from web1, and why the role keeps the greeting in defaults. Mention precedence and templates.",
        "answer": "The role's defaults/main.yml sets a greeting with the lowest precedence of all. The file group_vars/web/vars.yml overrides it for both web servers, and host_vars/web2.yml overrides it again for web2 only, because host variables beat group variables. The template module then fills the greeting into the settings file on each host, so one template gives each server its own file. If the greeting were in the role's vars/ folder, it would beat group_vars and host_vars, and nobody could change it from the inventory.",
    },
    "recap": [
        "Put knobs in role defaults, shared values in group_vars, exceptions in host_vars, and one-off overrides in -e.",
        "Facts and magic variables such as groups and hostvars feed templates, which render on the control node.",
        "loop, when, notify and tags cover most task logic; a failed play can lose a pending restart.",
        "A role has a fixed layout and prefixes its variables with its name; collections come from requirements.yml.",
        "Encrypt single values with encrypt_string, keep the vault password out of git, and expect $REDACTED$ in 2.22 output.",
        "Lint and syntax-check in CI, and let the aws_ec2 plugin find cloud servers by tag.",
    ],
    "check": [
        {
            "q": "A role's `vars/main.yml` sets `app_port: 9000`. A teammate puts `app_port: 8000` in host_vars/app1.yml and runs the playbook. Which port does app1 get?",
            "options": [
                "8000, because host_vars is the most specific place",
                "9000, because role vars beat host_vars",
                "Both, written to two separate config files",
                "An error about a variable defined twice",
            ],
            "answer": 1,
            "why": "Role vars sit above all inventory variables in the precedence list; move the value to defaults/ so the inventory can change it.",
        },
        {
            "q": "`group_vars/db/vault.yml` is one whole file encrypted with ansible-vault. A teammate without the password runs `ansible db -m ansible.builtin.ping`. What happens?",
            "options": [
                "Ping works, and only tasks that use the secrets fail",
                "Ping works, and the secrets print as $REDACTED$",
                "It fails, because Ansible must decrypt that file to load the db group",
                "It asks for the password and carries on if you press Enter",
            ],
            "answer": 2,
            "why": "A fully encrypted vars file is decrypted when the inventory loads; values made with encrypt_string are decrypted only when a task uses them.",
        },
        {
            "q": "With the lab's `hello.aws_ec2.yml`, you start a new instance tagged `Project=hello-devops` and `Role=db`. Where does it appear in `ansible-inventory --graph`?",
            "options": [
                "In the groups aws_ec2 and role_db",
                "Only in role_web, like the other servers",
                "Nowhere, until you add it to inventory.ini",
                "In ungrouped, because db is not a known role",
            ],
            "answer": 0,
            "why": "The plugin puts every matching instance in aws_ec2, and keyed_groups turns its Role tag into a role_ group.",
        },
    ],
    "interview": [
        {
            "q": "How does Ansible decide which value a variable gets?",
            "a": "Ansible has a fixed precedence order with 22 levels. The ones that matter most, from weak to strong, are role defaults, group_vars/all, group_vars for a group, host_vars, play vars and role vars. Extra vars from -e always win. More specific inventory beats less specific, so a host beats its group. I keep each variable in one place plus its role default, and when in doubt I check with the debug module or `ansible-inventory --host`.",
        },
        {
            "q": "How do you keep secrets in an Ansible repository?",
            "a": "I encrypt them with Ansible Vault, usually value by value with encrypt_string, in a vault_-prefixed variable that a plain vars file refers to. The vault password stays outside git: in a password manager, a CI secret or a mode-600 file listed in .gitignore. Tasks that write secrets get `diff: false` or `no_log`, and ansible-core 2.22 also masks decrypted values in its output. When there are many secrets or they rotate often, teams read them at run time from a secrets manager with a lookup plugin instead.",
        },
        {
            "q": "When would you choose Ansible, and when Packer, cloud-init or Kubernetes?",
            "a": "cloud-init runs once at first boot, which suits simple servers that never change. Ansible fits long-lived servers that need repeated changes and drift fixes, and it also manages network devices. Packer bakes the same changes into an image, so new servers start ready and nothing changes in place, which pairs well with autoscaling. For containerized apps, Kubernetes replaces containers instead of changing them, and Ansible's job shrinks to preparing the nodes.",
        },
    ],
    "deeper": {
        "minutes": 15,
        "body": t("""
            The aws_ec2 plugin only reads from AWS, so you can try it against an emulator. The moto library imitates AWS APIs in Python, and its server mode answers on a local port. Everything below is free and stays on your Mac.

            1. Give Ansible boto3 and the collection: `uv tool install ansible-core --with boto3`, then `ansible-galaxy collection install -r requirements.yml`.
            2. In a second terminal, start the emulator: `uvx --from 'moto[server]' moto_server -p 5055`.
            3. Back in the lab folder, use fake credentials so nothing can reach a real account: `export AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing AWS_URL=http://127.0.0.1:5055`. The plugin reads `AWS_URL` as its endpoint.
            4. Create two instances with the course tag and one without, using `aws ec2 run-instances` from Day 13 with `--endpoint-url http://127.0.0.1:5055 --region us-east-1`. moto accepts any image ID, such as `ami-12345678`. Tag them with `--tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=hello-web-1},{Key=Project,Value=hello-devops},{Key=Role,Value=web}]'`.
            5. Run `ansible-inventory -i aws/hello.aws_ec2.yml --graph`.

            When we did this, the graph showed `hello-web-1` and `hello-web-2` in two groups, `aws_ec2` and `role_web`. The third instance, tagged `Project=billing`, was missing, because the filter dropped it. Running `ansible-inventory -i aws/hello.aws_ec2.yml --host hello-web-1` printed what AWS knows about the host, including `ec2_tags`, `instance_type`, `private_ip_address` and the `ansible_host` that `compose` set from the public IP.

            Two details matter before you use this for real. First, the plugin's old `tags` host variable is being replaced by `ec2_tags`, and `use_deprecated_tags: false` in the lab's file switches the old one off now. Second, a dynamic inventory works with group_vars like any other. A file `group_vars/role_web.yml` next to your playbooks applies to every instance tagged `Role=web`, whatever its name. With `--playbook-dir .`, `ansible-inventory --host` showed a test variable from such a file on hello-web-1.

            Two `-i` options merge inventories: `ansible-inventory -i inventory.ini -i aws/hello.aws_ec2.yml --graph` printed the lab's three containers and the cloud hosts in one tree. Stop moto with Ctrl+C when you are done. Nothing was created in AWS.
        """),
    },
    "sources": [src("vars"), src("roles"), src("vault"), src("aws_ec2")],
}

# ================================================================ Part
part = {
    "part": 9,
    "title": "Configuration management with Ansible",
    "intro": "Terraform gave you servers, and the next question is what runs on them and who keeps it that way. Ansible logs in over SSH, makes each server match what your files describe, and leaves alone whatever already matches. Both days run against three small practice servers in Docker on your Mac, so nothing costs money. Day 37 ends by letting Ansible find EC2 servers by tag, which you can also try against a local AWS emulator.",
    "lessons": [d36, d37],
    "recap": [
        "Configuration management keeps servers matching what your files say; Terraform makes servers, Ansible sets them up.",
        "Ansible is agentless: it logs in over SSH, runs a Python module, reads the JSON result and cleans up.",
        "An inventory lists hosts in groups; the ansible.cfg in your project folder holds the defaults.",
        "Modules describe a state and report ok or changed, so a second run should show changed=0.",
        "--check --diff previews a run against the real servers, since Ansible keeps no state file.",
        "Precedence runs from role defaults up through group_vars, host_vars, play vars and role vars to -e, which always wins.",
        "Roles package tasks, handlers, templates and defaults; collections package modules and come from requirements.yml.",
        "Vault keeps secrets encrypted in git, and the vault password never goes into the repo.",
        "ansible-lint and --syntax-check run in CI; Molecule tests roles end to end on throwaway servers.",
        "The aws_ec2 dynamic inventory finds cloud servers by tag instead of a hand-written list.",
    ],
    "flashcards": [
        {"front": "What does Ansible do that Terraform does not?", "back": "It configures what runs inside existing servers (packages, files, services) over SSH, and can repeat that any time."},
        {"front": "What does a Linux server need before Ansible can manage it?", "back": "An SSH login, usually with sudo, and Python 3. No Ansible agent."},
        {"front": "ansible-core or ansible: which package is smaller?", "back": "ansible-core: the engine plus ansible.builtin. The ansible package adds many community collections."},
        {"front": "In which order does Ansible look for its config file?", "back": "ANSIBLE_CONFIG, then ./ansible.cfg, ~/.ansible.cfg and /etc/ansible/ansible.cfg. The first one found is used."},
        {"front": "Why does `ansible web1 -a 'cat f | grep x'` fail?", "back": "The default command module runs no shell, so cat receives the pipe as a file name. Use the shell module."},
        {"front": "What do ok and changed count in PLAY RECAP?", "back": "ok counts tasks that succeeded; changed counts the ones that also changed something on the server."},
        {"front": "When does a handler run?", "back": "Once, at the end of the play, and only if a task that notified it reported changed."},
        {"front": "What do --check and --diff do?", "back": "--check predicts changes without making them; --diff shows the lines a task changes in a file."},
        {"front": "Order these from weakest to strongest: host_vars, role defaults, -e, group_vars.", "back": "Role defaults, group_vars, host_vars, -e."},
        {"front": "Role defaults/ or vars/ for a setting users may change?", "back": "defaults/. Role vars beat inventory variables, so nobody could override them from group_vars or host_vars."},
        {"front": "What is an FQCN?", "back": "A module's full name, namespace.collection.module, such as ansible.builtin.copy."},
        {"front": "How do you install the collections a project needs?", "back": "ansible-galaxy collection install -r requirements.yml"},
        {"front": "encrypt or encrypt_string for a secret in group_vars?", "back": "encrypt_string. One encrypted value is decrypted only when used; a whole encrypted file needs the password for every command."},
        {"front": "Where should the vault password live?", "back": "Outside git: a password manager, a CI secret, or a mode-600 file listed in .gitignore."},
        {"front": "What does the aws_ec2 inventory plugin do?", "back": "It asks AWS which EC2 instances exist, filtered by tags and state, and turns them into hosts and groups."},
        {"front": "What does Molecule test?", "back": "A role or playbook end to end: it creates test servers, applies it twice to check idempotence, verifies and deletes."},
    ],
    "resources": [
        {"title": L["start"][0], "url": L["start"][1], "kind": "docs", "why": "The official tour of control nodes, inventories and playbooks, with a quick start you can follow on the lab servers."},
        {"title": L["sample"][0], "url": L["sample"][1], "kind": "docs", "why": "How the docs suggest laying out a real project: inventories per environment, group_vars, host_vars and roles."},
        {"title": L["vars"][0], "url": L["vars"][1], "kind": "docs", "why": "The full list of 22 precedence levels, for when the simplified ladder from Day 37 is not enough."},
        {"title": L["vault"][0], "url": L["vault"][1], "kind": "docs", "why": "Vault IDs, password scripts and the limits of what Vault protects, beyond the two commands the lab uses."},
        {"title": L["lint"][0], "url": L["lint"][1], "kind": "docs", "why": "Every rule with an example of good and bad code, and the profiles from min up to production."},
        {"title": L["molecule"][0], "url": L["molecule"][1], "kind": "docs", "why": "Guides for testing a role, a playbook or a collection, when you want the Day 37 checks automated."},
        {"title": L["aws_ec2"][0], "url": L["aws_ec2"][1], "kind": "docs", "why": "Every option of the dynamic inventory: filters, hostnames, keyed_groups, compose and caching."},
        {"title": L["playlist"][0], "url": L["playlist"][1], "kind": "watch", "why": "A live-streamed course from 2020 that goes from ad-hoc commands to roles, Vault and Molecule; some module names have changed since."},
        {"title": L["lltv"][0], "url": L["lltv"][1], "kind": "watch", "why": "A calm beginner course in short episodes, useful if you want a second explanation of each step."},
        {"title": L["book"][0], "url": L["book"][1], "kind": "read", "why": "The book the Ansible 101 videos follow, kept up to date by its author, with full real-world examples."},
        {"title": L["packer"][0], "url": L["packer"][1], "kind": "docs", "why": "How to run your roles inside a Packer build, so new servers boot with everything already installed."},
    ],
    "quiz": [
        {
            "q": "Someone edits nginx.conf by hand on one of twenty servers that a template task manages. What happens on the next playbook run?",
            "options": [
                "Ansible skips that server, because its file is newer",
                "The template task reports changed on that one server and puts the file back",
                "All twenty servers report changed, because one file differs",
                "Ansible stops and asks which version of the file to keep",
            ],
            "answer": 1,
            "why": "Each host is checked on its own, and only the server whose file differs from the rendered template gets changed.",
        },
        {
            "q": "Why does Ansible need no agent on the servers it manages?",
            "options": [
                "It sends a short-lived Python module over SSH for each task",
                "It installs a background service the first time it connects",
                "It only reads files from servers and never changes them",
                "It uses the cloud provider's API to change files on disks",
            ],
            "answer": 0,
            "why": "The module runs, prints JSON and is deleted, so nothing of Ansible stays running on the server.",
        },
        {
            "q": "`ansible web -a 'ls /var/log/*.log'` prints `No such file or directory`, although .log files exist. Why?",
            "options": [
                "The web group has no hosts in the inventory",
                "ls needs become: true to read /var/log",
                "The command module runs no shell, so the * is not expanded",
                "Ad-hoc commands cannot take arguments with slashes",
            ],
            "answer": 2,
            "why": "Globs like * are expanded by a shell; use the shell module, or the find module, for this.",
        },
        {
            "q": "A role default sets `app_port: 8000`, the play's vars set `8080`, and you run with `-e app_port=9090`. Which port is used?",
            "options": [
                "8000, because the role author chose it",
                "8080, because play vars beat everything in a play",
                "It differs from host to host",
                "9090, because extra vars always win",
            ],
            "answer": 3,
            "why": "Extra vars sit at the top of the precedence list.",
        },
        {
            "q": "Which command encrypts one value so you can paste it into an otherwise readable vars file?",
            "options": [
                "ansible-vault encrypt group_vars/all/vars.yml",
                "ansible-vault encrypt_string --name db_password 'x'",
                "ansible-vault rekey --new-vault-password-file new.txt vars.yml",
                "ansible-vault create --vault-id dev@prompt vars.yml",
            ],
            "answer": 1,
            "why": "encrypt_string prints a `!vault |` block for one variable, and the rest of the file stays plain text.",
        },
        {
            "q": "An instance has the tag `Project=hello-devops` but is stopped. Does the lab's aws_ec2 inventory list it?",
            "options": [
                "Yes, because its Project tag matches the filter",
                "Yes, but only in the ungrouped group at the end",
                "No, because the file keeps only running instances",
                "No, because stopped instances lose all of their tags",
            ],
            "answer": 2,
            "why": "Both filters must match, and the second one keeps only running instances.",
        },
        {
            "q": "A role should let users change its listen port. Where does `nginx_port: 80` belong?",
            "options": [
                "In roles/nginx/defaults/main.yml",
                "In roles/nginx/vars/main.yml",
                "In the template, written as 80",
                "In ansible.cfg under [defaults]",
            ],
            "answer": 0,
            "why": "Defaults have the lowest precedence, so group_vars, host_vars or -e can override them.",
        },
        {
            "q": "Terraform and Ansible both describe servers in files. Which keeps a record of what it created, so that it can delete those things later?",
            "options": [
                "Ansible, in its PLAY RECAP",
                "Both, in their state files",
                "Neither; the cloud provider keeps the record",
                "Terraform, in its state file",
            ],
            "answer": 3,
            "why": "Terraform's state maps code to real resources (Day 33); Ansible keeps no state, so deleting a task never removes what it installed.",
            "from": "Part 8",
        },
        {
            "q": "A playbook uses `ansible.builtin.systemd_service` with `state: started` but no `enabled: true`. What happens after the server reboots?",
            "options": [
                "The service starts, because Ansible remembers it",
                "The service stays stopped until something starts it again",
                "systemd starts every service that ran before the reboot",
                "The playbook runs again by itself at boot",
            ],
            "answer": 1,
            "why": "started is about now and enabled is about boot, the same split as systemctl start and systemctl enable on Day 6.",
            "from": "Part 1",
        },
    ],
}

import re as _re
for _L in part["lessons"]:
    for _st in _L["worked"]["steps"]:
        if _st.get("code"):
            _st["code"] = "\n".join(_re.sub(r" \*{3,}$", "", ln) for ln in _st["code"].split("\n"))
OUT.write_text(json.dumps(part, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
