output "lambda" {
  value = module.restore_lambda.lambda
}

output "role" {
  value = module.restore_lambda.lambda_role
}

output "completion_topic_arn" {
  value = module.completion_topic.arn
}
