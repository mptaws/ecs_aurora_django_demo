from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class ExternalSecretsStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            database_secrets: secretsmanager.ISecret,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Secret values required by the app which are store in the Secrets Manager
        # This values will be injected as env vars on runtime
        self.app_secrets = {
            "SECRET_KEY": ecs.Secret.from_secrets_manager(
                secretsmanager.Secret.from_secret_name_v2(
                    self,
                    f"DjangoKeySecret",
                    secret_name=f"DjangoSecretKey"
                )
            ),
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
            ),
            "AWS_ACCESS_KEY_ID": ecs.Secret.from_secrets_manager(
                secretsmanager.Secret.from_secret_name_v2(
                    self,
                    f"AWSAccessKeyIDSecret",
                    secret_name=f"AwsApiKeyId"
                )
            ),
            "AWS_SECRET_ACCESS_KEY": ecs.Secret.from_secrets_manager(
                secretsmanager.Secret.from_secret_name_v2(
                    self,
                    f"AWSAccessKeySecretSecret",
                    secret_name=f"AwsApiKeySecret",
                )
            ),
        }