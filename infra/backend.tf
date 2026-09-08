# Remote state in S3, with Terraform's native S3 lock file (no DynamoDB table).
#
# The bucket is NOT managed by this configuration — Terraform cannot store its
# own state in a bucket it is about to create. `task state:bootstrap` creates
# it once (versioned, encrypted, public access blocked) from the values below.
#
# Deploying your own copy: S3 bucket names are global, so either edit `bucket`
# here or override it without touching source by creating infra/backend.hcl
# (gitignored; see backend.hcl.example) — `task init` passes it as
# -backend-config, and command-line values win over this block.
#
# Workspaces: the `dev` workspace is stored under `env:/dev/` in the same bucket.
terraform {
  backend "s3" {
    bucket       = "games-boardgame-night-tfstate"
    region       = "eu-west-1"
    key          = "terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
