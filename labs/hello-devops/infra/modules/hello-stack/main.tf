# One hello-devops stack: a private network, Redis, and the app.
# Every name starts with var.name, so two stacks never collide.

resource "docker_network" "app" {
  name = "${var.name}-net"
}

resource "docker_container" "redis" {
  name  = "${var.name}-redis"
  image = var.redis_image

  networks_advanced {
    name = docker_network.app.name
  }
}

locals {
  # Settings for the app. GREETING is only added when the caller sets one.
  app_env = merge(
    {
      REDIS_HOST  = docker_container.redis.name
      APP_VERSION = var.app_version
    },
    var.greeting == "" ? {} : { GREETING = var.greeting },
  )
}

resource "docker_container" "app" {
  name  = "${var.name}-web"
  image = var.app_image
  env   = [for key, value in local.app_env : "${key}=${value}"]

  ports {
    internal = 8000
    external = var.host_port
  }

  networks_advanced {
    name = docker_network.app.name
  }
}
