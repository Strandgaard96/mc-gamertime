terraform {
  required_version = ">= 1.11" # backend.tf uses use_lockfile
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

locals {
  # "" in the default (prod) workspace so all existing resource names are unchanged
  env_suffix  = terraform.workspace == "default" ? "" : "-${terraform.workspace}"
  fqdn        = terraform.workspace == "default" ? "${var.subdomain}.${var.domain}" : "games-dev.${var.domain}"
  name_prefix = "${var.resource_prefix}${local.env_suffix}"

  # Uploaded-media key prefixes in the web bucket. Each is routed by CloudFront
  # to the API (served behind require_auth), writable by the Lambda, and denied
  # to CloudFront's direct S3 read. Must equal MEDIA_PREFIXES in
  # api/routes/storage.py — api/tests/test_media_prefixes_sync.py checks it.
  media_prefixes = ["avatars", "blog-images", "game-images", "session-images"]

  # CloudFront path patterns for those prefixes. The free pricing plan allows 5
  # cache behaviours in total (default + /api/* + these), so every "*-images"
  # prefix shares one wildcard behaviour instead of getting its own. Name a new
  # media prefix "<something>-images" and it costs nothing here;
  # test_media_prefixes_sync.py enforces the budget.
  media_path_patterns = distinct([
    for p in local.media_prefixes : endswith(p, "-images") ? "/*-images/*" : "/${p}/*"
  ])
}
