#!/usr/bin/env python3
"""
AWS Secrets Manager CLI for managing application and deployment secrets.

Usage:
    python scripts/manage_secrets.py --help
    python scripts/manage_secrets.py get-app-secret jwt_secret
    python scripts/manage_secrets.py set-app-secret jwt_secret "my-secret-value"
    python scripts/manage_secrets.py get-deployment-secret ec2_host
    python scripts/manage_secrets.py set-deployment-secret ec2_key_name "my-key-pair"
"""

import argparse
import json
import sys
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError


class SecretsManagerCLI:
    """Command-line interface for AWS Secrets Manager."""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize the CLI with AWS region."""
        self.client = boto3.client("secretsmanager", region_name=region)
        self.app_secret_name = "FastAPIAppSecrets"
        self.deployment_secret_name = "FastAPIDeploymentSecrets"
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve a secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response["SecretString"])
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"Secret {secret_name} not found")
                return {}
            raise
    
    def update_secret(self, secret_name: str, secret_dict: Dict[str, Any]):
        """Update a secret in AWS Secrets Manager."""
        try:
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_dict)
            )
            print(f"Successfully updated secret: {secret_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Create the secret if it doesn't exist
                self.client.create_secret(
                    Name=secret_name,
                    SecretString=json.dumps(secret_dict)
                )
                print(f"Successfully created secret: {secret_name}")
            else:
                raise
    
    def get_app_secret(self, key: str):
        """Get a specific key from application secrets."""
        secrets = self.get_secret(self.app_secret_name)
        value = secrets.get(key)
        if value:
            print(f"{key}: {value}")
        else:
            print(f"Key '{key}' not found in application secrets")
        return value
    
    def set_app_secret(self, key: str, value: str):
        """Set a specific key in application secrets."""
        secrets = self.get_secret(self.app_secret_name)
        secrets[key] = value
        self.update_secret(self.app_secret_name, secrets)
        print(f"Set {key} in application secrets")
    
    def get_deployment_secret(self, key: str):
        """Get a specific key from deployment secrets."""
        secrets = self.get_secret(self.deployment_secret_name)
        value = secrets.get(key)
        if value:
            print(f"{key}: {value}")
        else:
            print(f"Key '{key}' not found in deployment secrets")
        return value
    
    def set_deployment_secret(self, key: str, value: str):
        """Set a specific key in deployment secrets."""
        secrets = self.get_secret(self.deployment_secret_name)
        secrets[key] = value
        self.update_secret(self.deployment_secret_name, secrets)
        print(f"Set {key} in deployment secrets")
    
    def list_secrets(self):
        """List all secrets and their keys."""
        print("\n=== Application Secrets ===")
        app_secrets = self.get_secret(self.app_secret_name)
        for key in app_secrets:
            print(f"  - {key}")
        
        print("\n=== Deployment Secrets ===")
        deployment_secrets = self.get_secret(self.deployment_secret_name)
        for key in deployment_secrets:
            print(f"  - {key}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage AWS Secrets Manager secrets")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List secrets command
    subparsers.add_parser("list", help="List all secrets and their keys")
    
    # Get app secret
    get_app = subparsers.add_parser("get-app-secret", help="Get application secret value")
    get_app.add_argument("key", help="Secret key to retrieve")
    
    # Set app secret
    set_app = subparsers.add_parser("set-app-secret", help="Set application secret value")
    set_app.add_argument("key", help="Secret key to set")
    set_app.add_argument("value", help="Secret value to set")
    
    # Get deployment secret
    get_deploy = subparsers.add_parser("get-deployment-secret", help="Get deployment secret value")
    get_deploy.add_argument("key", help="Secret key to retrieve")
    
    # Set deployment secret
    set_deploy = subparsers.add_parser("set-deployment-secret", help="Set deployment secret value")
    set_deploy.add_argument("key", help="Secret key to set")
    set_deploy.add_argument("value", help="Secret value to set")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SecretsManagerCLI(region=args.region)
    
    try:
        if args.command == "list":
            cli.list_secrets()
        elif args.command == "get-app-secret":
            cli.get_app_secret(args.key)
        elif args.command == "set-app-secret":
            cli.set_app_secret(args.key, args.value)
        elif args.command == "get-deployment-secret":
            cli.get_deployment_secret(args.key)
        elif args.command == "set-deployment-secret":
            cli.set_deployment_secret(args.key, args.value)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()