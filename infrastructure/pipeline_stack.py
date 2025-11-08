"""CDK Stack for CI/CD Pipeline using CodePipeline."""

from aws_cdk import (
    Stack,
    SecretValue,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class PipelineStack(Stack):
    """Stack for CI/CD Pipeline that builds and deploys the Lambda function."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # GitHub source configuration
        # You'll need to store your GitHub token in AWS Secrets Manager
        github_token = SecretValue.secrets_manager(
            "github-token",
            json_field="token"
        )

        # Create artifacts
        source_output = codepipeline.Artifact("SourceOutput")
        build_output = codepipeline.Artifact("BuildOutput")

        # Create CodeBuild project for building (no tests - validation done in GitHub Actions)
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            project_name="SpeakerRoleClassifierBuild",
            description="Build Speaker Role Classifier Lambda package (no tests)",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=False,
            ),
            environment_variables={
                "OPENAI_API_KEY": codebuild.BuildEnvironmentVariable(
                    type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                    value="openai-api-key:OPENAI_API_KEY"
                ),
            },
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.11",
                        },
                        "commands": [
                            "echo Installing production dependencies only...",
                            "pip install --upgrade pip",
                            "pip install -e .",  # No [dev] - production dependencies only
                        ],
                    },
                    "build": {
                        "commands": [
                            "echo Build started on `date`",
                            "echo Building Lambda deployment package...",
                            "echo All validation (tests, security) completed in GitHub Actions",
                            "echo This stage only packages for deployment",
                            "echo Build completed successfully",
                        ],
                    },
                },
                "artifacts": {
                    "files": [
                        "**/*",
                    ],
                },
            }),
        )

        # Create CodeBuild project for CDK deployment
        deploy_project = codebuild.PipelineProject(
            self,
            "DeployProject",
            project_name="SpeakerRoleClassifierDeploy",
            description="Deploy Speaker Role Classifier using CDK",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=False,
            ),
            environment_variables={
                "OPENAI_API_KEY": codebuild.BuildEnvironmentVariable(
                    type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                    value="openai-api-key:OPENAI_API_KEY"
                ),
            },
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.11",
                            "nodejs": "18",
                        },
                        "commands": [
                            "echo Installing CDK and dependencies...",
                            "npm install -g aws-cdk",
                            "cd infrastructure",
                            "pip install -r requirements.txt",
                        ],
                    },
                    "build": {
                        "commands": [
                            "echo Deploying with CDK...",
                            "cdk deploy SpeakerRoleClassifierStack --require-approval never",
                        ],
                    },
                },
            }),
        )

        # Grant deploy project permissions to deploy CDK stacks
        deploy_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:*",
                    "lambda:*",
                    "logs:*",
                    "iam:*",
                    "s3:*",
                    "ecr:*",
                    "ssm:GetParameter",  # Required for CDK bootstrap version check
                    "sts:AssumeRole",     # Required to assume CDK deployment roles
                ],
                resources=["*"],
            )
        )

        # Create the pipeline
        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name="SpeakerRoleClassifierPipeline",
            restart_execution_on_update=True,
        )

        # Add source stage
        # NOTE: Webhook trigger is DISABLED - pipeline only runs when triggered by GitHub Actions
        # This ensures version is bumped and validated BEFORE deployment
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="AnthusAI",
            repo="speaker-role-classifier",
            branch="main",
            oauth_token=github_token,
            output=source_output,
            trigger=codepipeline_actions.GitHubTrigger.NONE,  # Disabled - manual trigger only
        )

        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action],
        )

        # Add build stage (no tests - validation done in GitHub Actions)
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build_Package",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action],
        )

        # Add deploy stage
        deploy_action = codepipeline_actions.CodeBuildAction(
            action_name="Deploy_Lambda",
            project=deploy_project,
            input=build_output,
        )

        pipeline.add_stage(
            stage_name="Deploy",
            actions=[deploy_action],
        )
