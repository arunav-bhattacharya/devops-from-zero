output "url" {
  description = "Where this stack's app answers on your laptop."
  value       = "http://localhost:${var.host_port}"
}

output "containers" {
  description = "The containers in this stack."
  value       = [docker_container.redis.name, docker_container.app.name]
}

output "network" {
  description = "The stack's private network."
  value       = docker_network.app.name
}
