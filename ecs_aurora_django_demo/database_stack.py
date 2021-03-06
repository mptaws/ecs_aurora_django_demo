from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_logs as logs
)
from constructs import Construct


class DatabaseStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            vpc: ec2.Vpc,
            database_name: str,
            min_capacity: rds.AuroraCapacityUnit = rds.AuroraCapacityUnit.ACU_2,
            max_capacity: rds.AuroraCapacityUnit = rds.AuroraCapacityUnit.ACU_4,
            auto_pause_minutes: int = 30,
            backup_retention_days: int = 1,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = vpc
        self.database_name = database_name
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        self.auto_pause_minutes = auto_pause_minutes
        self.backup_retention_days = backup_retention_days

        self.log_group = logs.LogGroup(
            self,
            "ECSDatabaseLogGroup",
            log_group_name=f"ECSDatabaseLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_DAY
        )

        self.aurora_serverless_db = rds.ServerlessCluster(
            self,
            "AuroraServerlessCluster",
            engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            default_database_name=self.database_name,
            backup_retention=Duration.days(
                self.backup_retention_days),  # 1 day retention is free
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,

            # Allow running queries in AWS console (free)
            enable_data_api=True,

            parameter_group=rds.ParameterGroup.from_parameter_group_name(  # Specify the mysql version
                self,
                "AuroraDBParameterGroup",
                "default.aurora-mysql5.7"
            ),
            scaling=rds.ServerlessScalingOptions(
                # Shutdown after minutes of inactivity to save costs
                auto_pause=Duration.minutes(self.auto_pause_minutes),
                min_capacity=self.min_capacity,
                max_capacity=self.max_capacity
            )
        )
        # Allow ingress traffic from ECS tasks
        self.aurora_serverless_db.connections.allow_default_port_from_any_ipv4(
            description="Services in private subnets can access the DB"
        )
