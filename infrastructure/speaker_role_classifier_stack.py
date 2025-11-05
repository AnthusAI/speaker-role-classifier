"""CDK Stack for Speaker Role Classifier Lambda function."""

from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    BundlingOptions,
    aws_lambda as lambda_,
    aws_logs as logs,
)
from constructs import Construct
import os


class SpeakerRoleClassifierStack(Stack):
    """Stack for deploying the Speaker Role Classifier as a Lambda function with Function URL."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch log group
        log_group = logs.LogGroup(
            self,
            "ClassifierFunctionLogGroup",
            retention=logs.RetentionDays.ONE_WEEK,
        )
        
        # Create the Lambda function
        classifier_function = lambda_.Function(
            self,
            "ClassifierFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                "../",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        " && ".join([
                            "pip install --no-cache-dir --platform manylinux2014_x86_64 --only-binary=:all: -r requirements.txt -t /asset-output",
                            "pip install --no-cache-dir . -t /asset-output",
                            "cp -r lambda_handler/* /asset-output/",
                        ])
                    ],
                )
            ),
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
            },
            log_group=log_group,
            description="Classifies speakers in call center transcripts as Agent or Customer using GPT-5",
        )

        # Create Function URL (simplest way to expose as HTTP endpoint)
        function_url = classifier_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,  # Public access - change to AWS_IAM for auth
            cors=lambda_.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[lambda_.HttpMethod.POST],
                allowed_headers=["Content-Type"],
            )
        )

        # Output the Function URL
        CfnOutput(
            self,
            "FunctionUrl",
            value=function_url.url,
            description="HTTP endpoint for the Speaker Role Classifier"
        )

        CfnOutput(
            self,
            "FunctionName",
            value=classifier_function.function_name,
            description="Lambda function name"
        )

