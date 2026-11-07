# Ansible lab (Part 9, Days 36 and 37)

Three practice servers on your Mac, and the Ansible code that configures them.

- `web1` and `web2` run hello-devops as a systemd service (SSH on ports 2201 and 2202, the app on 8101 and 8102).
- `lb1` runs nginx in front of them (SSH on 2203, nginx on 8180).

## Start

```bash
cp -R ~/code/devops-from-zero/labs/ansible ~/code/ansible-lab
cd ~/code/ansible-lab
./setup.sh                 # makes .keys/id_ed25519, builds the image, starts 3 servers
ansible all -m ping        # every server answers "pong"
```

The playbooks copy `app.py` and `requirements.txt` from `../hello-devops`, so keep this
folder next to your hello-devops repo (`~/code/hello-devops`).

## Files

| File | Day | What it is |
|---|---|---|
| `Dockerfile`, `compose.yaml`, `setup.sh` | 36 | The practice servers: Ubuntu 24.04 with systemd, sshd and Python 3 |
| `ansible.cfg`, `inventory.ini`, `inventory.yml` | 36 | Settings and the inventory, in INI and in YAML |
| `ping.yml`, `first-playbook.yml`, `files/` | 36 | First playbooks |
| `hello-devops.yml` | 36 | One answer to the Day 36 task (try your own first) |
| `site.yml`, `roles/hello_devops/`, `templates/` | 37 | The role, the load balancer and its template |
| `group_vars/`, `host_vars/` | 37 | Variables per group and per host, and a Vault secret |
| `requirements.yml`, `.ansible-lint`, `.github/workflows/ansible.yml` | 37 | Collections, linting and CI |
| `aws/hello.aws_ec2.yml` | 37 | A dynamic inventory that finds EC2 instances by tag |

## Vault

`group_vars/web/vault.yml` holds a fake token encrypted with the practice password
`practice-only-password`. It is printed here only so the lab runs. A real vault password
lives in a password manager, never in a repo.

```bash
printf '%s\n' 'practice-only-password' > .vault_pass && chmod 600 .vault_pass
ansible-playbook site.yml --vault-password-file .vault_pass
```

## Stop

```bash
./setup.sh down            # removes the containers, the network and the image
```

The servers run systemd inside Docker, which needs `privileged: true`. That is fine for a
practice lab on your laptop and wrong anywhere else.
