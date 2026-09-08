# ─── ACM certificate (must be in us-east-1 for CloudFront) ───────────────────

resource "aws_acm_certificate" "web" {
  provider          = aws.us_east_1
  domain_name       = local.fqdn
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Project = var.project_name
  }
}

# ─── Local: DNS validation records for manual entry in Cloudflare ─────────────

locals {
  acm_certificate_validation_records = {
    for dvo in aws_acm_certificate.web.domain_validation_options : dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }
}

# ─── Wait for certificate validation ─────────────────────────────────────────
# After running `terraform apply`, add the CNAME records output by
# `acm_validation_records` to Cloudflare, then re-run `terraform apply`
# (or target this resource) to complete validation.

resource "aws_acm_certificate_validation" "web" {
  provider        = aws.us_east_1
  certificate_arn = aws_acm_certificate.web.arn

  # No validation_record_fqdns — Terraform will poll ACM until the cert becomes
  # ISSUED. Manual DNS entry in Cloudflare triggers ACM to validate on its own.
}
