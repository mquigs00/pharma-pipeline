terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "s3" {
  source = "./modules/s3"
  project = var.project
  environment = var.environment
}

module "lambda" {
  source = "./modules/lambda"
  project = var.project
  environment = var.environment
  data_lake_bucket_arn = module.s3.data_lake_bucket_arn
  data_lake_bucket_name = module.s3.date_lake_bucket_name
}