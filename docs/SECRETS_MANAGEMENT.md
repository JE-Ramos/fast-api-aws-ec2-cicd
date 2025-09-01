# AWS Secrets Manager Integration

This document explains how the application uses AWS Secrets Manager for centralized secret management, eliminating the need to maintain secrets in multiple places.

## Overview

Instead of managing secrets in GitHub Actions, environment variables, and configuration files, all secrets are now centralized in AWS Secrets Manager. This provides:

- **Single source of truth** - Update secrets in one place (AWS Console or CLI)
- **Enhanced security** - Encrypted storage with AWS KMS
- **Audit trail** - Track who accessed secrets and when
- **Rotation capability** - Automate secret rotation
- **Simplified CI/CD** - GitHub Actions only needs AWS credentials

## Architecture

### Two Types of Secrets

1. **Application Secrets** (`FastAPIAppSecrets`)
   - Runtime secrets used by the FastAPI application
   - Examples: database passwords, JWT secrets, API keys
   - Automatically loaded when app runs on EC2

2. **Deployment Secrets** (`FastAPIDeploymentSecrets`)
   - Infrastructure and deployment configuration
   - Examples: EC2 key pair name, instance IPs, GitHub repo URL
   - Used by CDK and GitHub Actions for deployments

### How It Works

```
┌─────────────────┐
│   AWS Secrets   │
│    Manager      │
├─────────────────┤
│ App Secrets     │──────┐
│ Deploy Secrets  │──┐   │
└─────────────────┘  │   │
                     │   │
     ┌───────────────┘   │
     │                   │
     ▼                   ▼
┌─────────────┐    ┌──────────┐
│ GitHub      │    │ FastAPI  │
│ Actions     │    │   App    │
└─────────────┘    └──────────┘
```

## Setup Instructions

### 1. Initial CDK Deployment

Deploy the infrastructure which creates the secrets:

```bash
cd infra
cdk deploy FastAPIEC2Stack-Staging
```

This creates two secrets in AWS Secrets Manager:
- `FastAPIAppSecrets` - For application runtime secrets
- `FastAPIDeploymentSecrets` - For deployment configuration

### 2. Configure Secrets in AWS Console

After deployment, update the secrets in AWS Secrets Manager console or using the CLI:

#### Using AWS Console

1. Go to AWS Secrets Manager in the console
2. Find `FastAPIDeploymentSecrets`
3. Click "Retrieve secret value" then "Edit"
4. Update the JSON with your values:
   ```json
   {
     "ec2_key_name": "your-key-pair-name",
     "ec2_host": "",  // Will be auto-populated after deployment
     "ec2_user": "ec2-user",
     "github_repo": "https://github.com/yourusername/yourrepo.git"
   }
   ```

5. Find `FastAPIAppSecrets`
6. Update with your application secrets:
   ```json
   {
     "db_password": "your-database-password",
     "jwt_secret": "your-jwt-secret",
     "api_keys": "your-api-keys",
     "generated_password": "auto-generated-value"
   }
   ```

#### Using the CLI Tool

```bash
# List all secrets
python scripts/manage_secrets.py list

# Set deployment secrets
python scripts/manage_secrets.py set-deployment-secret ec2_key_name "my-key-pair"

# Set application secrets
python scripts/manage_secrets.py set-app-secret jwt_secret "my-secret-jwt-key"
python scripts/manage_secrets.py set-app-secret db_password "my-db-password"

# Get a secret value
python scripts/manage_secrets.py get-app-secret jwt_secret
```

### 3. GitHub Actions Configuration

The only secrets needed in GitHub Actions are AWS credentials:

1. Go to GitHub repository settings → Secrets and variables → Actions
2. Add these secrets:
   - `AWS_ACCESS_KEY_ID` - IAM user access key
   - `AWS_SECRET_ACCESS_KEY` - IAM user secret key
   - `AWS_REGION` - AWS region (e.g., us-east-1)
   - `EC2_SSH_KEY` - Private SSH key for EC2 access (still needed for SSH)

All other secrets (EC2 host, key pair name, etc.) are retrieved from Secrets Manager during deployment.

## Local Development

### Option 1: Use Environment Variables

For local development, you can still use `.env` files:

```bash
# .env
DB_PASSWORD=local-password
JWT_SECRET=local-jwt-secret
API_KEYS=local-api-keys
USE_SECRETS_MANAGER=false
```

### Option 2: Use Secrets Manager Locally

Configure AWS credentials and enable Secrets Manager:

```bash
# Configure AWS CLI
aws configure

# Set environment variable
export USE_SECRETS_MANAGER=true

# Run the app
uvicorn app.main:app --reload
```

## Application Integration

The application automatically detects if it's running on EC2 and loads secrets from Secrets Manager:

```python
# app/config.py
class Settings(BaseSettings):
    use_secrets_manager: bool = False
    
    @validator("use_secrets_manager", pre=True)
    def check_ec2_environment(cls, v):
        # Auto-enable on EC2
        if os.path.exists("/var/lib/cloud/instance"):
            return True
        return os.getenv("USE_SECRETS_MANAGER", str(v)).lower() in ("true", "1")
```

Access secrets in your code:

```python
from app.config import get_settings

settings = get_settings()
jwt_secret = settings.jwt_secret  # Automatically loaded from Secrets Manager if enabled
```

## Deployment Workflow

1. **Developer pushes code** to GitHub
2. **GitHub Actions** runs with only AWS credentials
3. **Workflow retrieves** deployment secrets from Secrets Manager
4. **CDK deploys** infrastructure using secrets
5. **EC2 instance** starts and retrieves app secrets at runtime
6. **Application runs** with secrets loaded from Secrets Manager

## IAM Permissions

The EC2 instance role includes permissions to read secrets:

```python
# Automatically granted in CDK stack
app_secrets.grant_read(role)
deployment_secrets.grant_read(role)
```

For CI/CD, ensure the IAM user has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:UpdateSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:*:*:secret:FastAPIAppSecrets-*",
        "arn:aws:secretsmanager:*:*:secret:FastAPIDeploymentSecrets-*"
      ]
    }
  ]
}
```

## Troubleshooting

### Secrets not loading on EC2

1. Check IAM role permissions:
   ```bash
   aws sts get-caller-identity
   aws secretsmanager get-secret-value --secret-id FastAPIAppSecrets
   ```

2. Verify environment variable:
   ```bash
   echo $USE_SECRETS_MANAGER
   ```

3. Check application logs:
   ```bash
   sudo journalctl -u fastapi -f
   ```

### GitHub Actions deployment fails

1. Verify AWS credentials are set correctly in GitHub Secrets
2. Check if secrets exist in AWS:
   ```bash
   aws secretsmanager list-secrets
   ```

3. Ensure IAM user has necessary permissions

## Benefits

1. **Security** - No plaintext secrets in code or CI/CD
2. **Simplicity** - Update secrets in one place
3. **Auditability** - Track secret access
4. **Scalability** - Easy to add new environments
5. **Cost-effective** - Minimal AWS Secrets Manager costs

## Migration from Environment Variables

To migrate existing deployments:

1. Deploy the updated CDK stack
2. Copy existing secrets to AWS Secrets Manager
3. Update GitHub Actions to use new workflow
4. Remove old secrets from GitHub Actions (except AWS credentials)
5. Verify application loads secrets correctly

## Future Enhancements

- [ ] Implement automatic secret rotation
- [ ] Add secret versioning and rollback
- [ ] Integrate with AWS Parameter Store for non-secret config
- [ ] Add secret validation before deployment
- [ ] Implement secret backup and recovery