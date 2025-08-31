# FastAPI AWS EC2 CI/CD Project

[![codecov](https://codecov.io/gh/JE-Ramos/fast-api-aws-ec2-cicd/branch/main/graph/badge.svg)](https://codecov.io/gh/JE-Ramos/fast-api-aws-ec2-cicd)
[![Tests](https://github.com/JE-Ramos/fast-api-aws-ec2-cicd/actions/workflows/deploy.yml/badge.svg)](https://github.com/JE-Ramos/fast-api-aws-ec2-cicd/actions/workflows/deploy.yml)

A production-ready FastAPI application deployed on AWS EC2 with CI/CD pipeline using AWS CDK.

## Project Structure

```
.
├── app/                    # FastAPI application
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   ├── config.py          # Application configuration
│   ├── main.py            # FastAPI app entry point
│   └── requirements.txt   # Python dependencies
├── infra/                  # AWS CDK infrastructure
│   ├── stacks/            # CDK stacks
│   ├── constructs/        # Custom CDK constructs
│   ├── app.py             # CDK app entry point
│   ├── cdk.json           # CDK configuration
│   └── requirements.txt   # CDK dependencies
├── .github/
│   └── workflows/         # GitHub Actions CI/CD
├── .env.example           # Environment variables template
└── README.md              # Project documentation
```

## Prerequisites

- Python 3.9+
- AWS Account with configured credentials
- AWS CDK CLI (`npm install -g aws-cdk`)
- Docker (optional, for containerized deployment)

### Initial AWS Setup (One-Time Configuration)

Before deploying the infrastructure, you need to create an IAM user with the minimum required permissions. Follow these steps using the AWS Console:

#### Step 1: Create IAM Policy

1. **Login to AWS Console** at https://console.aws.amazon.com/
2. Navigate to **IAM** → **Policies** → **Create policy**
3. Click on **JSON** tab
4. Copy and paste the contents from `infra/iam-policy.json`
5. Click **Next: Tags** (optional: add tags)
6. Click **Next: Review**
7. Name the policy: `FastAPIEC2DeployPolicy`
8. Add description: "Minimum permissions for FastAPI EC2 CDK deployment"
9. Click **Create policy**

#### Step 2: Create IAM User

1. Navigate to **IAM** → **Users** → **Add users**
2. User name: `fastapi-deploy`
3. Select **Access key - Programmatic access**
4. Click **Next: Permissions**
5. Select **Attach existing policies directly**
6. Search for and select `FastAPIEC2DeployPolicy`
7. Click **Next: Tags** (optional: add tags)
8. Click **Next: Review**
9. Click **Create user**

#### Step 3: Save Credentials

1. **Download .csv** or copy the credentials shown:
   - Access key ID
   - Secret access key (⚠️ This is shown only once!)
2. Add these credentials to your `.env` file:
   ```bash
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION=us-east-1
   CDK_DEFAULT_ACCOUNT=123456789012  # Your AWS Account ID
   CDK_DEFAULT_REGION=us-east-1
   ```

#### Step 4: Find Your AWS Account ID

1. In AWS Console, click your username in the top-right
2. Click **Account** or look at the dropdown
3. Copy your 12-digit Account ID
4. Add it to `.env` as `CDK_DEFAULT_ACCOUNT`

### Minimum IAM Permissions

The policy in `infra/iam-policy.json` includes permissions for:
- **CloudFormation**: Stack management for CDK
- **EC2**: VPC, subnets, security groups, instances
- **IAM**: Roles and instance profiles for EC2
- **S3**: CDK asset storage
- **SSM**: Parameter store for CDK
- **ECR**: Container registry for CDK assets

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd fast-api-aws-ec2-cicd
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your AWS credentials and settings
```

### 3. Install dependencies

For the FastAPI app:
```bash
cd app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

For AWS CDK:
```bash
cd ../infra
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Local Development

### Running the FastAPI application
```bash
cd app
uvicorn main:app --reload --port 8000
```

Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Infrastructure Deployment

### Prerequisites Check
Before deploying, ensure you have:
- ✅ Created IAM user with deployment policy (see Initial AWS Setup above)
- ✅ Added AWS credentials to `.env` file
- ✅ Installed AWS CDK: `npm install -g aws-cdk`

### Deploy Infrastructure with CDK

1. **Configure AWS credentials from .env**:
```bash
source .env
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set region "${AWS_REGION:-us-east-1}"
```

2. **Verify credentials are working**:
```bash
aws sts get-caller-identity
# Should return your account details
```

3. **Install CDK dependencies**:
```bash
cd infra
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Bootstrap CDK** (first time only):
```bash
cdk bootstrap aws://$CDK_DEFAULT_ACCOUNT/$CDK_DEFAULT_REGION
```

5. **Preview the deployment** (optional):
```bash
cdk diff
```

6. **Deploy the infrastructure**:
```bash
cdk deploy FastAPIEC2Stack
```

7. **Note the outputs**:
   - The deployment will output the EC2 instance's public IP
   - Save this IP for application deployment

### Destroy Infrastructure (when done)
To avoid AWS charges, destroy the infrastructure when not in use:
```bash
cd infra
cdk destroy FastAPIEC2Stack
```

### Application Deployment to EC2

After infrastructure is deployed, deploy the application:

1. **Update the GitHub repository URL** in `infra/stacks/ec2_stack.py`
2. **SSH into your EC2 instance** (replace with your IP):
```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```
3. **Run the setup script**:
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/fast-api-aws-ec2-cicd/main/scripts/setup_ec2.sh | bash
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/items` - List items
- `GET /api/v1/items/{item_id}` - Get specific item
- `POST /api/v1/items` - Create new item

## CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs tests on push to main
2. Builds and validates the application
3. Deploys to AWS EC2 using CDK

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` - AWS region (default: us-east-1)
- `CODECOV_TOKEN` - (Optional) Token for Codecov integration
- `EC2_HOST` - EC2 instance IP/hostname for deployment
- `EC2_USER` - EC2 username (usually ec2-user)
- `EC2_SSH_KEY` - Private SSH key for EC2 access

## Environment Variables

See `.env.example` for all required environment variables:
- AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- AWS region configuration
- Application settings

## Testing

### Running Tests Locally

```bash
# Run tests with coverage report
pytest

# Run tests with specific verbosity
pytest -v

# Run only unit tests
pytest -m unit

# Run tests and generate HTML coverage report
pytest --cov-report=html
# Open htmlcov/index.html in browser to view detailed coverage

# Run tests without coverage (faster)
pytest --no-cov
```

### Coverage Requirements

- Minimum coverage: 80%
- Coverage includes branch coverage
- Reports generated: Terminal, HTML, XML, JSON

### Coverage Reports

After running tests, coverage reports are available in:
- **Terminal**: Displayed immediately after test run
- **HTML**: `htmlcov/index.html` - Interactive HTML report
- **XML**: `coverage.xml` - For CI/CD integration
- **JSON**: `coverage.json` - Machine-readable format

## Security Considerations

- Never commit `.env` files with real credentials
- Use AWS IAM roles for production
- Implement proper authentication/authorization
- Use HTTPS in production
- Regularly update dependencies

## License

MIT