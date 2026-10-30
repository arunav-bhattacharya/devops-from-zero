# Day 25: your first Terraform. One nginx container on your laptop.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

# Talk to the Docker engine on your laptop. No cloud account needed.
provider "docker" {}

# Like `docker pull nginx:1.30-alpine`.
resource "docker_image" "nginx" {
  name         = "nginx:1.30-alpine"
  keep_locally = true # on destroy, leave the image on your laptop
}

# Like `docker run -d --name tf-web -p 8090:80 nginx:1.30-alpine`.
resource "docker_container" "web" {
  name    = "tf-web"
  image   = docker_image.nginx.image_id
  restart = "no"

  ports {
    internal = 80
    external = 8090
  }
}
