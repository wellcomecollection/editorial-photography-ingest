locals {
  objects = chomp(file("../src/delete_shoots/prefixes.txt"))
  resources = formatlist("arn:aws:s3:::wellcomecollection-editorial-photography/%s/*", split("\n", local.objects))
}

resource "aws_iam_role" "delete_photoshoots_role" {
  name               = "delete_photoshoots"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::760097843905:role/platform-read_only"]
    }
  }
}

resource "aws_iam_policy" "delete_photoshoots_policy" {
  name        = "delete_photoshoots_policy"
  description = "Permissions to delete objects with specific prefixes"
  
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:ListBucket",
          "s3:GetObject*"
        ]
        Resource = [
          "arn:aws:s3:::wellcomecollection-editorial-photography",
          "arn:aws:s3:::wellcomecollection-editorial-photography/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = "s3:DeleteObject"
        Resource = local.resources  
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "developer_role_policy" {
  role       = aws_iam_role.delete_photoshoots_role.name
  policy_arn = aws_iam_policy.delete_photoshoots_policy.arn
}
