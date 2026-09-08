# ─── DynamoDB tables ──────────────────────────────────────────────────────────

locals {
  dynamo_tables = {
    users         = var.users_table_name
    games         = var.games_table_name
    results       = var.results_table_name
    posts         = var.posts_table_name
    recs          = var.recs_table_name
    reactions     = var.reactions_table_name
    notifications = var.notifications_table_name
    settings      = var.settings_table_name
  }
}

resource "aws_dynamodb_table" "tables" {
  for_each     = local.dynamo_tables
  name         = "${each.value}${local.env_suffix}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  # Enable streams only if the map key is "results"
  stream_enabled = each.key == "results" ? true : false
  # stream_view_type is required if stream_enabled is true
  stream_view_type = each.key == "results" ? "NEW_IMAGE" : null

  deletion_protection_enabled = true

  tags = {
    Project = var.project_name
  }
}
