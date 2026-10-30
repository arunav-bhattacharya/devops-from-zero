terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

# Talk to Docker on your laptop. No cloud account needed.
provider "docker" {}

# Pull an image, like `docker pull nginx:1.30-alpine`.
resource "docker_image" "nginx" {
  name = "nginx:1.30-alpine"
}

# Run a container from it, like `docker run -d -p 8090:80 nginx`.
resource "docker_container" "web" {
  name    = "p4-tf-web"
  image   = docker_image.nginx.image_id
  restart = "unless-stopped"

  ports {
    internal = 80
    external = 18202
  }
}
