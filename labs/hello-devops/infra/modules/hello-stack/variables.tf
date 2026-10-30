variable "name" {
  description = "Prefix for every name in this stack, for example hello or hello-test."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.name))
    error_message = "name must start with a letter and use only lowercase letters, digits and dashes."
  }
}

variable "host_port" {
  description = "Port on your laptop that forwards to the app."
  type        = number

  validation {
    condition     = var.host_port >= 1024 && var.host_port <= 65535
    error_message = "host_port must be between 1024 and 65535."
  }
}

variable "app_image" {
  description = "The hello-devops image to run, for example hello-devops:1.0.0."
  type        = string
}

variable "app_version" {
  description = "Shown by the app at /."
  type        = string
  default     = "dev"
}

variable "greeting" {
  description = "Message the app shows at /. Empty means the app's own default."
  type        = string
  default     = ""
}

variable "redis_image" {
  description = "ID of the Redis image to run, from a docker_image resource in the caller."
  type        = string
}
