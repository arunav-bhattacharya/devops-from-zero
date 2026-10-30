output "url" {
  description = "Open this in your browser."
  value       = "http://localhost:${var.host_port}"
}

output "containers" {
  description = "The containers this folder manages."
  value       = [docker_container.redis.name, docker_container.web.name]
}
