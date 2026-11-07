# tflint settings for this folder. Run: tflint --init && tflint
# The terraform plugin ships with tflint; "recommended" is its default rule set.
plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

# Rules that know AWS, such as which instance types exist.
plugin "aws" {
  enabled = true
  version = "0.50.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}
