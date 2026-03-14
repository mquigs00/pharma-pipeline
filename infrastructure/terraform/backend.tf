terraform {
  backend "s3" {
    bucket = "pharma-pipeline-tf-state"
    key = "pharma-pipeline/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}