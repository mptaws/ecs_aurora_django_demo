from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
)
from constructs import Construct


class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,  # default is all AZs in region
            nat_gateways=0,
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        self.ecs_cluster = ecs.Cluster(self, f"ECSCluster", vpc=self.vpc)

        # Create a security group for our endpoints
        security_group = ec2.SecurityGroup(
            self, "ECR-SG",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        # Needed to pull container image to ECR
        self.s3_private_link = ec2.GatewayVpcEndpoint(
            self,
            "S3GWEndpoint",
            vpc=self.vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        self.ecr_api_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "ECRapiEndpoint",
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            open=True,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )
        self.ecr_dkr_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "ECRdkrEndpoint",
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            open=True,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )
        self.secrets_manager_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "SecretsManagerEndpoint",
            vpc=self.vpc,
            security_groups=[security_group],
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            open=True,
            private_dns_enabled=True
        )

        # Needed for  health metrics to connect to Cloudwatch in private subnet
        self.cloudwatch_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "CloudWatchEndpoint",
            vpc=self.vpc,
            security_groups=[security_group],
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            open=True,
            private_dns_enabled=True
        )
