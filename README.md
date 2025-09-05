# FastAPI AWS EC2 CI/CD Project

[![codecov](https://codecov.io/gh/JE-Ramos/fast-api-aws-ec2-cicd/branch/main/graph/badge.svg)](https://codecov.io/gh/JE-Ramos/fast-api-aws-ec2-cicd)
[![Tests](https://github.com/JE-Ramos/fast-api-aws-ec2-cicd/actions/workflows/deploy.yml/badge.svg)](https://github.com/JE-Ramos/fast-api-aws-ec2-cicd/actions/workflows/deploy.yml)

A production-ready containerized FastAPI SaaS application with blue-green deployment pattern, automated CI/CD pipeline using Git Flow, AWS CDK, and ECR.

## Blue-Green Deployment & CI/CD Architecture

```mermaid
flowchart TD
    %% Git Flow with Blue-Green Deployment
    DEV[👨‍💻 Developer] -->|Feature Branch| FEATURE[feature/branch]
    FEATURE -->|Pull Request| DEVELOP[🔄 develop branch]
    DEVELOP -->|Create Release| RELEASE[release/v1.x.x]
    RELEASE -->|After Testing| MAIN[🚀 main branch]
    RELEASE -->|Merge back| DEVELOP
    
    %% CI/CD Pipeline with Three Environments
    DEVELOP -->|Auto Deploy| BUILD_STAGING[🐳 Build Docker Image]
    BUILD_STAGING -->|Tag: staging-sha| ECR_STAGING[📦 ECR: fastapi-staging]
    ECR_STAGING -->|Deploy| STAGING[🧪 STAGING Environment]
    
    RELEASE -->|Auto Deploy| BUILD_BLUE[🐳 Build Docker Image]
    BUILD_BLUE -->|Tag: blue-version-sha| ECR_BLUE[📦 ECR: fastapi-production-blue]
    ECR_BLUE -->|Deploy| PROD_BLUE[🔵 PRODUCTION-BLUE<br/>Release Testing]
    
    MAIN -->|Auto Deploy| BUILD_GREEN[🐳 Build Docker Image]
    BUILD_GREEN -->|Tag: green-date-sha| ECR_GREEN[📦 ECR: fastapi-production-green]
    ECR_GREEN -->|Deploy| PROD_GREEN[🟢 PRODUCTION-GREEN<br/>Live Traffic]
    
    %% ECR Repositories
    subgraph ECR_REPOS[📦 Amazon ECR Repositories]
        ECR_STAG_REPO[fastapi-staging<br/>🏷️ staging-sha, latest]
        ECR_BLUE_REPO[fastapi-production-blue<br/>🏷️ blue-version-sha, latest]
        ECR_GREEN_REPO[fastapi-production-green<br/>🏷️ green-date-sha, latest]
    end
    
    %% Three Separate Environments
    subgraph AWS_STAGING[🧪 Staging Environment]
        ALB_STAG[⚖️ Load Balancer]
        ASG_STAG[🔄 Auto Scaling Group]
        EC2_STAG[🖥️ EC2 Instances]
        SECRETS_STAG[🔐 Secrets Manager]
    end
    
    subgraph AWS_PROD_BLUE[🔵 Production-Blue Environment]
        ALB_BLUE[⚖️ Load Balancer]
        ASG_BLUE[🔄 Auto Scaling Group]
        EC2_BLUE[🖥️ EC2 Instances]
        SECRETS_BLUE[🔐 Secrets Manager]
    end
    
    subgraph AWS_PROD_GREEN[🟢 Production-Green Environment]
        ALB_GREEN[⚖️ Load Balancer]
        ASG_GREEN[🔄 Auto Scaling Group]
        EC2_GREEN[🖥️ EC2 Instances]
        SECRETS_GREEN[🔐 Secrets Manager]
    end
    
    %% Shared Resources
    subgraph SHARED_AWS[🌐 Shared AWS Resources]
        VPC[VPC with Public/Private Subnets]
        S3[🪣 S3 Bucket for Assets]
    end
    
    %% Traffic Flow
    USERS[🌍 Users] -->|Test Traffic| ALB_STAG
    USERS -->|Release Testing| ALB_BLUE
    USERS -->|Live Traffic| ALB_GREEN
    
    %% Blue-Green Switch Capability
    PROD_BLUE -.->|After Approval| TRAFFIC_SWITCH[🔄 Traffic Switch]
    TRAFFIC_SWITCH -.->|Swap URLs| PROD_GREEN
    
    %% Rollback Capability
    ECR_GREEN_REPO -->|Rollback| EC2_GREEN
    
    %% Styling
    classDef staging fill:#e1f5fe
    classDef blue fill:#c8e6c9
    classDef green fill:#fff3e0
    classDef cicd fill:#f3e5f5
    classDef ecr fill:#e8f5e8
    classDef shared fill:#f9f9f9
    
    class DEVELOP,BUILD_STAGING,ECR_STAGING,STAGING,AWS_STAGING,ALB_STAG,ASG_STAG,EC2_STAG,SECRETS_STAG,ECR_STAG_REPO staging
    class RELEASE,BUILD_BLUE,ECR_BLUE,PROD_BLUE,AWS_PROD_BLUE,ALB_BLUE,ASG_BLUE,EC2_BLUE,SECRETS_BLUE,ECR_BLUE_REPO blue
    class MAIN,BUILD_GREEN,ECR_GREEN,PROD_GREEN,AWS_PROD_GREEN,ALB_GREEN,ASG_GREEN,EC2_GREEN,SECRETS_GREEN,ECR_GREEN_REPO green
    class FEATURE,BUILD_STAGING,BUILD_BLUE,BUILD_GREEN cicd
    class ECR_REPOS,ECR_STAG_REPO,ECR_BLUE_REPO,ECR_GREEN_REPO ecr
    class SHARED_AWS,VPC,S3 shared
```

### Blue-Green Deployment Strategy

1. **Feature Development** → Create `feature/branch` → PR to `develop`
2. **Staging Deployment** → `develop` branch auto-deploys to **STAGING** environment
3. **Release Preparation** → Create `release/v1.x.x` branch FROM `develop`
4. **Release Testing** → `release/v1.x.x` auto-deploys to **PRODUCTION-BLUE** (isolated from staging)
5. **Production Deployment** → After testing, merge to `main` → auto-deploys to **PRODUCTION-GREEN**
6. **Release Completion** → Merge `release/v1.x.x` back to `develop`
7. **Rollback** → Auto Scaling Group pulls previous ECR image tags or swap blue/green environments

#### Why Three Environments?
- **Staging**: Continuous integration testing (develop branch changes don't affect releases)
- **Production-Blue**: Isolated release testing (no interference from ongoing development)
- **Production-Green**: Live production traffic (stable, approved releases only)

### Container Image Tagging Strategy

- **Staging**: `fastapi-staging:staging-{short-sha}` + `:latest`
- **Production-Blue**: `fastapi-production-blue:blue-{version}-{short-sha}` + `:latest`
- **Production-Green**: `fastapi-production-green:green-{date}-{short-sha}` + `:latest`
- **Rollback**: Deploy previous image tag from ECR history or swap environments

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
- Docker (required for production deployment)
- AWS CDK CLI v2

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

### Running the Containerized Application

**Using Docker (Recommended):**
```bash
# Build the Docker image
docker build -t fastapi-app .

# Run with Secrets Manager integration
docker run -d -p 8000:8000 --name fastapi-local \
  -e USE_SECRETS_MANAGER=true \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  fastapi-app

# Check logs
docker logs fastapi-local
```

**Direct Python (Development only):**
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

### Architecture Overview

The infrastructure satisfies all tasks.md requirements:
- ✅ **VPC with public & private subnets** (line 29)
- ✅ **Two EC2 instances** - Actually three environments for proper blue-green (line 30)
- ✅ **Security groups with least privilege** (line 31)
- ✅ **S3 bucket for static assets** (line 32)
- ✅ **Modular, parameterized, reusable** infrastructure (line 33)
- ✅ **Automated tests on code push** (line 37)
- ✅ **Builds the application** (line 38)
- ✅ **Deploys to staging on develop merge** (line 39)
- ✅ **Deploys to production on approved main release** (line 40)
- ✅ **Stores build artifacts in ECR** (line 41)
- ✅ **Rollback capabilities** via Auto Scaling Groups (line 42)
- ✅ **AWS Secrets Manager integration** (lines 44-46)
- ✅ **Infrastructure as Code** using AWS CDK

## ☁️ Container-Based AWS Deployment

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

# 2. Deploy staging environment
cdk deploy FastAPIEC2Stack-Staging

# 3. Deploy production-blue environment (for release testing)
cdk deploy FastAPIEC2Stack-ProductionBlue

# 4. Deploy production-green environment (for live traffic)
cdk deploy FastAPIEC2Stack-ProductionGreen

# 4. Save the Load Balancer DNS from outputs
```

### Step 4: Container Deployment via CI/CD

1. **Push to develop branch** → Auto-deploys to **Staging**
2. **Create release branch** → `git checkout -b release/v1.0.0` → Auto-deploys to **Production-Blue**
3. **Test in Production-Blue** → Verify release in isolated environment
4. **Merge to main** → Auto-deploys to **Production-Green** (live traffic)
5. **Access via Load Balancer DNS** for each environment (from CDK outputs)

**Container Images per Environment:**
- Staging: `fastapi-staging:staging-{commit-sha}`
- Production-Blue: `fastapi-production-blue:blue-{version}-{sha}`
- Production-Green: `fastapi-production-green:green-{date}-{sha}`

### Cleanup (Important!)
```bash
cd infra
cdk destroy FastAPIEC2Stack-Staging          # Destroy staging
cdk destroy FastAPIEC2Stack-ProductionBlue    # Destroy production-blue
cdk destroy FastAPIEC2Stack-ProductionGreen   # Destroy production-green
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

The GitHub Actions workflow implements blue-green deployment with Git Flow:
1. **Feature branches** → Run tests and PR checks
2. **Develop branch** → Build Docker image → Push to ECR → Deploy to **Staging**
3. **Release branches** → Build Docker image → Push to ECR → Deploy to **Production-Blue**
4. **Main branch** → Build Docker image → Push to ECR → Deploy to **Production-Green**
5. **Auto rollback** via Auto Scaling Group if health checks fail

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - IAM user with ECR and CDK permissions
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key  
- `AWS_REGION` - AWS region (default: us-east-1)
- `CODECOV_TOKEN` - (Optional) Token for Codecov integration

**🆕 Container-First Approach:** 
- Application secrets managed in AWS Secrets Manager
- Container images stored in ECR with environment-specific tagging
- Zero-downtime deployments via Auto Scaling Group rolling updates
- Automatic PR comments with deployment URLs

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

- ✅ **Secrets Management**: AWS Secrets Manager for all sensitive data
- ✅ **Container Security**: ECR image scanning enabled
- ✅ **Network Security**: VPC with private subnets, security groups with least privilege
- ✅ **IAM Security**: Minimal permissions for CI/CD user
- ✅ **Zero Credentials in Code**: No secrets in repositories or container images
- ✅ **HTTPS Ready**: Load balancer supports SSL termination
- 🔄 **Regular Updates**: Automated dependency updates via Dependabot

## Rollback Strategy

1. **ECR Image History**: Previous releases tagged as `release-v1.x.x`
2. **Auto Scaling Group**: Rolling updates with health checks
3. **Zero Downtime**: Min 1 instance always running during deployment
4. **Automated Rollback**: Failed health checks trigger automatic rollback

## License

MIT