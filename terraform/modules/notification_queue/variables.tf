variable "queue_visibility_timeout" {
  type = number
}

variable "environment" {
  type = string
  validation {
    condition = contains(["staging", "production"], var.environment)
    error_message = "environment must be one of staging or production"
  }
}

variable "action_name" {
  type = string
}

variable "extra_topics" {
  type = list(string)
  default = []
  description = "List of topics defined elsewhere that the queue should subscribe to"
}