# Infrastructure Deployment Guide

This directory contains AWS CDK Infrastructure as Code (IaC) for deploying a production-ready FastAPI SaaS application with automated CI/CD pipeline.

## Architecture Overview

**Problem Solved:** Replaces manual AWS console provisioning with automated, version-controlled infrastructure.

**Infrastructure Components:**
- ✅ VPC with public & private subnets across multiple AZs
- ✅ Application Load Balancer distributing traffic to EC2 instances  
- ✅ Auto Scaling Group managing EC2 instances (staging + production)
- ✅ Security groups with least privilege access
- ✅ S3 bucket for static assets and build artifacts
- ✅ AWS Secrets Manager for secure credential storage
- ✅ Parameterized and reusable across environments

## Prerequisites

### AWS Account Setup
```bash
# Check if CDK is already bootstrapped
aws cloudformation describe-stacks --stack-name CDKToolkit --region us-east-1

# If not bootstrapped (requires admin access)
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

### Dependencies
```bash
# Install CDK CLI
npm install -g aws-cdk

# Install Python dependencies
cd infra
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Pre-Deployment Validation

**Always validate before deploying to production:**

```bash
# 1. Synthesize CloudFormation template (no deployment)
cdk synth

# 2. Preview changes against existing stack
cdk diff

# 3. Check for configuration issues
cdk doctor

# 4. Security scanning (optional but recommended)
npm install -g cfn-nag
cfn-nag_scan --input-path cdk.out/FastAPIEC2Stack.template.json
```

## Deployment Instructions

### 1. Staging Environment

```bash
# Deploy with staging parameters
cdk deploy FastAPIEC2Stack \
  --parameters Environment=staging \
  --parameters InstanceType=t3.micro \
  --parameters MinCapacity=1 \
  --parameters MaxCapacity=2
```

### 2. Production Environment

```bash
# Deploy with production parameters
cdk deploy FastAPIEC2Stack \
  --parameters Environment=production \
  --parameters InstanceType=t3.small \
  --parameters MinCapacity=2 \
  --parameters MaxCapacity=5 \
  --require-approval never
```

### 3. Environment-Specific Stacks (Alternative)

For complete separation, deploy separate stacks:

```bash
# Deploy staging stack
cdk deploy FastAPIEC2Stack-Staging \
  --context environment=staging

# Deploy production stack  
cdk deploy FastAPIEC2Stack-Production \
  --context environment=production
```

## Stack Parameters

| Parameter | Default | Description | Staging | Production |
|-----------|---------|-------------|---------|------------|
| Environment | production | Environment name | staging | production |
| InstanceType | t3.micro | EC2 instance type | t3.micro | t3.small+ |
| MinCapacity | 1 | Min ASG instances | 1 | 2 |
| MaxCapacity | 3 | Max ASG instances | 2 | 5+ |

## Post-Deployment Configuration

### 1. Update Repository URL

**Critical:** Update the GitHub repository URL in `stacks/ec2_stack.py:290`:

```python
"git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git app",
```

### 2. Configure Secrets

```bash
# Get secrets ARN from stack output
aws cloudformation describe-stacks \
  --stack-name FastAPIEC2Stack \
  --query 'Stacks[0].Outputs[?OutputKey==`SecretsManagerArn`].OutputValue' \
  --output text

# Update secrets (replace SECRET_ARN)
aws secretsmanager update-secret \
  --secret-id SECRET_ARN \
  --secret-string '{"db_password":"your-db-password","jwt_secret":"your-jwt-secret","api_keys":"your-api-keys"}'
```

### 3. Verify Deployment

```bash
# Get load balancer DNS
aws cloudformation describe-stacks \
  --stack-name FastAPIEC2Stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text

# Test application
curl http://YOUR-LOAD-BALANCER-DNS/health
curl http://YOUR-LOAD-BALANCER-DNS/api/v1/items
```

## CI/CD Pipeline Integration

The infrastructure supports automated deployments:

### Staging Deployment (develop branch)
- Automatic deployment on merge to `develop`
- Uses staging parameters
- Artifact storage in S3 bucket

### Production Deployment (main branch)
- Requires approval for deployment
- Uses production parameters
- Rollback capabilities through ASG rolling updates

### Required GitHub Secrets
```bash
# Infrastructure deployment secrets
AWS_ACCESS_KEY_ID=<limited-iam-user-key>
AWS_SECRET_ACCESS_KEY=<limited-iam-user-secret>
AWS_REGION=us-east-1
```

## Rollback Procedures

### 1. Application Rollback (via Auto Scaling Group)

```bash
# Rollback to previous launch template version
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name FastAPIAutoScalingGroup \
  --launch-template LaunchTemplateName=FastAPILaunchTemplate,Version='$Previous'

# Force instance refresh to apply rollback
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name FastAPIAutoScalingGroup
```

### 2. Infrastructure Rollback (via CDK)

```bash
# View deployment history
aws cloudformation describe-stack-events --stack-name FastAPIEC2Stack

# Rollback to previous stack version (if needed)
aws cloudformation cancel-update-stack --stack-name FastAPIEC2Stack
```

### 3. Application Code Rollback (via Git)

```bash
# SSH to instances and rollback code
# (Better: Use CodeDeploy for automated rollbacks)
git checkout <previous-commit-hash>
sudo systemctl restart fastapi
```

## Security Considerations

### Network Security
- ✅ EC2 instances in private subnets only
- ✅ Load balancer in public subnets
- ✅ Security groups with least privilege (no direct internet access to instances)
- ✅ VPC isolation from other resources

### Access Control
- ✅ IAM roles with minimal required permissions
- ✅ No hardcoded credentials in code or configs
- ✅ Secrets Manager integration for runtime secret retrieval
- ✅ Instance profile for secure AWS service access

### Data Protection
- ✅ S3 bucket encryption enabled
- ✅ Secrets Manager encryption at rest
- ✅ VPC flow logs for network monitoring
- ✅ CloudWatch logs for application monitoring

## Troubleshooting

### Common Issues

**CDK Bootstrap Errors:**
- Ensure you have admin access for initial bootstrap
- Check AWS credentials are correctly configured
- Verify account ID and region match your configuration

**Deployment Failures:**
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name FastAPIEC2Stack

# Check CDK context and clear if needed
cdk context --clear
```

**Instance Launch Failures:**
```bash
# Check Auto Scaling Group activity
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name FastAPIAutoScalingGroup

# Check instance logs via SSM
aws ssm start-session --target INSTANCE-ID
```

### Monitoring and Logs

```bash
# View application logs
aws logs describe-log-streams --log-group-name /aws/ec2/fastapi

# Monitor load balancer metrics
aws elbv2 describe-target-health --target-group-arn TARGET-GROUP-ARN
```

## Cost Optimization

**Development:**
- Use `t3.micro` instances (free tier eligible)
- Set MinCapacity=1, MaxCapacity=2
- Use `RemovalPolicy.DESTROY` for easy cleanup

**Production:**
- Use `t3.small` or larger based on load
- Set appropriate capacity limits
- Use `RemovalPolicy.RETAIN` for data persistence
- Monitor CloudWatch metrics for right-sizing

## Cleanup

```bash
# Destroy infrastructure (saves costs)
cdk destroy FastAPIEC2Stack

# Clean up CDK artifacts
rm -rf cdk.out
```