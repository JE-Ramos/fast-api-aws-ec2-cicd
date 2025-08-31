#!/usr/bin/env python3
"""
FastAPI SaaS Multi-Environment CDK Application

This CDK app deploys separate staging and production environments as required
by the SaaS infrastructure modernization project.

Why separate stacks:
- Enables independent staging and production deployments per tasks.md requirements
- Provides environment isolation and separate secret management
- Supports CI/CD workflow: develop→staging, main→production with approvals
- Allows separate rollback capabilities per environment

How it works:
- Two identical infrastructure stacks with environment-specific configuration
- Staging: Deploys automatically on develop branch merge
- Production: Deploys with manual approval on main branch release
- Each environment has Auto Scaling Group for rollback capabilities (Min: 1, Max: 2)

Existing vs New account:
- Existing account: Can deploy to existing VPCs or create new isolated environments
- New account: Creates complete infrastructure foundation for both environments
"""

import os
from aws_cdk import App, Environment
from stacks.ec2_stack import EC2Stack
from dotenv import load_dotenv

load_dotenv()

app = App()

# AWS Environment Configuration
env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1")
)

# Get repository URL from environment or use default
repository_url = os.getenv("REPOSITORY_URL", "https://github.com/YOUR_USERNAME/YOUR_REPO.git")

# Staging Environment Stack
# Why: Automatic deployment target for develop branch merges
# How: Isolated environment for testing changes before production
staging_stack = EC2Stack(
    app,
    "FastAPIEC2Stack-Staging",
    env=env,
    environment_name="staging",
    repository_url=repository_url,
    instance_type="t3.micro",  # Cost optimization for staging
    min_capacity=1,
    max_capacity=2,  # Allows rollback deployments
    description="FastAPI staging environment with rollback capabilities"
)

# Production Environment Stack  
# Why: Manual approval deployment target for main branch releases
# How: Production-grade configuration with higher capacity and monitoring
production_stack = EC2Stack(
    app,
    "FastAPIEC2Stack-Production", 
    env=env,
    environment_name="production",
    repository_url=repository_url,
    instance_type="t3.small",  # Better performance for production load
    min_capacity=1,
    max_capacity=2,  # Allows rollback deployments
    description="FastAPI production environment with rollback capabilities"
)

app.synth()