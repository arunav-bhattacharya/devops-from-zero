# These blocks tell Terraform that resources changed address, not that
# they are new. Without them, the next apply would destroy the containers
# you already have and create new ones. On a fresh laptop they do nothing.

# Day 27: the app container's address changed from web to app.
moved {
  from = docker_container.web
  to   = docker_container.app
}

# Day 28: the stack moved into the hello-stack module, as module.dev.
moved {
  from = docker_network.app
  to   = module.dev.docker_network.app
}

moved {
  from = docker_container.redis
  to   = module.dev.docker_container.redis
}

moved {
  from = docker_container.app
  to   = module.dev.docker_container.app
}
