# Day 26: count vs for_each. No Docker needed: these resources are plain files.
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.9"
    }
  }
}

variable "names" {
  description = "One file per name, made twice: once with count, once with for_each."
  type        = list(string)
  default     = ["alpha", "bravo", "charlie"]
}

# count: copies are numbered 0, 1, 2. The number is the copy's identity.
resource "local_file" "by_count" {
  count    = length(var.names)
  filename = "${path.module}/out/count-${count.index}.txt"
  content  = "hello ${var.names[count.index]}\n"
}

# for_each: copies are named after each key. The key is the copy's identity.
resource "local_file" "by_each" {
  for_each = toset(var.names)
  filename = "${path.module}/out/each-${each.key}.txt"
  content  = "hello ${each.key}\n"
}

output "count_files" {
  value = local_file.by_count[*].filename
}

output "each_files" {
  value = { for name, file in local_file.by_each : name => file.filename }
}
