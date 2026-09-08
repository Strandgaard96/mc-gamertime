# ─── S3 bucket ───────────────────────────────────────────────────────────────

resource "aws_s3_bucket" "web" {
  bucket = "${local.name_prefix}-web"

  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_cors_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT"]
    allowed_origins = [
      "https://${local.fqdn}",
    ]
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_public_access_block" "web" {
  bucket = aws_s3_bucket.web.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ─── CloudFront Origin Access Control ────────────────────────────────────────

resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "${local.name_prefix}-oac"
  description                       = "OAC for ${local.name_prefix} S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ─── Bucket policy — allow CloudFront OAC ────────────────────────────────────

data "aws_iam_policy_document" "s3_cloudfront" {
  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web.arn}/*"]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.web.arn]
    }
  }

  # This bucket is both the website origin and the destination that
  # scripts/export-tables.py writes DynamoDB dumps to (its own usage line names
  # this bucket). CloudFront's default cache behaviour serves the entire bucket
  # at the site root, so an upload to exports/ would publish the users table —
  # emails and bcrypt hashes — to anyone who guesses the date in the key.
  #
  # An explicit Deny beats remembering not to run the command: even if a dump
  # lands here, CloudFront cannot read it. Deny always wins over Allow in IAM.
  statement {
    sid    = "DenyCloudFrontAccessToPrivateObjects"
    effect = "Deny"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]
    resources = [
      # Table dumps from scripts/export-tables.py — never web-servable.
      "${aws_s3_bucket.web.arn}/exports/*",
      # Uploaded media is served by the API behind require_auth. CloudFront
      # routes these prefixes to Lambda, so it has no reason to read them from
      # S3; denying it means a future behaviour change cannot silently make
      # them public again.
      "${aws_s3_bucket.web.arn}/avatars/*",
      "${aws_s3_bucket.web.arn}/blog-images/*",
      "${aws_s3_bucket.web.arn}/game-images/*"
    ]
  }
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id
  policy = data.aws_iam_policy_document.s3_cloudfront.json

  # The bucket policy references the distribution ARN, so the distribution
  # must exist first.
  depends_on = [aws_cloudfront_distribution.web]
}

# ─── S3 versioning (preserves blog image history) ────────────────────────────

resource "aws_s3_bucket_versioning" "web" {
  bucket = aws_s3_bucket.web.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ─── Expire old image versions after 90 days ─────────────────────────────────

resource "aws_s3_bucket_lifecycle_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  rule {
    id     = "expire-noncurrent-blog-images"
    status = "Enabled"

    filter {
      prefix = "blog-images/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }

  rule {
    id     = "expire-noncurrent-web-assets"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  depends_on = [aws_s3_bucket_versioning.web]
}
