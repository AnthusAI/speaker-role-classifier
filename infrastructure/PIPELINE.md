# CI/CD Pipeline Setup Guide

This guide explains how to set up and use the AWS CodePipeline CI/CD pipeline for automated testing and deployment of the Speaker Role Classifier Lambda function.

## Architecture

The pipeline consists of three stages:

1. **Source Stage**: Pulls code from GitHub when changes are pushed to the `main` branch
2. **Build Stage**: Runs tests using pytest to ensure code quality
3. **Deploy Stage**: Deploys the Lambda function using AWS CDK

```
GitHub → CodePipeline → CodeBuild (Test) → CodeBuild (Deploy) → Lambda
```

## Prerequisites

Before deploying the pipeline, you need:

1. **AWS Account** with appropriate permissions
2. **GitHub Personal Access Token** with `repo` and `admin:repo_hook` permissions
3. **OpenAI API Key** for the Lambda function

## Setup Instructions

### Step 1: Store Secrets in AWS Secrets Manager

The pipeline requires two secrets to be stored in AWS Secrets Manager:

#### 1. GitHub Token

Create a GitHub Personal Access Token:
- Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Click "Generate new token (classic)"
- Select scopes: `repo` and `admin:repo_hook`
- Copy the token

Store it in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name github-token \
    --description "GitHub token for CodePipeline" \
    --secret-string '{"token":"your-github-token-here"}'
```

#### 2. OpenAI API Key

Store your OpenAI API key:

```bash
aws secretsmanager create-secret \
    --name openai-api-key \
    --description "OpenAI API key for Speaker Role Classifier" \
    --secret-string '{"OPENAI_API_KEY":"your-openai-api-key-here"}'
```

### Step 2: Deploy the Pipeline Stack

```bash
cd infrastructure

# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (if not already done)
cdk bootstrap

# Deploy the pipeline stack
cdk deploy SpeakerRoleClassifierPipelineStack
```

The deployment will create:
- CodePipeline pipeline
- Two CodeBuild projects (Build and Deploy)
- IAM roles and policies
- GitHub webhook for automatic triggers

### Step 3: Verify the Pipeline

After deployment:

1. Go to the AWS CodePipeline console
2. Find the "SpeakerRoleClassifierPipeline"
3. The pipeline should automatically trigger and run through all stages
4. Verify each stage completes successfully

## Pipeline Behavior

### Automatic Triggers

The pipeline automatically triggers when:
- Code is pushed to the `main` branch
- A pull request is merged to `main`

### Build Stage

The Build stage:
1. Installs Python 3.11 and dependencies
2. Runs the full test suite with pytest
3. Fails the pipeline if any tests fail
4. Produces build artifacts for the next stage

### Deploy Stage

The Deploy stage:
1. Installs AWS CDK
2. Runs `cdk deploy` to update the Lambda function
3. Uses the OpenAI API key from Secrets Manager
4. Updates the Lambda function with the latest code

## Monitoring and Troubleshooting

### View Pipeline Execution

```bash
# List recent pipeline executions
aws codepipeline list-pipeline-executions \
    --pipeline-name SpeakerRoleClassifierPipeline

# Get execution details
aws codepipeline get-pipeline-execution \
    --pipeline-name SpeakerRoleClassifierPipeline \
    --pipeline-execution-id <execution-id>
```

### View Build Logs

1. Go to AWS CodeBuild console
2. Select the build project (Build or Deploy)
3. Click on a build run to view logs
4. Or use CloudWatch Logs to view detailed logs

### Common Issues

#### Pipeline Fails at Source Stage

**Issue**: Cannot access GitHub repository

**Solution**: 
- Verify GitHub token has correct permissions
- Check that the token is stored correctly in Secrets Manager
- Ensure the repository name and owner are correct in `pipeline_stack.py`

#### Pipeline Fails at Build Stage

**Issue**: Tests fail

**Solution**:
- Run tests locally first: `pytest tests/ -v`
- Check test output in CodeBuild logs
- Fix failing tests and push changes

#### Pipeline Fails at Deploy Stage

**Issue**: CDK deployment fails

**Solution**:
- Check CodeBuild logs for specific error
- Verify IAM permissions for the deploy project
- Ensure OpenAI API key is correctly stored in Secrets Manager
- Try deploying manually: `cd infrastructure && cdk deploy`

## Manual Pipeline Execution

To manually trigger the pipeline:

```bash
aws codepipeline start-pipeline-execution \
    --name SpeakerRoleClassifierPipeline
```

Or use the AWS Console:
1. Go to CodePipeline
2. Select "SpeakerRoleClassifierPipeline"
3. Click "Release change"

## Updating the Pipeline

To update the pipeline configuration:

1. Modify `infrastructure/pipeline_stack.py`
2. Deploy the changes:
   ```bash
   cd infrastructure
   cdk deploy SpeakerRoleClassifierPipelineStack
   ```

The pipeline will automatically update and restart.

## Cost Considerations

The pipeline incurs costs for:
- **CodePipeline**: $1/month per active pipeline
- **CodeBuild**: $0.005/build minute (Small instance)
- **CloudWatch Logs**: Storage and data transfer
- **Lambda**: Execution time and requests

Estimated monthly cost for typical usage: $5-10

## Security Best Practices

1. **Secrets Management**: All sensitive data is stored in AWS Secrets Manager
2. **IAM Roles**: Pipeline uses least-privilege IAM roles
3. **GitHub Token**: Use a token with minimal required scopes
4. **Branch Protection**: Consider enabling branch protection on `main`
5. **Code Review**: Require PR reviews before merging to `main`

## Advanced Configuration

### Adding Manual Approval

To add a manual approval step before deployment, modify `pipeline_stack.py`:

```python
# Add after build stage
approval_action = codepipeline_actions.ManualApprovalAction(
    action_name="Approve_Deployment",
    additional_information="Review test results before deploying to production",
)

pipeline.add_stage(
    stage_name="Approval",
    actions=[approval_action],
)
```

### Adding Notifications

To receive notifications on pipeline events:

```python
from aws_cdk import aws_sns as sns
from aws_cdk import aws_codestarnotifications as notifications

# Create SNS topic
topic = sns.Topic(self, "PipelineNotifications")

# Add notification rule
notifications.NotificationRule(
    self,
    "PipelineNotificationRule",
    source=pipeline,
    events=[
        "codepipeline-pipeline-pipeline-execution-failed",
        "codepipeline-pipeline-pipeline-execution-succeeded",
    ],
    targets=[topic],
)
```

### Multi-Environment Deployment

To deploy to multiple environments (dev, staging, prod):

1. Create separate Lambda stacks for each environment
2. Add multiple deploy stages to the pipeline
3. Use manual approvals between environments

## Cleanup

To delete the pipeline and all resources:

```bash
cd infrastructure
cdk destroy SpeakerRoleClassifierPipelineStack
```

Note: This does NOT delete the Lambda function stack. To delete everything:

```bash
cdk destroy --all
```

## Additional Resources

- [AWS CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
