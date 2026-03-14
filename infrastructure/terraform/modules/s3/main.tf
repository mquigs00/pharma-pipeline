resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project}-data-lake-${var.environment}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "folders" {
  for_each = toset([
    "bronze/faers/",
    "silver/faers/",
    "gold/faers/",
    "bronze/omop/",
    "silver/omop/",
    "gold/omop/",
    "scripts/",
    "logs/"
  ])

  bucket = aws_s3_bucket.data_lake.id
  key = each.value
  content = ""
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}