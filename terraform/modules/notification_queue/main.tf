
module "transfer_shoots_topic" {
  source = "github.com/wellcomecollection/terraform-aws-sns-topic.git?ref=v1.0.1"
  name = "transfer-shoots-${var.environment}"
}

module "dlq_alarm_topic" {
  source = "github.com/wellcomecollection/terraform-aws-sns-topic.git?ref=v1.0.1"
  name = "transfer-shoots-alarm-${var.environment}"
}

module "input_queue" {
  source = "github.com/wellcomecollection/terraform-aws-sqs//queue?ref=v1.2.1"

  queue_name = "transfer-shoots-${var.environment}"

  topic_arns                 = [module.transfer_shoots_topic.arn]
  visibility_timeout_seconds = var.queue_visibility_timeout
  max_receive_count          = 1
  message_retention_seconds = 1200
  alarm_topic_arn           = module.dlq_alarm_topic.arn
}
