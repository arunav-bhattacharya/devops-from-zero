output "bucket_name" {
  description = "Put this name in the backend block in versions.tf."
  value       = aws_s3_bucket.state.bucket
}

output "github_actions_role_arn" {
  description = "Save as the repository variable AWS_ROLE_ARN in GitHub."
  value       = aws_iam_role.github_actions.arn
}
