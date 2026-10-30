variable "aws_region" {
  description = "AWS region for the networking foundation"
  type        = string
  default     = "ap-south-1"
}
variable "project_name" {
  description = "Name prefix for resources"
  type        = string
  default     = "observability-platform"
}
variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.40.0.0/16"
}
