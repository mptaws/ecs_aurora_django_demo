import uuid
from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs
)
from constructs import Construct


class ECSStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        database_secrets: secretsmanager.ISecret,
        ecs_cluster: ecs.Cluster,
        task_cpu: int = 256,
        task_memory_mib: int = 1024,
        task_desired_count: int = 2,
        task_min_scaling_capacity: int = 2,
        task_max_scaling_capacity: int = 4,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.vpc = vpc
        self.database_secrets = database_secrets
        self.ecs_cluster = ecs_cluster
        self.task_cpu = task_cpu
        self.task_memory_mib = task_memory_mib
        self.task_desired_count = task_desired_count
        self.task_min_scaling_capacity = task_min_scaling_capacity
        self.task_max_scaling_capacity = task_max_scaling_capacity

        # Prepare parameters

        uid = uuid.uuid4().hex[:6].upper()
        self.container_name = f"django_app"
        self.unique_secret_name = "DjangoSecretAppKey"+uid

        self.newKey = secretsmanager.Secret(
            self,
            "DjangoSecretAppKey",
            secret_name=self.unique_secret_name,
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template="{}", generate_string_key="SecretKey", exclude_punctuation=True
            )
        )

        self.secretKey = secretsmanager.Secret.from_secret_name_v2(
            self, "DjangoKeySecret", secret_name=self.unique_secret_name)

        # Set the secrets in the container as environment variables
        self.app_secrets = {
            "SECRET_KEY": ecs.Secret.from_secrets_manager(self.secretKey, field="SecretKey"),
            "HOST": ecs.Secret.from_secrets_manager(
                database_secrets,
                field="host"
            ),
            "PORT": ecs.Secret.from_secrets_manager(
                database_secrets,
                field="port"
            ),
            "DB_NAME": ecs.Secret.from_secrets_manager(
                database_secrets,
                field="dbname"
            ),
            "USERNAME": ecs.Secret.from_secrets_manager(
                database_secrets,
                field="username"
            ),
            "PASSWORD": ecs.Secret.from_secrets_manager(
                database_secrets,
                field="password"
            )
        }

        # Create Log Group for Cluster
        self.log_group = logs.LogGroup(
            self,
            "ECSLogGroup",
            log_group_name=f"ECSLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_DAY
        )

        # Create the load balancer, ECS service and fargate task for teh Django App
        self.alb_fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "DjangoToDoApp",
            protocol=elbv2.ApplicationProtocol.HTTP,
            redirect_http=False,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            cluster=self.ecs_cluster,  # Required
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            cpu=self.task_cpu,  # Default is 256
            memory_limit_mib=self.task_memory_mib,  # Default is 512
            desired_count=self.task_desired_count,  # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(
                    directory="app/",
                    file="Dockerfile"
                ),
                container_name=self.container_name,
                container_port=8000,
                secrets=self.app_secrets,
                log_driver=ecs.LogDriver.aws_logs(
                    log_group=self.log_group,
                    stream_prefix=f"DjangoToDoApp",
                )
            ),
            public_load_balancer=True
        )
        # Set the health checks settings
        self.alb_fargate_service.target_group.configure_health_check(
            path="/health_check/",
            healthy_threshold_count=3,
            unhealthy_threshold_count=2
        )
        # Autoscaling based on CPU utilization
        scalable_target = self.alb_fargate_service.service.auto_scale_task_count(
            min_capacity=self.task_min_scaling_capacity,
            max_capacity=self.task_max_scaling_capacity
        )
        scalable_target.scale_on_cpu_utilization(
            f"CpuScaling",
            target_utilization_percent=75,
        )
