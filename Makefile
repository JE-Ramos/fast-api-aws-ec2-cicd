.PHONY: help install run test lint deploy clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make run        - Run FastAPI locally"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make deploy     - Deploy to AWS"
	@echo "  make clean      - Clean up generated files"

install:
	pip install -r app/requirements.txt
	pip install -r infra/requirements.txt
	pip install pytest pytest-cov flake8 black

run:
	cd app && uvicorn main:app --reload --port 8000

test:
	pytest

test-verbose:
	pytest -v

test-coverage:
	pytest --cov-report=html && open htmlcov/index.html

lint:
	flake8 app --max-line-length=127
	black app --check

format:
	black app

docker-build:
	docker build -t fastapi-aws-app .

docker-run:
	docker-compose up

cdk-synth:
	cd infra && cdk synth

cdk-deploy:
	cd infra && cdk deploy FastAPIEC2Stack

cdk-destroy:
	cd infra && cdk destroy FastAPIEC2Stack

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf cdk.out