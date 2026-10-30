terraform {
  required_version = ">= 1.10"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

# Talks to the Docker engine on your laptop. No cloud account needed.
# The modules below use this provider too.
provider "docker" {}
