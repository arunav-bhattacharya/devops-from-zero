# The prod environment: its own folder, its own state file.
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

  name    = "site-prod"
  port    = 8202
  message = "Hello from prod"
}

output "url" {
  value = module.site.url
}
