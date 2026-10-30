# Both stacks use this image, so it lives here and not in the module.
resource "docker_image" "redis" {
  name         = "redis:8-alpine"
  keep_locally = true # Compose uses this image too, so never delete it
}

# Your everyday stack. Its names (hello-web, hello-redis, hello-net)
# are the same as before Day 28, so moved.tf can keep its containers.
module "dev" {
  source = "../modules/hello-stack"

  name        = "hello"
  host_port   = var.dev_port
  app_image   = var.app_image
  app_version = var.app_version
  redis_image = docker_image.redis.image_id
}

# A second, separate copy for trying things out.
module "test" {
  source = "../modules/hello-stack"

  name        = "hello-test"
  host_port   = var.test_port
  app_image   = var.app_image
  app_version = var.app_version
  greeting    = "Hello from the test stack!"
  redis_image = docker_image.redis.image_id
}
