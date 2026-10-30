# Redis for hello-devops, managed by Terraform instead of `docker run`.
resource "docker_image" "redis" {
  name         = "redis:8-alpine"
  keep_locally = true # Compose uses this image too, so never delete it
}

resource "docker_container" "redis" {
  name  = "hello-redis"
  image = docker_image.redis.image_id
}
