from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_ecs as ecs,
)
from constructs import Construct


class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Our network in the cloud
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,  # default is all AZs in region
            nat_gateways=0,
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        self.ecs_cluster = ecs.Cluster(self, f"ECSCluster", vpc=self.vpc)

        self.s3_private_link = ec2.GatewayVpcEndpoint(
            self,
            "S3GWEndpoint",
            vpc=self.vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        # Create a security group for our endpoints
        security_group = ec2.SecurityGroup(
            self, "ECR-SG",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        # Allow 443 inbound on our Security Group
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.tcp(443)
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
        self.cloudwatch_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "CloudWatchEndpoint",
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            open=True,
            private_dns_enabled=True
        )
        self.secrets_manager_private_link = ec2.InterfaceVpcEndpoint(
            self,
            "SecretsManagerEndpoint",
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            open=True,
            private_dns_enabled=True
        )

        # Save useful info in SSM for later usage
        ssm.StringParameter(
            self,
            "VpcIdParam",
            parameter_name=f"VpcId",
            string_value=self.vpc.vpc_id
        )
        self.task_subnets = ssm.StringListParameter(
            self,
            "VpcPrivateSubnetsParam",
            parameter_name=f"VpcPrivateSubnetsParam",
            string_list_value=[
                s.subnet_id
                for s in self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnets
            ]
        )
