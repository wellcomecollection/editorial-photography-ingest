
module "transfer_lambda" {
  source = "../transferrer_lambda"
  environment = var.environment
  lambda_zip = var.lambda_zip
  lambda_storage = var.lambda_storage
  lambda_timeout = var.lambda_timeout
}

module "input_queue" {
  source = "../notification_queue"
  environment = var.environment
  queue_visibility_timeout = var.queue_visibility_timeout
  action_name = "transfer-shoots"
}

module "trigger" {
  source = "../sqs_lambda_trigger"
  queue_arn = module.input_queue.queue_arn
  function_name = module.transfer_lambda.lambda.function_name
  role_name = module.transfer_lambda.role.name
  trigger_name = "editorial-photography-${var.environment}"
}