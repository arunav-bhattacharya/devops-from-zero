# Lets GitHub Actions log in to AWS with short-lived tokens (OIDC).
# No AWS keys are stored in GitHub. An account can have only one of these.
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

locals {
  # GitHub puts the repo in the token's "sub" claim in one of two forms.
  # Repos created after July 15, 2026 use the second one, with numeric IDs.
  sub_by_name = "repo:${var.github_owner}/${var.github_repo}"
  sub_by_id   = "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repo}@${var.github_repo_id}"
}

# Who may use the role: only your repo, and only for pull requests
# (plan) or jobs that run in the "production" environment (apply).
data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "${local.sub_by_name}:pull_request",
        "${local.sub_by_id}:pull_request",
        "${local.sub_by_name}:environment:production",
        "${local.sub_by_id}:environment:production",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.project}-github-actions"
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

# What the role may do: manage this project's S3 buckets (including the
# state bucket), and read its own IAM setup so `terraform plan` works.
# Changes to IAM itself are applied from your laptop, never from CI.
# trivy:ignore:AWS-0345 s3:* is limited to this project's buckets.
data "aws_iam_policy_document" "permissions" {
  statement {
    sid     = "ProjectBuckets"
    actions = ["s3:*"]
    resources = [
      "arn:aws:s3:::${var.project}-*",
      "arn:aws:s3:::${var.project}-*/*",
    ]
  }
  statement {
    sid     = "ReadOwnIam"
    actions = ["iam:Get*", "iam:List*"]
    resources = [
      aws_iam_openid_connect_provider.github.arn,
      aws_iam_role.github_actions.arn,
    ]
  }
}

resource "aws_iam_role_policy" "github_actions" {
  name   = "terraform"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.permissions.json
}
