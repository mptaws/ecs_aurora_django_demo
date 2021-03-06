#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    Environment,
    aws_rds as rds
)
from ecs_aurora_django_demo.network_stack import NetworkStack
from ecs_aurora_django_demo.database_stack import DatabaseStack
from ecs_aurora_django_demo.ecs_stack import ECSStack


app = cdk.App()

aws_env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

vpc = NetworkStack(
    app,
    "Network",
    env=aws_env,
)

database = DatabaseStack(
    app,
    "Database",
    env=aws_env,
    vpc=vpc.vpc,
    database_name="app_db",
    min_capacity=rds.AuroraCapacityUnit.ACU_1,
    max_capacity=rds.AuroraCapacityUnit.ACU_2,
    auto_pause_minutes=60,
)

ECSStack(
    app,
    "AppService",
    env=aws_env,
    vpc=vpc,
    database_secrets=database.aurora_serverless_db.secret,
    ecs_cluster=vpc.ecs_cluster,
    task_cpu=256,
    task_memory_mib=512,
    task_desired_count=2,
    task_min_scaling_capacity=1,
    task_max_scaling_capacity=2,
)

app.synth()
