variable "lambda_zip" {
  type = object(
    {
      output_path = string,
      output_base64sha256 = string
    }
  )
}
