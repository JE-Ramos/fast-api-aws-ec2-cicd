"""
FastAPI SaaS Infrastructure Stack

This module defines the AWS infrastructure for a production-ready SaaS application
deployment using Infrastructure as Code (IaC) principles.

Architecture Overview:
- Multi-environment support (staging/production) with parameterized configuration
- Load balancer distributing traffic across EC2 instances for high availability
- VPC with public/private subnet isolation for security
- S3 bucket for static asset storage and build artifacts
- Integrated secrets management for secure credential handling
- Auto Scaling Group for instance management and self-healing

Why this architecture:
- Addresses manual provisioning issues by providing reproducible infrastructure
- Enables staging/production parity through parameterized environments  
- Implements security best practices with least-privilege access controls
- Supports CI/CD automation with proper separation of concerns

Deployment scenarios:
- New AWS account: Requires CDK bootstrap with admin credentials first
- Existing environment: Can reuse VPC resources or create isolated environments
- Multi-region: Parameterized region configuration supports geographic distribution
"""

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_autoscaling as autoscaling,
    CfnOutput,
    Tags,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class EC2Stack(Stack):
    """
    FastAPI EC2 Infrastructure Stack
    
    Creates a complete SaaS infrastructure including:
    - VPC with public/private subnets across multiple AZs
    - Application Load Balancer with SSL termination capabilities
    - Auto Scaling Group managing EC2 instances for the FastAPI application
    - S3 bucket for static assets and deployment artifacts
    - Secrets Manager for secure credential storage
    - IAM roles with least-privilege permissions
    
    Why parameterized design:
    - Enables multiple environment deployments (dev/staging/prod) from same code
    - Supports existing AWS accounts with customizable configurations  
    - Allows resource sharing or isolation based on organizational needs
    
    How it works:
    - Load balancer receives traffic and distributes across healthy instances
    - Auto Scaling Group maintains desired capacity and replaces failed instances
    - User data script configures instances on startup with application code
    - Secrets are retrieved from AWS Secrets Manager during deployment
    - S3 bucket stores both static assets and CI/CD build artifacts
    """
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        environment_name: str,
        repository_url: str,
        instance_type: str = "t3.micro",
        min_capacity: int = 1,
        max_capacity: int = 2,
        **kwargs
    ) -> None:
        """
        Initialize EC2Stack with environment-specific configuration
        
        Args:
            environment_name: Environment identifier (staging/production)
            repository_url: GitHub repository URL for application source
            instance_type: EC2 instance type for the environment
            min_capacity: Minimum number of instances in Auto Scaling Group
            max_capacity: Maximum number of instances (enables rollback deployments)
        
        Why constructor parameters instead of CDK parameters:
        - Enables separate stack deployments per environment
        - Supports automated CI/CD without manual parameter input
        - Allows environment-specific defaults and validation
        
        How rollback works with min_capacity=1, max_capacity=2:
        - Rolling update keeps 1 instance running during deployment
        - New instance launches and is health-checked before old instance terminates
        - If new instance fails, deployment stops and old instance remains active
        """
        super().__init__(scope, construct_id, **kwargs)
        
        # Store configuration for use throughout the stack
        self.environment_name = environment_name
        self.repository_url = repository_url
        self.instance_type = instance_type
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        
        # VPC Configuration
        # Why: Isolated network environment with public/private subnet separation
        # How: Public subnets for load balancer, private subnets for EC2 instances
        # Existing account: Will create new VPC or can be modified to use existing one
        # New account: Creates complete network infrastructure from scratch
        vpc = ec2.Vpc(
            self, "FastAPIVPC",
            max_azs=2,  # Multi-AZ for high availability
            nat_gateways=1,  # Cost optimization: single NAT gateway, can increase for production
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24  # /24 provides 254 addresses per AZ
                ),
                ec2.SubnetConfiguration(
                    name="private", 
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24  # Private subnets for EC2 instances behind load balancer
                )
            ]
        )
        
        # S3 Bucket for Static Assets and Build Artifacts
        # Why: Centralizes asset storage and supports CI/CD artifact management
        # How: Versioned bucket with lifecycle policies for cost optimization
        # Existing account: Creates new bucket, can be configured to use existing one
        # New account: Provisions complete S3 storage infrastructure
        assets_bucket = s3.Bucket(
            self, "FastAPIAssetsBucket",
            versioned=True,  # Enable versioning for rollback capabilities
            public_read_access=False,  # Security: private by default
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,  # For dev environments, use RETAIN for production
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="cleanup-old-versions",
                    enabled=True,
                    noncurrent_version_expiration=Duration.days(30)  # Clean up old versions after 30 days
                )
            ]
        )
        
        # Secrets Manager for Secure Credential Storage
        # Why: Replaces plain-text secrets in config files with encrypted storage
        # How: Application retrieves secrets at runtime using IAM permissions
        # Existing account: Can integrate with existing secrets or create new ones
        # New account: Establishes secure secrets management foundation
        app_secrets = secretsmanager.Secret(
            self, "FastAPIAppSecrets",
            description=f"Application secrets for FastAPI {self.environment_name} environment",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"db_password": "", "jwt_secret": "", "api_keys": ""}',
                generate_string_key="generated_password",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
                password_length=32
            )
        )
        
        # Security Groups with Least Privilege Access
        # Why: Implements network-level security controls per AWS best practices
        # How: Separate security groups for load balancer and EC2 instances
        # Existing account: Creates new security groups, avoids conflicts with existing ones
        # New account: Establishes secure network access patterns
        
        # Load Balancer Security Group - Internet facing
        lb_security_group = ec2.SecurityGroup(
            self, "LoadBalancerSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True
        )
        
        lb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic from internet"
        )
        
        lb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS traffic from internet"
        )
        
        # EC2 Instance Security Group - Private access only
        instance_security_group = ec2.SecurityGroup(
            self, "InstanceSecurityGroup",
            vpc=vpc,
            description="Security group for FastAPI EC2 instances", 
            allow_all_outbound=True
        )
        
        # Only allow traffic from load balancer security group
        instance_security_group.add_ingress_rule(
            peer=ec2.Peer.security_group_id(lb_security_group.security_group_id),
            connection=ec2.Port.tcp(8000),
            description="Allow FastAPI traffic from load balancer only"
        )
        
        # SSH access for operational maintenance (restrict source IP in production)
        instance_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),  # TODO: Restrict to bastion host or VPN in production
            connection=ec2.Port.tcp(22),
            description="Allow SSH access for maintenance"
        )
        
        # IAM Role for EC2 Instances
        # Why: Provides secure access to AWS services without embedding credentials
        # How: Instance profile attached to EC2 instances with least-privilege permissions
        # Existing account: Creates new role, can reference existing policies
        # New account: Establishes secure service-to-service authentication
        role = iam.Role(
            self, "FastAPIEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
            ]
        )
        
        # Grant access to Secrets Manager for runtime secret retrieval
        app_secrets.grant_read(role)
        
        # Grant access to S3 bucket for static assets and artifacts
        assets_bucket.grant_read_write(role)
        
        # Application Load Balancer
        # Why: Distributes traffic across multiple instances for high availability
        # How: Internet-facing ALB in public subnets routes to private EC2 instances
        # Existing account: Creates new ALB, can integrate with existing DNS
        # New account: Provides production-ready load balancing from start
        load_balancer = elbv2.ApplicationLoadBalancer(
            self, "FastAPILoadBalancer",
            vpc=vpc,
            internet_facing=True,
            security_group=lb_security_group,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
        
        # Target Group for Health Checks and Traffic Routing
        # Why: Enables health-based routing and supports rolling deployments
        # How: Health checks ensure only healthy instances receive traffic
        target_group = elbv2.ApplicationTargetGroup(
            self, "FastAPITargetGroup",
            vpc=vpc,
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                path="/health",
                protocol=elbv2.Protocol.HTTP,
                port="8000",
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
                timeout=Duration.seconds(5),
                interval=Duration.seconds(30)
            )
        )
        
        # Load Balancer Listener
        # Why: Defines how incoming requests are processed and routed
        # How: HTTP listener forwards to target group, can be extended for HTTPS
        listener = load_balancer.add_listener(
            "HTTPListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group]
        )
        
        # User Data Script for Instance Configuration
        # Why: Automates application deployment and configuration on instance startup
        # How: Shell script installs dependencies, clones code, and starts application
        # Existing account: Works with existing or new instances
        # New account: Provides complete application bootstrap process
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            # System updates and dependencies
            "yum update -y",
            "yum install -y python3 python3-pip git aws-cli",
            "pip3 install --upgrade pip",
            
            # Application deployment
            "cd /home/ec2-user",
            f"git clone {self.repository_url} app",
            "cd app",
            "pip3 install -r app/requirements.txt",
            
            # Configure application to use AWS services
            f"aws secretsmanager get-secret-value --secret-id {app_secrets.secret_arn} --region {self.region} --query SecretString --output text > /tmp/secrets.json",
            
            # Start application as systemd service for reliability
            "cat > /etc/systemd/system/fastapi.service << 'EOF'",
            "[Unit]",
            "Description=FastAPI application",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            "User=ec2-user",
            "WorkingDirectory=/home/ec2-user/app",
            "ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000",
            "Restart=always",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "systemctl enable fastapi",
            "systemctl start fastapi"
        )
        
        # Launch Template for Auto Scaling Group
        # Why: Defines instance configuration for consistent deployments
        # How: Template used by ASG to launch identical instances
        launch_template = ec2.LaunchTemplate(
            self, "FastAPILaunchTemplate",
            instance_type=ec2.InstanceType(self.instance_type),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023
            ),
            security_group=instance_security_group,
            role=role,
            user_data=user_data
        )
        
        # Auto Scaling Group for High Availability and Self-Healing
        # Why: Maintains desired capacity and replaces failed instances automatically
        # How: Monitors instance health and scales based on demand
        # Existing account: Creates new ASG, can integrate with existing monitoring
        # New account: Provides production-ready scaling and resilience
        auto_scaling_group = autoscaling.AutoScalingGroup(
            self, "FastAPIAutoScalingGroup",
            vpc=vpc,
            launch_template=launch_template,
            min_capacity=self.min_capacity,
            max_capacity=self.max_capacity,
            desired_capacity=self.min_capacity,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS  # Instances in private subnets
            ),
            health_check=autoscaling.HealthCheck.elb(grace=Duration.seconds(300)),  # Use load balancer health checks
            update_policy=autoscaling.UpdatePolicy.rolling_update(
                min_instances_in_service=1,  # Ensure zero-downtime deployments
                max_batch_size=1,
                pause_time=Duration.minutes(5)  # Wait 5 minutes between instance replacements
            )
        )
        
        # Attach Auto Scaling Group to Load Balancer Target Group
        # Why: Enables automatic registration/deregistration of instances
        # How: ASG manages target group membership based on instance lifecycle
        auto_scaling_group.attach_to_application_target_group(target_group)
        
        # Resource Tagging for Environment Management
        # Why: Enables cost tracking and resource management across environments
        # How: Consistent tagging strategy across all resources
        Tags.of(self).add("Environment", self.environment_name)
        Tags.of(self).add("Project", "FastAPI-SaaS")
        Tags.of(self).add("ManagedBy", "CDK")
        
        # Stack Outputs for Integration and Monitoring
        # Why: Provides essential information for CI/CD and operational tasks
        # How: CloudFormation outputs accessible via AWS CLI or console
        CfnOutput(
            self, "LoadBalancerDNS",
            value=load_balancer.load_balancer_dns_name,
            description="Load Balancer DNS name for application access"
        )
        
        CfnOutput(
            self, "LoadBalancerHostedZone",
            value=load_balancer.load_balancer_canonical_hosted_zone_id,
            description="Load Balancer hosted zone for Route53 alias records"
        )
        
        CfnOutput(
            self, "S3BucketName",
            value=assets_bucket.bucket_name,
            description="S3 bucket name for static assets and build artifacts"
        )
        
        CfnOutput(
            self, "SecretsManagerArn", 
            value=app_secrets.secret_arn,
            description="Secrets Manager ARN for application secrets"
        )
        
        CfnOutput(
            self, "VPCId",
            value=vpc.vpc_id,
            description="VPC ID for network integration"
        )