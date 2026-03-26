data "archive_file" "faers_ingestor" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../ingestion/faers_ingestor"
  output_path = "${path.module}/../../../../ingestion/faers_ingestor/faers_ingestor.zip"
}

resource "aws_iam_role" "faers_ingestor" {
  name = "${var.project}-faers_ingestor-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "faers_ingestor_s3" {
  name = "${var.project}-faers_ingestor_s3_${var.environment}"
  role = aws_iam_role.faers_ingestor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${var.data_lake_bucket_arn}/bronze/faers/*"
      },
      {
        Effect = "Allow"
        Action = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.faers_api_key.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "faers_ingestor_logs" {
  role = aws_iam_role.faers_ingestor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "faers_ingestor" {
  function_name = "${var.project}-faers-ingestor${var.environment}"
  role = aws_iam_role.faers_ingestor.arn
  handler = "handler.lambda_handler"
  runtime = "python3.11"
  timeout = 300
  memory_size = 512
  filename = data.archive_file.faers_ingestor.output_path
  source_code_hash = data.archive_file.faers_ingestor.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = var.data_lake_bucket_name
      ENVIRONMENT = var.environment
    }
  }
}