resource "docker_image" "redis" {
  name = "redis:8-alpine"
}

resource "docker_container" "redis" {
  name  = "p4-hello-redis"
  image = docker_image.redis.image_id
}
