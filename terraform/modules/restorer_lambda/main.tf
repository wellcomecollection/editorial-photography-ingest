locals {
  lambda_name = "editorial-photography-transfer-restorer"
  lambda_timeout = 600
  input_queue_visibility_timeout = 1200
  environment = "production"
  digitisation_account = "404315009621"
}


module "input_queue" {
  source = "../notification_queue"
  environment = local.environment
  queue_visibility_timeout = local.input_queue_visibility_timeout
  action_name = "restore_shoots"
}


module "restore_lambda" {
  source = "git@github.com:wellcomecollection/terraform-aws-lambda?ref=v1.2.0"

  name    = local.lambda_name
  runtime = "python3.12"
  handler = "restore_lambda.lambda_main"

  filename    = var.lambda_zip.output_path
  timeout     = local.lambda_timeout
  package_type = "Zip"

  source_code_hash = var.lambda_zip.output_base64sha256
  environment = {
    variables = {
      COMPLETED_TOPIC = module.completion_topic.arn
      SOURCE_QUEUE = module.input_queue.queue_url
    }
  }
}

resource "aws_iam_role_policy" "restore_shoot_from_glacier" {
  role = module.restore_lambda.lambda_role.name
  name = "restore_shoot_from_glacier"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": ["s3:ListBucket", "s3:RestoreObject"],
            "Resource": ["arn:aws:s3:::wellcomecollection-editorial-photography", "arn:aws:s3:::wellcomecollection-editorial-photography/*"]
        },
    ]
  }
  )
}


resource "aws_iam_role_policy" "pull_from_restore_queue" {
  role = module.restore_lambda.lambda_role.name
  name = "restore_queue_receieve_message"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": ["sqs:ReceiveMessage","sqs:DeleteMessage"]
            "Resource": module.input_queue.queue_arn
        },
    ]
  }
  )
}

module "restorer_scheduler" {
  source = "../lambda_scheduler"
  cron                 = "cron(0 20 ? * SUN-THU *)"
  description          = "Restore a batch of shoots in the evening so they are ready to be transferred in the morning"
  lambda_arn           = module.restore_lambda.lambda.arn
  lambda_function_name = module.restore_lambda.lambda.function_name
  name                 = "restorer"
}


module "completion_topic" {
  source = "github.com/wellcomecollection/terraform-aws-sns-topic.git?ref=v1.0.1"
  name = "shoot_restored-${local.environment}"
  cross_account_subscription_ids = [
    local.digitisation_account
  ]
}


resource "aws_iam_role_policy" "notify_restored_topic" {
  role = module.restore_lambda.lambda_role.name
  name = "notify-shoot_restored-${local.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": "sns:Publish"
            "Resource": module.completion_topic.arn
        },
    ]
  }
  )
}

