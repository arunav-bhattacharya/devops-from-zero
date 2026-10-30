# Day 28 worked example: a tiny module that runs one nginx site.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 4.6, < 5.0"
    }
  }
}

variable "name" {
  description = "Name of the container."
  type        = string
}

variable "port" {
  description = "Port on your laptop."
  type        = number
}

variable "message" {
  description = "Text the page shows."
  type        = string
}

resource "docker_image" "nginx" {
  name         = "nginx:1.30-alpine"
  keep_locally = true
}

resource "docker_container" "site" {
  name  = var.name
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = var.port
  }

  upload {
    file    = "/usr/share/nginx/html/index.html"
    content = "<h1>${var.message}</h1>\n"
  }
}

output "url" {
  description = "Where the site answers."
  value       = "http://localhost:${var.port}"
}
