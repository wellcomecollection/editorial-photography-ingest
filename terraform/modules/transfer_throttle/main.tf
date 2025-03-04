locals {
  lambda_name = "editorial-photography-transfer_throttle-${var.environment}"
  buckets = tomap(
    {
      staging = "wellcomecollection-archivematica-staging-transfer-source",
      production = "wellcomecollection-archivematica-transfer-source"
    }
  )
  target_bucket = lookup(local.buckets, var.environment)
  input_queue_visibility_timeout = 300
}

module "input_queue" {
  source = "../notification_queue"
  environment = var.environment
  queue_visibility_timeout = local.input_queue_visibility_timeout
  action_name = "queue_shoot_transfers"
  extra_topics = [var.upstream_topic_arn]
}

module "transfer_throttle_lambda" {
  source = "git@github.com:wellcomecollection/terraform-aws-lambda?ref=v1.2.0"
  name    = local.lambda_name
  runtime = "python3.12"
  handler = "transfer_throttle.lambda_main"
  filename    = var.lambda_zip.output_path
  timeout     = 300

  environment = {
    variables = {
      SOURCE_QUEUE = module.input_queue.queue_url
      ENVIRONMENT = var.environment
      TARGET_TOPIC = module.output_topic.arn
    }
  }
  source_code_hash = var.lambda_zip.output_base64sha256
}



module "transfer_scheduler" {
  source = "../lambda_scheduler"
  cron                 = "cron(30 7,9,11,13,15,16 ? * MON-FRI *)"
  description          = "Moves batches of shoots to the transferrer at a rate Archivematica can handle"
  lambda_arn           = module.transfer_throttle_lambda.lambda.arn
  lambda_function_name = module.transfer_throttle_lambda.lambda.function_name
  name                 = "transfer_throttle"
}


resource "aws_iam_role_policy" "pull_from_input_queue" {
  role = module.transfer_throttle_lambda.lambda_role.name
  name = "queue_shoot_transfers_receieve_message-${var.environment}"
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


module "output_topic" {
  source = "github.com/wellcomecollection/terraform-aws-sns-topic.git?ref=v1.0.1"
  name = "transfer_throttle_output-${var.environment}"
}

resource "aws_iam_role_policy" "notify_output_topic" {
  role = module.transfer_throttle_lambda.lambda_role.name
  name = "notify_throttled_transfer-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": "sns:Publish"
            "Resource": module.output_topic.arn
        },
    ]
  }
  )
}

















