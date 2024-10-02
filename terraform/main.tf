locals {
  event_batching_window_timeout = 20
  lambda_timeout = 120 //two minutes

  # The lambda event source pulls messages from SQS in batches, finally triggering the lambda
  # when either it has enough messages, or enough time has elapsed.
  # A message becomes invisible when it joins the event source buffer, so could wait for
  # the whole timeout window plus the whole execution time before being confirmed.
  # The value of visibility timeout must be at least 20 seconds more than the lambda timeout
  # This doesn't necessarily need to exist with a longer batching window, but
  # always adding 20 here should mean that you can safely set batching window to 0
  # if you wish.
  # See: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
  # "Lambda might wait for up to 20 seconds before invoking your function."
  queue_visibility_timeout = local.event_batching_window_timeout + local.lambda_timeout + 20
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "lambda.zip"
  source_dir = "../src"
}

module "staging_lambda" {
  source = "./modules/transferrer_pipe"
  environment = "staging"
  queue_visibility_timeout = local.queue_visibility_timeout
  lambda_zip = data.archive_file.lambda_zip
  providers = {
    aws: aws.digitisation
  }

}

module "production_lambda" {
  source = "./modules/transferrer_pipe"
  environment = "production"
  queue_visibility_timeout = local.queue_visibility_timeout
  lambda_zip = data.archive_file.lambda_zip
    providers = {
    aws: aws.digitisation
  }
  lambda_storage = 8192
  lambda_timeout = 600
}
#
# module "restorer_lambda" {
#   source = "./modules/restorer_lambda"
#   lambda_zip = data.archive_file.lambda_zip
#   providers = {
#     aws: aws.platform
#   }
# }
