variable "app_image" {
  description = "The hello-devops image to run. Build it first with docker build."
  type        = string
  default     = "hello-devops:1.0.0"
}

variable "app_version" {
  description = "Shown by the app at /."
  type        = string
  default     = "1.0.0"
}

variable "greeting" {
  description = "Message the app shows at /. Empty means the app's own default."
  type        = string
  default     = ""
}

variable "host_port" {
  description = "Port on your laptop that forwards to the app."
  type        = number
  default     = 8080

  validation {
    condition     = var.host_port >= 1024 && var.host_port <= 65535
    error_message = "host_port must be between 1024 and 65535."
  }
}
