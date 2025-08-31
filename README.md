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

### IAM Setup for CI/CD (Optional - for GitHub Actions)

**When to use:** Only for GitHub Actions automated deployments after CDK bootstrap is complete.

**When NOT to use:** CDK bootstrap requires admin access - use your main AWS account for bootstrap.

Create an IAM user with limited permissions for CI/CD:

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

1. Navigate to **IAM** → **Users** → **Create user**
2. **Step 1 - Specify user details:**
   - User name: `fastapi-deploy`
   - Click **Next**
3. **Step 2 - Set permissions:**
   - Select **Attach policies directly**
   - Search for `FastAPIEC2DeployPolicy` in the search box
   - Check the checkbox next to `FastAPIEC2DeployPolicy`
   - Click **Next**
4. **Step 3 - Review and create:**
   - Review the settings
   - Click **Create user**

#### Step 3: Create Access Keys

1. After creating the user, click on the username `fastapi-deploy`
2. Go to **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. **Step 1 - Access key best practices:**
   - Select **Command Line Interface (CLI)**
   - Check the confirmation checkbox
   - Click **Next**
6. **Step 2 - Set description tag** (optional):
   - Add description: "CDK deployment key"
   - Click **Create access key**
7. **Step 3 - Retrieve access keys:**
   - Copy **Access key** and **Secret access key**
   - ⚠️ **Important**: Save these credentials immediately! The secret key won't be shown again
   - Optionally download the .csv file for backup
8. Add these credentials to your `.env` file:
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

## Deployment Options

Choose between **local development** or **AWS infrastructure deployment**:

## 🏠 Local Development (Recommended for testing)

### Quick Start
```bash
./scripts/setup_local.sh
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Access at: http://localhost:8000/docs

## ☁️ AWS Infrastructure Deployment

**Reference:** [AWS CDK Bootstrapping Guide](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)

### Prerequisites Check
- ✅ AWS Account with admin access (for bootstrap) or existing CDK bootstrap
- ✅ AWS CDK CLI: `npm install -g aws-cdk`
- ✅ Node.js and Python 3.9+

### Step 1: Check if CDK is Already Bootstrapped

```bash
# Check if your AWS account is already bootstrapped
aws cloudformation describe-stacks --stack-name CDKToolkit --region us-east-1
```

**If you get a stack description:** ✅ Your account is already bootstrapped! Skip to Step 3.

**If you get "Stack does not exist":** Continue to Step 2.

### Step 2: Bootstrap CDK (First Time Only)

**📚 Official AWS Documentation:**
- [CDK Bootstrap Guide](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
- [CDK Bootstrap Environment](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html)
- [CDK Permissions Guide](https://docs.aws.amazon.com/cdk/v2/guide/permissions.html)

**Use Admin Credentials (Required)**

According to [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html), CDK bootstrap requires extensive permissions including:
```
CloudFormation: *, ECR: *, SSM: *, S3: *, IAM: *
```

**This effectively requires admin access.** Use your main AWS account credentials:

```bash
# Configure with your admin AWS credentials
aws configure
# Enter: Access Key ID, Secret Key, Region (us-east-1), Output format (json)

# Bootstrap your account
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

**What CDK Bootstrap Creates:**
- S3 bucket for CDK assets
- ECR repository for Docker images  
- IAM roles for deployments (with AdministratorAccess by default)
- CloudFormation execution role

### Step 3: Deploy Infrastructure

```bash
# 1. Install CDK dependencies
cd infra
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Preview deployment (optional)
cdk diff

# 3. Deploy infrastructure
cdk deploy FastAPIEC2Stack

# 4. Save the EC2 IP from the output
```

### Step 4: Deploy Application to EC2

1. **Update repository URL** in `infra/stacks/ec2_stack.py` (line ~41):
   ```python
   "git clone https://github.com/JE-Ramos/fast-api-aws-ec2-cicd.git app",
   ```

2. **The application will auto-deploy** via the user data script when the EC2 instance starts

3. **Access your app** at: `http://YOUR-EC2-IP:8000`

### Cleanup (Important!)
```bash
cd infra
cdk destroy FastAPIEC2Stack  # Avoid AWS charges
```

## 🤔 Already Bootstrapped Account?

According to [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html):

> "It's safe to re-bootstrap an environment. If an environment has already been bootstrapped, the bootstrap stack will be upgraded if necessary. Otherwise, nothing will happen."

**If your account is already bootstrapped:** Skip directly to Step 3 and deploy your infrastructure!

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
- `AWS_ACCESS_KEY_ID` - Limited IAM user access key (see IAM Setup section)
- `AWS_SECRET_ACCESS_KEY` - Limited IAM user secret key  
- `AWS_REGION` - AWS region (default: us-east-1)
- `CODECOV_TOKEN` - (Optional) Token for Codecov integration
- `EC2_HOST` - EC2 instance IP/hostname for deployment
- `EC2_USER` - EC2 username (usually ec2-user)
- `EC2_SSH_KEY` - Private SSH key for EC2 access

**Note:** For CI/CD, use the limited IAM user created in the "IAM Setup for CI/CD" section above.

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