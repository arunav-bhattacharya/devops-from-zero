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

# One module block, two copies: for_each makes one per map entry.
module "site" {
  source   = "./modules/site"
  for_each = { blue = 18221, green = 18222 }

  name  = "p4-site-${each.key}"
  image = docker_image.nginx.image_id
  port  = each.value
}

output "sites" {
  value = module.site
}
