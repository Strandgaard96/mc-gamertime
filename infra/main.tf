terraform {
  required_version = ">= 1.5"
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
  # backend "s3" {}  # commented out — user adds when ready
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
}
