resource "aws_secretsmanager_secret" "faers_api_key" {
  name = "${var.project}/faers-api-key"
  description = "openFDA API key for FAERS ingestion"
}

output "faers_api_key_arn" {
  value = aws_secretsmanager_secret.faers_api_key.arn
}