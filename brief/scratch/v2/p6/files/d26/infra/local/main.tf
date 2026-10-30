# A private network, so the app can reach Redis by its name (Day 14).
resource "docker_network" "app" {
  name = "hello-net"
}

resource "docker_image" "redis" {
  name         = "redis:8-alpine"
  keep_locally = true # Compose uses this image too, so never delete it
}

resource "docker_container" "redis" {
  name  = "hello-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.app.name
  }
}

locals {
  # Settings for the app. GREETING is only added when you set one.
  app_env = merge(
    {
      REDIS_HOST  = docker_container.redis.name
      APP_VERSION = var.app_version
    },
    var.greeting == "" ? {} : { GREETING = var.greeting },
  )
}

resource "docker_container" "web" {
  name  = "hello-web"
  image = var.app_image
  # Turns {REDIS_HOST = "hello-redis", ...} into ["REDIS_HOST=hello-redis", ...].
  env = [for key, value in local.app_env : "${key}=${value}"]

  ports {
    internal = 8000
    external = var.host_port
  }

  networks_advanced {
    name = docker_network.app.name
  }
}
