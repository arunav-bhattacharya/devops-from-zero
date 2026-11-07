output "url" {
  description = "The dev stack. Open this in your browser."
  value       = module.dev.url
}

output "test_url" {
  description = "The test stack."
  value       = module.test.url
}

output "containers" {
  description = "Every container this folder manages."
  value       = concat(module.dev.containers, module.test.containers)
}
