# A practice server: Ubuntu 24.04 with systemd, an SSH server and Python 3,
# close to a fresh Ubuntu cloud server. Built by setup.sh. Lab use only.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# systemd runs services (Day 6), openssh-server lets Ansible log in,
# python3 runs Ansible's modules, sudo lets the ubuntu user become root.
# python3-apt is what the apt module uses; cloud images ship it too.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       systemd systemd-sysv dbus openssh-server sudo \
       python3 python3-apt ca-certificates curl iproute2 less \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Drop units that make no sense in a container (consoles, hardware events).
RUN rm -f /lib/systemd/system/getty.target \
          /lib/systemd/system/systemd*udev* \
          /etc/systemd/system/getty.target.wants/* \
    && systemctl mask console-getty.service

# Each container makes its own SSH host keys on first boot, like a real
# server, so delete the ones the package made at build time.
RUN rm -f /etc/ssh/ssh_host_* \
    && mkdir -p /etc/systemd/system/ssh.service.d \
    && printf '[Service]\nExecStartPre=\nExecStartPre=/usr/bin/ssh-keygen -A\nExecStartPre=/usr/sbin/sshd -t\n' \
       > /etc/systemd/system/ssh.service.d/10-hostkeys.conf \
    && systemctl enable ssh.service

# Key login only, no passwords, no root login.
RUN printf 'PasswordAuthentication no\nPermitRootLogin no\n' \
       > /etc/ssh/sshd_config.d/10-lab.conf

# The ubuntu user already exists in this image (UID 1000). Like on a cloud
# server, it may use sudo without a password, and it trusts the lab's public
# key. The private key never enters the image (see .dockerignore).
RUN echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-ubuntu \
    && chmod 440 /etc/sudoers.d/90-ubuntu
COPY --chown=ubuntu:ubuntu --chmod=600 .keys/id_ed25519.pub /home/ubuntu/.ssh/authorized_keys
RUN chown ubuntu:ubuntu /home/ubuntu/.ssh && chmod 700 /home/ubuntu/.ssh

# systemd stops cleanly on this signal; plain SIGTERM makes it re-execute.
STOPSIGNAL SIGRTMIN+3

# systemd is PID 1, as on a real server.
CMD ["/sbin/init"]
