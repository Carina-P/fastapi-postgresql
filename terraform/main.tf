terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region  = "eu-north-1"
  profile = "terraform-learning"
}

resource "aws_ecr_repository" "my_app" {
  name                 = "terraform-learning"
  image_tag_mutability = "IMMUTABLE"
}