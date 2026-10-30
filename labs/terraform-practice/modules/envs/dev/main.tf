# The dev environment: its own folder, its own state file.
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}

provider "docker" {}

module "site" {
  source = "../../modules/site"

  name    = "site-dev"
  port    = 8201
  message = "Hello from dev"
}

output "url" {
  value = module.site.url
}
