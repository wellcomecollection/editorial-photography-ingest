variable "queue_arn" {
  type = string
}

variable "function_name" {
  type = string
}

variable "role_name" {
    type = string
}

variable "trigger_name" {
  type = string
}
variable "batch_size" {
  type = number
  default = 1
}