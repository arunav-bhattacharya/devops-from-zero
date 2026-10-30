# Day 26 hands-on: one nginx container per entry in a map, with for_each.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

provider "docker" {}

variable "sites" {
  description = "One nginx site per entry: site name => port on your laptop."
  type        = map(number)
  default = {
    blue  = 8101
    green = 8102
    red   = 8103
  }

  validation {
    condition     = alltrue([for port in values(var.sites) : port >= 1024 && port <= 65535])
    error_message = "Every port must be between 1024 and 65535."
  }
}

resource "docker_image" "nginx" {
  name         = "nginx:1.30-alpine"
  keep_locally = true
}

resource "docker_container" "site" {
  for_each = var.sites

  name  = "site-${each.key}"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = each.value
  }

  # Replace nginx's welcome page with one that names the site.
  upload {
    file    = "/usr/share/nginx/html/index.html"
    content = "<h1>Hello from ${each.key}</h1>\n"
  }
}

output "urls" {
  description = "One URL per site."
  value       = { for name, port in var.sites : name => "http://localhost:${port}" }
}
