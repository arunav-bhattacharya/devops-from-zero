terraform {
  required_providers {
    docker = { source = "kreuzwerker/docker" }
  }
}

variable "name" { type = string }
variable "image" { type = string }
variable "port" { type = number }

resource "docker_container" "this" {
  name  = var.name
  image = var.image
  ports {
    internal = 80
    external = var.port
  }
}

output "url" { value = "http://localhost:${var.port}" }
