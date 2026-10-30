variable "app_image" {
  description = "The app image to run (build it first with docker build)."
  type        = string
  default     = "hello-devops:1.0.0"
}

variable "app_version" {
  description = "Shown by the app at /."
  type        = string
  default     = "1.0.0"
}

variable "host_port" {
  description = "Port on your laptop that forwards to the app."
  type        = number
  default     = 8080
}
