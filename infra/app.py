#!/usr/bin/env python3
"""
FastAPI SaaS Multi-Environment CDK Application with Blue-Green Deployment

This CDK app deploys three separate environments to support proper blue-green
deployment pattern as required by the SaaS infrastructure modernization project.

Why three environments:
- Staging: For develop branch continuous integration testing
- Production-Blue: For release branch testing in production-like environment
- Production-Green: Live production environment from main branch
- Prevents staging deployments from interfering with release testing

How blue-green deployment works:
1. Develop branch → Staging (continuous testing)
2. Release branch → Production-Blue (isolated production testing)
3. Main branch → Production-Green (live traffic after approval)
4. Blue and Green can be swapped for zero-downtime deployments

Satisfies tasks.md requirements:
- ✅ Staging deployment on develop merge (line 39)
- ✅ Production deployment on approved main release (line 40)
- ✅ Separate EC2 instances for staging and production (line 30)
- ✅ Rollback capabilities via Auto Scaling Groups
- ✅ Load balancers for each environment

Existing vs New account:
- Existing account: Can deploy to existing VPCs or create new isolated environments
- New account: Creates complete infrastructure foundation for all three environments
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
# Branch: develop
# Purpose: Continuous integration testing for develop branch
staging_stack = EC2Stack(
    app,
    "FastAPIEC2Stack-Staging",
    env=env,
    environment_name="staging",
    repository_url=repository_url,
    instance_type="t3.micro",  # Cost optimization for staging
    min_capacity=1,
    max_capacity=2,  # Allows rollback deployments
    description="FastAPI staging environment for develop branch testing"
)

# Production-Blue Environment Stack (Pre-Production)
# Branch: release/*
# Purpose: Isolated production testing for release branches
# This prevents staging deployments from interfering with release testing
production_blue_stack = EC2Stack(
    app,
    "FastAPIEC2Stack-ProductionBlue", 
    env=env,
    environment_name="production-blue",
    repository_url=repository_url,
    instance_type="t3.small",  # Production-grade performance
    min_capacity=1,
    max_capacity=2,  # Allows rollback deployments
    description="FastAPI production-blue environment for release testing"
)

# Production-Green Environment Stack (Live Production)
# Branch: main  
# Purpose: Live production traffic after approved release
production_green_stack = EC2Stack(
    app,
    "FastAPIEC2Stack-ProductionGreen", 
    env=env,
    environment_name="production-green",
    repository_url=repository_url,
    instance_type="t3.small",  # Production-grade performance
    min_capacity=2,  # Higher minimum for production availability
    max_capacity=3,  # Higher maximum for production scaling
    description="FastAPI production-green environment for live traffic"
)

app.synth()