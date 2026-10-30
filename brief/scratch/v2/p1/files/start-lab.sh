#!/usr/bin/env bash
# start-lab.sh: open a Linux practice shell for Part 1 of the course.
# Run it from the folder that holds the practice files:  bash start-lab.sh
#
# What the docker run options mean:
#   -it          interactive, with a terminal, so you can type into bash
#   --rm         delete the container when you exit (your files stay, see -v)
#   -v "$PWD":/work   show this folder inside the container as /work
#   -w /work     start in /work
# Inside, apt-get installs the extra tools the lessons use, then bash starts.
docker run -it --rm -v "$PWD":/work -w /work ubuntu:24.04 \
  bash -c 'apt-get update -qq && apt-get install -y -qq less tree jq file curl lsof iproute2 psmisc shellcheck > /dev/null && exec bash'
