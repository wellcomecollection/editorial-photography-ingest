terraform {
  backend "s3" {
    assume_role = {
      role_arn = "arn:aws:iam::760097843905:role/platform-developer"
    }

    bucket         = "wellcomecollection-platform-infra"
    key            = "terraform/editorial-photography-ingest/terraform.tfstate"
    dynamodb_table = "terraform-locktable"
    region         = "eu-west-1"
  }
}
