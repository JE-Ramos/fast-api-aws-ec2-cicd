# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- `pytest` - Run all tests with coverage (min 80% required)
- `pytest -v` - Run tests with verbose output
- `pytest -m unit` - Run only unit tests
- `pytest -m integration` - Run only integration tests
- `pytest --no-cov` - Run tests without coverage (faster)
- `make test` - Run tests via Makefile
- `make test-coverage` - Run tests and open HTML coverage report

### Linting and Formatting
- `flake8 app --max-line-length=127` - Lint the application code
- `black app --check` - Check code formatting
- `black app` - Format code with Black
- `make lint` - Run linting via Makefile
- `make format` - Format code via Makefile

### Local Development
- `uvicorn app.main:app --reload --port 8000` - Run FastAPI app locally
- `make run` - Run app via Makefile
- `./scripts/setup_local.sh` - Set up local development environment

### AWS CDK Infrastructure
- `cd infra && cdk synth` - Synthesize CDK templates
- `cd infra && cdk diff` - Preview infrastructure changes
- `cd infra && cdk deploy FastAPIEC2Stack-Staging` - Deploy staging infrastructure
- `cd infra && cdk deploy FastAPIEC2Stack-Production` - Deploy production infrastructure
- `cd infra && cdk destroy FastAPIEC2Stack-Staging` - Destroy staging infrastructure
- `make cdk-synth`, `make cdk-deploy`, `make cdk-destroy` - CDK commands via Makefile

### Docker and ECR
- `docker build -t fastapi-app .` - Build Docker image locally
- `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin` - Login to ECR
- `docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/fastapi-staging:latest` - Push to ECR

### Environment Setup
- Bootstrap CDK (first time): `cdk bootstrap aws://ACCOUNT-ID/us-east-1`
- Check if bootstrapped: `aws cloudformation describe-stacks --stack-name CDKToolkit --region us-east-1`

## Architecture Overview

### Project Structure
- **app/** - FastAPI application with modular structure
- **infra/** - AWS CDK infrastructure as code
- **tests/** - Comprehensive test suite with 80%+ coverage requirement
- **scripts/** - Setup and deployment automation

### Key Components

#### FastAPI Application (`app/`)
- **main.py** - FastAPI app entry point with CORS middleware
- **config.py** - Pydantic settings with environment variable management
  - Uses `extra="ignore"` in ConfigDict to handle CDK environment variables
  - Implements singleton pattern with `@lru_cache()` for settings
- **api/routes.py** - API endpoints under `/api/v1` prefix
- Configuration loads from `.env` file with AWS credentials

#### CDK Infrastructure (`infra/`)
- **app.py** - CDK app entry point with staging/production environments
- **stacks/ec2_stack.py** - Main infrastructure stack
  - Creates VPC with public/private subnets across multiple AZs
  - Application Load Balancer with target groups
  - Auto Scaling Group with rolling update capabilities
  - ECR repository for Docker image storage
  - S3 bucket for static assets and build artifacts
  - Secrets Manager for secure credential management
  - IAM roles with least-privilege permissions
- **iam-policy.json** - Minimal IAM permissions for CI/CD deployment

### Environment Configuration
- Project uses `.env` files for configuration
- AWS credentials required: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- CDK settings: `CDK_DEFAULT_ACCOUNT`, `CDK_DEFAULT_REGION`
- Pydantic config handles extra CDK environment variables gracefully

### Testing Strategy
- pytest with coverage reporting (HTML, XML, JSON formats)
- Markers: `unit`, `integration`, `slow`
- Coverage minimum: 80% with branch coverage
- Test structure mirrors app structure
- Integration tests use FastAPI TestClient

### CI/CD Pipeline
- GitHub Actions with containerized deployment
- Builds Docker images and pushes to ECR
- Deploys to staging on develop branch, production on main branch
- Automated rollback capabilities via Auto Scaling Group
- PR comments with deployment URLs
- Requires secrets: AWS credentials, CODECOV_TOKEN
- Uses limited IAM user for CI/CD (not admin credentials)

### AWS Deployment Notes
- CDK bootstrap requires admin access (CloudFormation:*, ECR:*, SSM:*, S3:*, IAM:*)
- After bootstrap, can use limited IAM policy for deployments
- Containerized deployment using Docker and ECR
- Auto Scaling Group provides zero-downtime deployments
- Load balancer health checks ensure traffic routing to healthy instances
- Separate staging and production environments with parameterized stacks

### Important Configuration Details
- Repository URL is automatically set from GitHub context in CI/CD
- Settings class uses `extra="ignore"` to prevent Pydantic validation errors with CDK variables
- Coverage configuration excludes test files and virtual environments
- Security groups: Load balancer (80, 443), EC2 instances (8000 from LB only, 22 for SSH)
- ECR repositories created per environment: `fastapi-staging`, `fastapi-production`
- Docker images tagged with both `latest` and commit SHA for rollback capability