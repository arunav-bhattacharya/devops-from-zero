variable "region" {
  description = "AWS Region for everything in this folder."
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Short name used in resource names and tags."
  type        = string
  default     = "hello-devops"
}

variable "github_owner" {
  description = "Your GitHub user name, for example octocat."
  type        = string
}

variable "github_repo" {
  description = "Your repository name."
  type        = string
  default     = "hello-devops"
}

variable "github_owner_id" {
  description = "Numeric ID of your GitHub user: gh api users/YOUR_USER --jq .id"
  type        = string
}

variable "github_repo_id" {
  description = "Numeric ID of your repo: gh api repos/YOUR_USER/hello-devops --jq .id"
  type        = string
}
