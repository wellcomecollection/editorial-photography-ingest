
provider "aws" {
  region = "eu-west-1"
  alias  = "digitisation"
  allowed_account_ids = ["404315009621"]
  assume_role {
    role_arn = "arn:aws:iam::404315009621:role/digitisation-admin"
  }
}

provider "aws" {
  region = "eu-west-1"
  alias  = "platform"
  allowed_account_ids = ["760097843905"]

  assume_role {
    role_arn = "arn:aws:iam::760097843905:role/platform-admin"
  }
}