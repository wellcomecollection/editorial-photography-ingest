
data "aws_iam_policy_document" "allow_sqs_pull" {
    statement {
      actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      var.queue_arn
    ]
  }
}

resource "aws_iam_role_policy" "allow_sqs_pull" {
  name   = "${var.trigger_name}-pull-from-queue"
  role   = var.role_name
  policy = data.aws_iam_policy_document.allow_sqs_pull.json
}

resource "aws_lambda_event_source_mapping" "lambda_trigger" {
  event_source_arn = var.queue_arn
  enabled          = true
  function_name    = var.function_name
  batch_size       = var.batch_size
}

resource "aws_lambda_permission" "allow_lambda_sqs_trigger" {
  action        = "lambda:InvokeFunction"
  function_name    = var.function_name
  principal     = "sqs.amazonaws.com"
  source_arn = var.queue_arn
}