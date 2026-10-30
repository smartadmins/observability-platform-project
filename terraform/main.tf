module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"

  name = var.project_name
  cidr = var.vpc_cidr

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnets  = ["10.40.1.0/24", "10.40.2.0/24"]
  private_subnets = ["10.40.11.0/24", "10.40.12.0/24"]

  enable_nat_gateway = false
  single_nat_gateway = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Project     = var.project_name
    Environment = "learning"
    ManagedBy   = "Terraform"
  }
}
