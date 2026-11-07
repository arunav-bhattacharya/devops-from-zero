terraform {
  required_version = ">= 1.10"
  required_providers {
    # A child module names its providers but never configures them.
    # The root module's provider "docker" {} block is passed down.
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 4.6, < 5.0"
    }
  }
}
