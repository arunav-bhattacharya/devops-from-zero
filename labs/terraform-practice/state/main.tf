# Day 27 worked example: look inside state, rename with moved, adopt with import.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name         = "nginx:1.30-alpine"
  keep_locally = true
}

# This resource started life as docker_container.web.
resource "docker_container" "site" {
  name  = "state-web"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8111
  }
}

# Same container, new address. Terraform renames it in state, nothing is rebuilt.
moved {
  from = docker_container.web
  to   = docker_container.site
}
