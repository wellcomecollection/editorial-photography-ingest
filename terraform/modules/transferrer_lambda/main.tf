locals {
  lambda_name = "editorial-photography-transfer-${var.environment}"
  buckets = tomap(
    {
      staging = "wellcomecollection-archivematica-staging-transfer-source",
      production = "wellcomecollection-archivematica-transfer-source"
    }
  )
  target_bucket = lookup(local.buckets, var.environment)

}


module "transfer_lambda" {
  source = "git@github.com:wellcomecollection/terraform-aws-lambda?ref=v1.2.0"
  name    = local.lambda_name
  runtime = "python3.12"
  handler = "lambda_function.lambda_handler"
  filename    = var.lambda_zip.output_path
  memory_size = 2048
  timeout     = var.lambda_timeout

  environment = {
    variables = {
      ACCESSION_NUMBER = "2754"
      TARGET_BUCKET = local.target_bucket
    }
  }
  source_code_hash = var.lambda_zip.output_base64sha256
  ephemeral_storage  = {
    size = var.lambda_storage
  }
}

resource "aws_iam_role_policy" "write_to_archivematica_transfer_source" {
  role = module.transfer_lambda.lambda_role.name
  name = "write_to_archivematica_transfer_source-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${local.target_bucket}/*"
        },
    ]
  }
  )
}

resource "aws_iam_role_policy" "read_from_editorial_photography" {
  role = module.transfer_lambda.lambda_role.name
  name = "read_from_editorial_photography-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect" =  "Allow",
            "Action" =  [
              "s3:GetObject",
              "s3:ListBucket"
            ],
            "Resource" = [
              "arn:aws:s3:::wellcomecollection-editorial-photography",
              "arn:aws:s3:::wellcomecollection-editorial-photography/*"
            ],
        },
    ]
  })

}