variable "environment" {
  type = string
  validation {
    condition = contains(["staging", "production"], var.environment)
    error_message = "environment must be one of staging or production"
  }
}

variable "queue_visibility_timeout" {
  type = number
}

variable "lambda_zip" {
  type = object(
    {
      output_path = string,
      output_base64sha256 = string
    }
  )
}