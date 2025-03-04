resource "aws_iam_role" "delete_photoshoots_role" {
  name               = "delete_photoshoots"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}
data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::760097843905:role/platform-developer"]
    }
  }
}
