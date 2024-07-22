
provider "aws" {
  region = "eu-west-1"

  assume_role {
    role_arn = "arn:aws:iam::404315009621:role/digitisation-developer"
  }
}
