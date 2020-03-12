# Create an index table in dynamodb

# Required
variable "name" { type = string }
variable "env" { type = string }

# Optional
variable "tags" { default = {} }
variable "stream_enabled" { default = false }
variable "stream_view" { default = "NEW_IMAGE" }
variable "hash_key" { default = "id" }
variable "billing_mode" { default = "PAY_PER_REQUEST" }
variable "read_capacity" { default = 0 }
variable "write_capacity" { default = 0 }

# Resources
resource "aws_dynamodb_table" "this" {
  name = "${var.env}_${var.name}_index"

  billing_mode   = var.billing_mode
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity

  hash_key = var.hash_key

  attribute {
    name = var.hash_key
    type = "S"
  }

  stream_enabled   = var.stream_enabled
  stream_view_type = var.stream_enabled ? var.stream_view : ""

  tags = var.tags
}

resource "aws_ssm_parameter" "name" {
  name  = "/${var.env}/dynamo/${var.name}/table/name"
  value = aws_dynamodb_table.this.id
  type  = "SecureString"
  tags  = var.tags
}

resource "aws_ssm_parameter" "arn" {
  name  = "/${var.env}/dynamo/${var.name}/table/arn"
  value = aws_dynamodb_table.this.arn
  type  = "SecureString"
  tags  = var.tags
}

resource "aws_ssm_parameter" "stream_arn" {
  count = var.stream_enabled ? 1 : 0
  name  = "/${var.env}/dynamo/${var.name}/stream/arn"
  value = aws_dynamodb_table.this.stream_arn
  type  = "SecureString"
  tags  = var.tags
}

resource "aws_ssm_parameter" "stream_label" {
  count = var.stream_enabled ? 1 : 0
  name  = "/${var.env}/dynamo/${var.name}/stream/label"
  value = aws_dynamodb_table.this.stream_label
  type  = "SecureString"
  tags  = var.tags
}

# Outputs
output "table_name" {
  value = aws_dynamodb_table.this.id
}

output "table_arn" {
  value = aws_dynamodb_table.this.arn
}

output "ssm_param_table_name" {
  value = aws_ssm_parameter.name.name
}

output "ssm_param_table_arn" {
  value = aws_ssm_parameter.arn.name
}
