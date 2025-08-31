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

## Deployment

### Deploy with AWS CDK

1. Bootstrap CDK (first time only):
```bash
cd infra
cdk bootstrap
```

2. Deploy the stack:
```bash
cdk deploy FastAPIEC2Stack
```

3. The deployment will output the EC2 instance's public IP address.

### Manual EC2 Deployment

1. SSH into your EC2 instance
2. Clone your repository
3. Install dependencies
4. Run the application with systemd or supervisor

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