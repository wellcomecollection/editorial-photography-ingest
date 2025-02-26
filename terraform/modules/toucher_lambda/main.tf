locals {
  lambda_name = "editorial-photography-toucher-${var.environment}"
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
  action_name = "touch_shoots"
}

module "toucher_lambda" {
  source = "git@github.com:wellcomecollection/terraform-aws-lambda?ref=v1.2.0"
  name    = local.lambda_name
  runtime = "python3.12"
  handler = "touch.lambda_main"
  filename    = var.lambda_zip.output_path
  timeout     = 600
  memory_size = 1024

  environment = {
    variables = {
      MESSAGES_PER_BATCH = "10"
      TARGET_BUCKET = local.target_bucket
      SOURCE_QUEUE = module.input_queue.queue_url
    }
  }
  source_code_hash = var.lambda_zip.output_base64sha256
}

resource "aws_iam_role_policy" "touch_archivematica_transfer_source" {
  # Touching is achieved by copying an object onto itself, with new metadata.
  role = module.toucher_lambda.lambda_role.name
  name = "touch_archivematica_transfer_source-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Effect": "Allow",
            "Action": ["s3:CopyObject", "s3:GetObject", "s3:PutObject", "s3:GetObjectTagging", "s3:PutObjectTagging"]
            "Resource": ["arn:aws:s3:::${local.target_bucket}", "arn:aws:s3:::${local.target_bucket}/*"]
        },
    ]
  }
  )
}

resource "aws_iam_role_policy" "pull_from_touch_queue" {
  role = module.toucher_lambda.lambda_role.name
  name = "touch_queue_receieve_message-${var.environment}"
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


resource "aws_cloudwatch_event_rule" "schedule_rule" {
  # On weekdays, Archivematica switches on in the morning and is ready by 0730 (UTC)
  # and switches off at 1900.

  # The shoots need to be fed to Archivematica slowly.
  # If you give it too much to do all at once, it will give it a try
  # and end up hurting itself.

  # Archivematica seems reasonably comfortable to consume
  # up to twenty shoots, three times a day, four if you are lucky.

  # The Toucher pushes up to ten shoots to Archivematica at once
  # (the maximum that can be pulled from SQS in one request)
  # So it gets triggered six times a day in order to hit a total of up to 60 shoots.
  # If this works without problems, we might consider increasing the number of times it gets triggered.

  # The first trigger is 07:30, in order to start as soon as possible in the day.
  # The last trigger is at 16:30.  This is slightly more front-loaded than a purely even spread across the
  # period available.  This should give it time to catch up before switch-off if there are any delays.

  name                = "toucher_schedule"
  description         = "Trigger the toucher Lambda at 07:30, then five further times across the working day"
  schedule_expression = "cron(30 7,9,11,13,15,16 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.schedule_rule.name
  target_id = "toucher_lambda_target"
  arn       = module.toucher_lambda.lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.toucher_lambda.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule_rule.arn
}













