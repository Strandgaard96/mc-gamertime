# ─── IAM role for Lambda ──────────────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.name_prefix}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ─── IAM policy: DynamoDB access ─────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_dynamodb" {
  statement {
    sid    = "DynamoDBAccess"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
    ]

    resources = [for t in aws_dynamodb_table.tables : t.arn]
  }
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name   = "${local.name_prefix}-dynamodb"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_dynamodb.json
}

# ─── IAM policy: SSM access ───────────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_ssm" {
  statement {
    sid       = "SSMAccess"
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = local.ssm_param_arns
  }
}

resource "aws_iam_role_policy" "lambda_ssm" {
  name   = "${local.name_prefix}-ssm"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_ssm.json
}

# ─── IAM policy: S3 access ────────────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_s3" {
  statement {
    sid    = "S3AvatarsAndBlog"
    effect = "Allow"
    # GetObject is required because the API now serves uploaded media itself
    # (routes/storage.py media_router) rather than CloudFront reading it from
    # S3 — that path was public to anyone holding the URL.
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = [
      "${aws_s3_bucket.web.arn}/blog-images/*",
      "${aws_s3_bucket.web.arn}/avatars/*",
      "${aws_s3_bucket.web.arn}/game-images/*"
    ]
  }
}

resource "aws_iam_role_policy" "lambda_s3" {
  name   = "${local.name_prefix}-s3"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_s3.json
}

# ─── Lambda function ──────────────────────────────────────────────────────────

resource "aws_lambda_function" "api" {
  function_name = "${local.name_prefix}-api"
  role          = aws_iam_role.lambda.arn

  runtime  = "python3.12"
  handler  = "main.handler"
  filename = var.lambda_zip_path

  # Safely handle the case where the zip doesn't exist yet during first plan.
  source_code_hash = try(filebase64sha256(var.lambda_zip_path), null)

  memory_size = 256
  timeout     = 30

  # Ensure Terraform owns the log group (with retention) before the function can
  # lazily create it with default never-expire retention.
  depends_on = [aws_cloudwatch_log_group.api]

  environment {
    variables = {
      # The app defaults to self-hosted (SQLite, local files, env secrets, no
      # origin guard). AWS is the opt-in path, so it names every cloud backend
      # explicitly rather than relying on a default.
      DB_BACKEND                 = "dynamodb"
      STORAGE_BACKEND            = "s3"
      SECRETS_PROVIDER           = "ssm"
      ORIGIN_GUARD_ENABLED       = "true"
      PUBLIC_RECOMMENDED_ENABLED = "true"

      USERS_TABLE         = "${var.users_table_name}${local.env_suffix}"
      GAMES_TABLE         = "${var.games_table_name}${local.env_suffix}"
      RESULTS_TABLE       = "${var.results_table_name}${local.env_suffix}"
      POSTS_TABLE         = "${var.posts_table_name}${local.env_suffix}"
      RECS_TABLE          = "${var.recs_table_name}${local.env_suffix}"
      REACTIONS_TABLE     = "${var.reactions_table_name}${local.env_suffix}"
      NOTIFICATIONS_TABLE = "${var.notifications_table_name}${local.env_suffix}"
      SETTINGS_TABLE      = "${var.settings_table_name}${local.env_suffix}"
      S3_BUCKET           = aws_s3_bucket.web.bucket
      # No CLOUDFRONT_URL: media URLs are relative now, so the browser sends the
      # session cookie with them. An absolute CDN URL would be cross-site.
      # Credentialed CORS peers. Derived from the deployed FQDN so no domain is
      # hardcoded in application source.
      #
      # The distribution's own *.cloudfront.net domain is included because the
      # app really is served from it: origin_guard's CSRF check rejects unsafe
      # methods whose Origin isn't listed here, and CloudFront's custom error
      # page turns that 403 into index.html with status 200 — so a browser on
      # the raw distribution domain sees "invalid username or password" on a
      # correct login instead of an error. That is the normal way to reach the
      # dev stack, since games-dev.<domain> redirects to it.
      CORS_ALLOWED_ORIGINS = join(",", concat([
        "https://${local.fqdn}",
        "https://${aws_cloudfront_distribution.web.domain_name}",
      ], var.extra_cors_origins))
    }
  }

  tags = {
    Project = var.project_name
  }
}

# ─── API Gateway HTTP API → Lambda ───────────────────────────────────────────

resource "aws_apigatewayv2_api" "api" {
  name          = "${local.name_prefix}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw.arn
    format = jsonencode({
      requestId = "$context.requestId"
      ip        = "$context.identity.sourceIp"
      method    = "$context.httpMethod"
      route     = "$context.routeKey"
      status    = "$context.status"
      latency   = "$context.responseLatency"
    })
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

# ─── Stream Lambda ────────────────────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_streams" {
  statement {
    sid    = "DynamoDBStreamRead"
    effect = "Allow"

    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]

    resources = [aws_dynamodb_table.tables["results"].stream_arn]
  }
}

resource "aws_iam_role_policy" "lambda_streams" {
  name   = "${local.name_prefix}-streams"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_streams.json
}

resource "aws_lambda_function" "stream" {
  function_name = "${local.name_prefix}-stream"
  role          = aws_iam_role.lambda.arn

  runtime  = "python3.12"
  handler  = "handlers.stream_processor.process_stream_handler"
  filename = var.lambda_zip_path

  source_code_hash = try(filebase64sha256(var.lambda_zip_path), null)

  memory_size = 128
  timeout     = 60

  depends_on = [aws_cloudwatch_log_group.stream]

  environment {
    variables = {
      GAMES_TABLE = "${var.games_table_name}${local.env_suffix}"
    }
  }

  tags = {
    Project = var.project_name
  }
}

resource "aws_lambda_event_source_mapping" "stream" {
  event_source_arn  = aws_dynamodb_table.tables["results"].stream_arn
  function_name     = aws_lambda_function.stream.arn
  starting_position = "LATEST"
}
