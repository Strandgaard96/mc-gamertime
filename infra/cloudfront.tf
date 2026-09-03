# ─── CloudFront distribution ──────────────────────────────────────────────────

locals {
  s3_origin_id     = "s3-web"
  lambda_origin_id = "lambda-api"
}

resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  default_root_object = "index.html"
  price_class         = "PriceClass_All"
  aliases             = [local.fqdn]
  # Prod keeps its existing CloudFront-managed ACL (auto-created, free-tier;
  # state must not manage/import this ACL). CF-managed ACLs are per-distribution
  # and can't be shared, so dev runs with no WAF (web_acl_id = "").
  # The ARN embeds the AWS account id — set it in terraform.tfvars, never here.
  web_acl_id = local.is_default_ws ? var.cloudfront_web_acl_arn : ""

  # ── Origin 1: S3 (static assets) ──────────────────────────────────────────

  origin {
    origin_id                = local.s3_origin_id
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  # ── Origin 2: Lambda Function URL ─────────────────────────────────────────

  origin {
    origin_id   = local.lambda_origin_id
    domain_name = replace(aws_apigatewayv2_api.api.api_endpoint, "https://", "")

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = "X-Origin-Token"
      value = local.origin_token_value
    }
  }

  # ── Default behaviour → S3 ────────────────────────────────────────────────

  default_cache_behavior {
    target_origin_id       = local.s3_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    # AWS managed CachingOptimized policy
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }

  # ── Ordered behaviour → Lambda (/api/*) ───────────────────────────────────

  ordered_cache_behavior {
    path_pattern           = "/api/*"
    target_origin_id       = local.lambda_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    # AWS managed CachingDisabled policy
    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"

    # AWS managed AllViewerExceptHostHeader — forwards all viewer headers except Host.
    # OAC adds Authorization (SigV4) after this policy; viewer auth is via cookies.
    origin_request_policy_id = "b689b0a8-53d0-40ab-baf2-68738e2966ac"
  }

  # ── Uploaded media → Lambda ───────────────────────────────────────────────
  #
  # Avatars and uploaded images used to come straight from S3 through the
  # default behaviour, which made every one of them world-readable to anyone
  # holding the URL — and avatar keys are just the username. Routing these
  # prefixes to the API instead means routes/storage.py's media_router serves
  # them behind require_auth, matching how the self-hosted stack has always
  # worked. Caching is disabled: the response depends on the caller's session,
  # so a shared CloudFront cache entry would be served to the wrong viewer.

  dynamic "ordered_cache_behavior" {
    for_each = toset(["/avatars/*", "/blog-images/*", "/game-images/*"])

    content {
      path_pattern           = ordered_cache_behavior.value
      target_origin_id       = local.lambda_origin_id
      viewer_protocol_policy = "redirect-to-https"
      allowed_methods        = ["GET", "HEAD", "OPTIONS"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true

      # AWS managed CachingDisabled
      cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
      # AWS managed AllViewerExceptHostHeader — forwards the session cookie
      origin_request_policy_id = "b689b0a8-53d0-40ab-baf2-68738e2966ac"
    }
  }

  # ── SPA routing: return index.html for 403/404 from S3 ────────────────────

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  # ── TLS certificate ───────────────────────────────────────────────────────

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.web.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Project = var.project_name
  }
}
