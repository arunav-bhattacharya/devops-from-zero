# Tests for the hello-stack module. Run them from infra/modules/hello-stack:
#   terraform init && terraform test
# The mock provider pretends to be Docker, so no containers are created.
mock_provider "docker" {}

variables {
  name        = "hello-test"
  host_port   = 8082
  app_image   = "hello-devops:1.0.0"
  app_version = "1.0.0"
  redis_image = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

run "names_start_with_the_stack_name" {
  command = plan

  assert {
    condition     = docker_container.app.name == "hello-test-web"
    error_message = "The app container should be called <name>-web."
  }

  assert {
    condition     = docker_network.app.name == "hello-test-net"
    error_message = "The network should be called <name>-net."
  }
}

run "app_talks_to_its_own_redis" {
  command = plan

  assert {
    condition     = contains(docker_container.app.env, "REDIS_HOST=hello-test-redis")
    error_message = "REDIS_HOST must point at this stack's Redis container."
  }
}

run "greeting_is_optional" {
  command = plan

  variables {
    greeting = "Hi from a test"
  }

  assert {
    condition     = contains(docker_container.app.env, "GREETING=Hi from a test")
    error_message = "A greeting should reach the app as GREETING."
  }
}

run "url_uses_the_host_port" {
  # apply with a mock provider: Terraform runs the whole module, nothing real is made.
  command = apply

  assert {
    condition     = output.url == "http://localhost:8082"
    error_message = "The url output should use host_port."
  }
}

run "rejects_privileged_ports" {
  command = plan

  variables {
    host_port = 80
  }

  expect_failures = [var.host_port]
}
