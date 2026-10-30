terraform {
  required_version = ">= 1.11"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Step 2 (after the first apply): uncomment this block, put in your bucket
  # name from `terraform output bucket_name`, then run:
  #   terraform init -migrate-state
  backend "s3" {
    bucket       = "hello-devops-tfstate-123456789012"
    key          = "infra/aws/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    dynamodb_table = "locks"
  }
}

provider "aws" {
  region = var.region

  # Every resource this provider creates gets these tags.
  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
      Repo      = "${var.github_owner}/${var.github_repo}"
    }
  }
}
