# Who am I? Gives us the 12-digit account ID for a unique bucket name.
data "aws_caller_identity" "current" {}

# A private bucket. Later it also holds this folder's Terraform state.
# trivy:ignore:AWS-0089 Access logs need a second bucket. Not worth it for a lab.
resource "aws_s3_bucket" "state" {
  bucket = "${var.project}-tfstate-${data.aws_caller_identity.current.account_id}"

  # Lab only: lets `terraform destroy` delete the bucket even if it holds
  # files. For a real state bucket, remove this and add prevent_destroy.
  force_destroy = true
}

# Keep every old version of every file, so a bad state write can be undone.
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Nobody on the internet can read this bucket, even by mistake.
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Encrypt files at rest with keys that S3 manages (free).
# trivy:ignore:AWS-0132 A customer managed KMS key costs money each month.
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
