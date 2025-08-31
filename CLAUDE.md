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
- `cd infra && cdk deploy FastAPIEC2Stack` - Deploy infrastructure
- `cd infra && cdk destroy FastAPIEC2Stack` - Destroy infrastructure
- `make cdk-synth`, `make cdk-deploy`, `make cdk-destroy` - CDK commands via Makefile

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
- **app.py** - CDK app entry point, loads environment from `.env`
- **stacks/ec2_stack.py** - Main infrastructure stack
  - Creates VPC with public/private subnets
  - EC2 instance with security groups (ports 22, 80, 8000)
  - IAM role with SSM and CloudWatch permissions
  - User data script for automatic app deployment
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
- GitHub Actions with test and deploy jobs
- Requires secrets: AWS credentials, EC2 SSH details, CODECOV_TOKEN
- Automated deployment on main branch push
- Uses limited IAM user for CI/CD (not admin credentials)

### AWS Deployment Notes
- CDK bootstrap requires admin access (CloudFormation:*, ECR:*, SSM:*, S3:*, IAM:*)
- After bootstrap, can use limited IAM policy for deployments
- EC2 instance auto-configures via user data script
- Update repository URL in `ec2_stack.py:73` before deployment

### Important Configuration Details
- Repository URL must be updated in `infra/stacks/ec2_stack.py` line 73
- Settings class uses `extra="ignore"` to prevent Pydantic validation errors with CDK variables
- Coverage configuration excludes test files and virtual environments
- Security groups allow HTTP (80), FastAPI (8000), and SSH (22) access