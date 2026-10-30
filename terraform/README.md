# Terraform foundation (AWS networking)

This folder uses the official AWS VPC module to create networking primitives for a future EKS deployment. It does not create EKS, NAT gateways, databases, or load balancers. Review all costs and security settings before applying.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
# Only after reviewing the plan:
terraform apply
terraform destroy
```

Configure AWS credentials using an approved method such as an AWS CLI profile or OIDC. Never commit credentials or tfstate. For a lower-cost lab, NAT gateways can be expensive; this example defaults to no NAT gateways and private subnets will not have internet egress.
