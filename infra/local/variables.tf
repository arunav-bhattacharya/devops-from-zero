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

variable "dev_port" {
  description = "Port on your laptop for the dev stack."
  type        = number
  default     = 8080
}

variable "test_port" {
  description = "Port on your laptop for the test stack."
  type        = number
  default     = 8082
}
