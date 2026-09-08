# ─── Random secrets (created only in the default workspace) ──────────────────

locals {
  is_default_ws = terraform.workspace == "default"
}

resource "random_password" "jwt_secret" {
  count   = local.is_default_ws ? 1 : 0
  length  = 64
  special = false
}

resource "random_password" "origin_token" {
  count   = local.is_default_ws ? 1 : 0
  length  = 64
  special = false
}

# ─── SSM parameters (Standard tier — free) ────────────────────────────────────
# Owned by the default workspace; the dev workspace shares them via data sources.

resource "aws_ssm_parameter" "jwt_secret" {
  count = local.is_default_ws ? 1 : 0
  name  = "/boardsite/jwt-secret"
  type  = "SecureString"
  value = random_password.jwt_secret[0].result

  tags = {
    Project = var.project_name
  }
}

resource "aws_ssm_parameter" "origin_token" {
  count = local.is_default_ws ? 1 : 0
  name  = "/boardsite/origin-token"
  type  = "SecureString"
  value = random_password.origin_token[0].result

  tags = {
    Project = var.project_name
  }
}

resource "aws_ssm_parameter" "bgg_token" {
  count = local.is_default_ws ? 1 : 0
  name  = "/boardsite/bgg-token"
  type  = "SecureString"
  value = var.bgg_token

  lifecycle {
    ignore_changes = [value]
  }

  tags = {
    Project = var.project_name
  }
}

# ─── State moves: resource → resource[0] (keeps prod plan at zero changes) ───

moved {
  from = random_password.jwt_secret
  to   = random_password.jwt_secret[0]
}

moved {
  from = random_password.origin_token
  to   = random_password.origin_token[0]
}

moved {
  from = aws_ssm_parameter.jwt_secret
  to   = aws_ssm_parameter.jwt_secret[0]
}

moved {
  from = aws_ssm_parameter.origin_token
  to   = aws_ssm_parameter.origin_token[0]
}

moved {
  from = aws_ssm_parameter.bgg_token
  to   = aws_ssm_parameter.bgg_token[0]
}

# ─── Dev workspace reads the shared parameters ────────────────────────────────

data "aws_ssm_parameter" "jwt_secret" {
  count = local.is_default_ws ? 0 : 1
  name  = "/boardsite/jwt-secret"
}

data "aws_ssm_parameter" "origin_token" {
  count = local.is_default_ws ? 0 : 1
  name  = "/boardsite/origin-token"
}

data "aws_ssm_parameter" "bgg_token" {
  count = local.is_default_ws ? 0 : 1
  name  = "/boardsite/bgg-token"
}

# ─── Workspace-independent accessors ─────────────────────────────────────────

locals {
  origin_token_value = local.is_default_ws ? aws_ssm_parameter.origin_token[0].value : data.aws_ssm_parameter.origin_token[0].value
  ssm_param_arns = local.is_default_ws ? [
    aws_ssm_parameter.jwt_secret[0].arn,
    aws_ssm_parameter.origin_token[0].arn,
    aws_ssm_parameter.bgg_token[0].arn,
    ] : [
    data.aws_ssm_parameter.jwt_secret[0].arn,
    data.aws_ssm_parameter.origin_token[0].arn,
    data.aws_ssm_parameter.bgg_token[0].arn,
  ]
}
