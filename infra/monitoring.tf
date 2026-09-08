# ─── Logging & monitoring ─────────────────────────────────────────────────────
# Addresses logging-audit findings L-2 (retention), L-4 (API GW access logs),
# L-5 (alarms). Applies to both workspaces (prod=default, dev) via name_prefix.
#
# NOTE: Lambda auto-creates /aws/lambda/<fn> on first invoke. If this log group
# already exists in an account, import it once before the first apply:
#   terraform import aws_cloudwatch_log_group.api /aws/lambda/${local.name_prefix}-api

# L-2 — Lambda log group with a finite retention (was: never expire)
resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${local.name_prefix}-api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "stream" {
  name              = "/aws/lambda/${local.name_prefix}-stream"
  retention_in_days = 30
}

# L-4 — API Gateway access-log destination (wired into the stage in lambda.tf)
resource "aws_cloudwatch_log_group" "apigw" {
  name              = "/aws/apigw/${local.name_prefix}"
  retention_in_days = 30
}

# L-5 — Alerting: SNS topic + CloudWatch alarms on error/throttle/latency
resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  dimensions          = { FunctionName = aws_lambda_function.api.function_name }
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 5
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_description   = "Lambda API errors — likely a cold-start ImportModuleError taking down every route (see CLAUDE.md Debugging Prod)"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${local.name_prefix}-lambda-throttles"
  namespace           = "AWS/Lambda"
  metric_name         = "Throttles"
  dimensions          = { FunctionName = aws_lambda_function.api.function_name }
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_description   = "Lambda API is being throttled (concurrency limit)"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "apigw_5xx" {
  alarm_name          = "${local.name_prefix}-apigw-5xx"
  namespace           = "AWS/ApiGateway"
  metric_name         = "5xx"
  dimensions          = { ApiId = aws_apigatewayv2_api.api.id }
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 5
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_description   = "API Gateway 5xx spike"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
