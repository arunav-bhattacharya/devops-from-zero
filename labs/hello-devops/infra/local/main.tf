# A private network so the app can reach Redis by name.
resource "docker_network" "app" {
  name = "hello-net"
}

resource "docker_image" "redis" {
  name = "redis:8-alpine"
}

resource "docker_container" "redis" {
  name  = "hello-redis"
  image = docker_image.redis.image_id
  networks_advanced {
    name = docker_network.app.name
  }
}

resource "docker_container" "web" {
  name  = "hello-web"
  image = var.app_image
  env = [
    "REDIS_HOST=${docker_container.redis.name}",
    "APP_VERSION=${var.app_version}",
  ]
  ports {
    internal = 8000
    external = var.host_port
  }
  networks_advanced {
    name = docker_network.app.name
  }
}
