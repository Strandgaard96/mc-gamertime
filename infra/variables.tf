variable "aws_region" {
  description = "AWS region for primary resources (Lambda, DynamoDB, S3)"
  type        = string
  default     = "eu-west-1"
}

variable "domain" {
  description = "Root domain name (e.g. example.com) that you own. DNS records are added by hand, so any provider works. No default: set it in terraform.tfvars so a fork can't deploy against someone else's domain."
  type        = string
}

variable "extra_cors_origins" {
  description = "Additional credentialed CORS origins beyond the deployed FQDN (e.g. a legacy domain still pointed at this app). Set in terraform.tfvars."
  type        = list(string)
  default     = []
}

variable "cloudfront_web_acl_arn" {
  description = "ARN of the CloudFront-managed WAF ACL to associate with the prod distribution. Contains the AWS account id, so it lives in terraform.tfvars (gitignored), not in source. Empty = no WAF association."
  type        = string
  default     = ""
}

variable "subdomain" {
  description = "Subdomain for the application (e.g. mcgamertime → mcgamertime.example.com)"
  type        = string
  default     = "mcgamertime"
}

variable "project_name" {
  description = "Short name used as a suffix in all resource names"
  type        = string
  default     = "boardgame-night"
}

variable "resource_prefix" {
  description = "Prefix for every AWS resource name (Lambda, S3, API Gateway, log groups). Pick it once at first deploy and leave it alone: changing it renames every resource, which Terraform performs as destroy-and-recreate. It is deliberately independent of domain/subdomain so renaming the site does not rebuild the infrastructure."
  type        = string
  default     = "games-boardgame-night"
}

variable "users_table_name" {
  description = "DynamoDB table for users"
  type        = string
  default     = "boardsite-users"
}

variable "games_table_name" {
  description = "DynamoDB table for games"
  type        = string
  default     = "boardsite-games"
}

variable "results_table_name" {
  description = "DynamoDB table for game results"
  type        = string
  default     = "boardsite-results"
}

variable "posts_table_name" {
  description = "DynamoDB table for blog posts"
  type        = string
  default     = "boardsite-posts"
}

variable "recs_table_name" {
  description = "DynamoDB table for curated recommendations"
  type        = string
  default     = "boardsite-recs"
}

variable "reactions_table_name" {
  description = "DynamoDB table for session reactions and comments"
  type        = string
  default     = "boardsite-reactions"
}

variable "notifications_table_name" {
  description = "DynamoDB table for achievement notifications"
  type        = string
  default     = "boardsite-notifications"
}

variable "settings_table_name" {
  description = "DynamoDB table for instance-level settings"
  type        = string
  default     = "boardsite-settings"
}

variable "lambda_zip_path" {
  description = "Path to the Lambda deployment zip archive"
  type        = string
  default     = "../api/lambda.zip"
}

variable "bgg_token" {
  description = "BoardGameGeek API bearer token (only needed on first apply — value ignored after creation)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "alert_email" {
  description = "Email address for CloudWatch alarm notifications (empty = no email subscription; confirm the SNS subscription via the link AWS emails once)"
  type        = string
  default     = ""
}
