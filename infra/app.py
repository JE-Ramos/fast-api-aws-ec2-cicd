#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from stacks.ec2_stack import EC2Stack
from dotenv import load_dotenv

load_dotenv()

app = App()

env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1")
)

EC2Stack(
    app, 
    "FastAPIEC2Stack",
    env=env,
    description="FastAPI application running on EC2 with CI/CD"
)

app.synth()