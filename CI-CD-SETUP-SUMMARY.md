# CI/CD Pipeline Setup - Summary

This document summarizes the CI/CD pipeline setup for the Speaker Role Classifier project.

## What Was Created

### 1. AWS CodePipeline Stack (`infrastructure/pipeline_stack.py`)

A complete CDK stack that creates:
- **CodePipeline** - Orchestrates the CI/CD workflow
- **CodeBuild Projects** - Two projects for testing and deployment
- **GitHub Integration** - Webhook-based triggers on push to main
- **IAM Roles** - Proper permissions for all resources

**Pipeline Flow:**
```
GitHub Push → Source Stage → Build/Test Stage → Deploy Stage → Lambda Updated
```

### 2. GitHub Actions Workflow (`.github/workflows/deploy.yml`)

An alternative CI/CD solution using GitHub Actions:
- **Test Job** - Runs pytest on every push and PR
- **Deploy Job** - Deploys to AWS Lambda on push to main
- **Coverage Reporting** - Integrates with Codecov
- **PR Comments** - Automatic feedback on pull requests

### 3. Documentation

#### `infrastructure/PIPELINE.md`
Comprehensive guide covering:
- Architecture overview
- Setup instructions
- Secrets management
- Monitoring and troubleshooting
- Cost considerations
- Advanced configurations

#### `CI-CD-COMPARISON.md`
Helps you choose between:
- AWS CodePipeline vs GitHub Actions
- Cost analysis
- Feature comparison
- Migration guides

#### `infrastructure/setup-pipeline.sh`
Interactive setup script that:
- Configures AWS Secrets Manager
- Installs dependencies
- Bootstraps CDK
- Deploys the pipeline

### 4. Configuration Files

#### `buildspec.yml`
Reference CodeBuild buildspec showing:
- Test execution
- Dependency installation
- Build process

#### Updated `infrastructure/app.py`
Now includes both stacks:
- `SpeakerRoleClassifierStack` - Lambda function
- `SpeakerRoleClassifierPipelineStack` - CI/CD pipeline

#### Updated `infrastructure/README.md`
Enhanced with:
- CI/CD pipeline information
- Deployment options
- Links to detailed guides

#### Updated main `README.md`
Added CI/CD section with:
- Quick start options
- Links to documentation
- Deployment choices

## Quick Start

### Option 1: AWS CodePipeline

```bash
cd infrastructure
./setup-pipeline.sh
```

**Requirements:**
- GitHub Personal Access Token (repo, admin:repo_hook scopes)
- OpenAI API Key
- AWS credentials configured

**What it does:**
1. Stores secrets in AWS Secrets Manager
2. Deploys CodePipeline stack
3. Sets up GitHub webhook
4. Triggers initial pipeline run

### Option 2: GitHub Actions

```bash
# 1. Add GitHub Secrets (in repository settings):
#    - AWS_ACCESS_KEY_ID
#    - AWS_SECRET_ACCESS_KEY
#    - AWS_REGION
#    - OPENAI_API_KEY

# 2. Push the workflow file
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions CI/CD"
git push origin main

# 3. Check Actions tab in GitHub
```

## Architecture

### AWS CodePipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub Repo                          │
│                  (AnthusAI/speaker-role-classifier)         │
└────────────────────────────┬────────────────────────────────┘
                             │ Webhook on push to main
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS CodePipeline                        │
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   Source    │───▶│  Build/Test  │───▶│    Deploy     │  │
│  │   Stage     │    │    Stage     │    │    Stage      │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│        │                   │                     │           │
│        │                   │                     │           │
│        ▼                   ▼                     ▼           │
│   Pull from          Run pytest           CDK Deploy        │
│    GitHub           CodeBuild             CodeBuild         │
└─────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
                                          ┌────────────────┐
                                          │ Lambda Function│
                                          │   (Updated)    │
                                          └────────────────┘
```

### GitHub Actions Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub Repo                          │
│                  (AnthusAI/speaker-role-classifier)         │
└────────────────────────────┬────────────────────────────────┘
                             │ Push to main or PR
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Actions                          │
│                                                               │
│  ┌─────────────────────┐         ┌────────────────────────┐ │
│  │     Test Job        │         │     Deploy Job         │ │
│  │                     │         │   (main branch only)   │ │
│  │  • Install deps     │         │                        │ │
│  │  • Run pytest       │────────▶│  • Configure AWS       │ │
│  │  • Upload coverage  │         │  • Install CDK         │ │
│  │                     │         │  • Deploy Lambda       │ │
│  └─────────────────────┘         └────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ Lambda Function│
                                     │   (Updated)    │
                                     └────────────────┘
```

## Features

### Both Solutions Provide

✅ **Automated Testing** - Runs full test suite on every change
✅ **Automated Deployment** - Deploys to Lambda on push to main
✅ **Secrets Management** - Secure storage of API keys and credentials
✅ **Build Logs** - Detailed logs for debugging
✅ **Failure Notifications** - Know immediately when something breaks

### CodePipeline Specific

✅ **AWS-Native** - Fully integrated with AWS services
✅ **Secrets Manager** - Centralized secret management
✅ **CloudWatch Integration** - Advanced monitoring and logging
✅ **No GitHub Dependency** - Runs entirely in AWS

### GitHub Actions Specific

✅ **Free Tier** - 2000 minutes/month for private repos, unlimited for public
✅ **Simple Setup** - Just add YAML file and secrets
✅ **GitHub Integration** - PR comments, status checks, etc.
✅ **Easy Debugging** - View logs directly in GitHub UI

## Cost Comparison

### AWS CodePipeline
```
Monthly costs (estimated):
- CodePipeline:        $1.00
- CodeBuild:           $0.50  (20 builds × 5 min × $0.005/min)
- CloudWatch Logs:     $0.50
- Secrets Manager:     $0.80  (2 secrets × $0.40)
─────────────────────────────
Total:                 ~$2.80-5.00/month
```

### GitHub Actions
```
Monthly costs (estimated):
- Public repo:         FREE (unlimited)
- Private repo:        FREE (within 2000 min/month free tier)
                       Typical usage: ~100 min/month
─────────────────────────────
Total:                 FREE (for most use cases)
```

## Next Steps

1. **Choose Your CI/CD Solution**
   - Read [CI-CD-COMPARISON.md](CI-CD-COMPARISON.md)
   - Consider your team's preferences and existing tools

2. **Set Up Secrets**
   - AWS Secrets Manager (for CodePipeline)
   - GitHub Secrets (for GitHub Actions)

3. **Deploy the Pipeline**
   - Run setup script or configure manually
   - Monitor first pipeline run

4. **Test the Pipeline**
   - Make a small change
   - Push to a branch
   - Create PR and merge to main
   - Verify deployment

5. **Configure Notifications** (Optional)
   - Set up SNS topics (CodePipeline)
   - Configure GitHub notifications (Actions)

6. **Add Branch Protection** (Recommended)
   - Require PR reviews
   - Require status checks to pass
   - Prevent direct pushes to main

## Troubleshooting

### Pipeline Not Triggering

**CodePipeline:**
- Check GitHub webhook in repository settings
- Verify GitHub token in Secrets Manager
- Check CloudWatch Events

**GitHub Actions:**
- Check workflow file syntax
- Verify workflow is enabled
- Check branch name matches trigger

### Tests Failing

- Run tests locally first: `pytest tests/ -v`
- Check test output in build logs
- Verify OPENAI_API_KEY is set correctly

### Deployment Failing

- Check IAM permissions
- Verify CDK bootstrap is complete
- Check CloudFormation stack events
- Review CodeBuild/Actions logs

## Monitoring

### CodePipeline
```bash
# View pipeline status
aws codepipeline get-pipeline-state \
  --pipeline-name SpeakerRoleClassifierPipeline

# View build logs
aws logs tail /aws/codebuild/SpeakerRoleClassifierBuild --follow
```

### GitHub Actions
- Go to repository → Actions tab
- Click on workflow run to view details
- Download logs for offline analysis

## Security Best Practices

1. **Use Secrets Manager** - Never commit secrets to repository
2. **Rotate Credentials** - Regularly rotate API keys and tokens
3. **Least Privilege** - Grant minimum required IAM permissions
4. **Branch Protection** - Require reviews before merging
5. **Audit Logs** - Monitor CloudTrail/GitHub audit logs

## Resources

### Documentation
- [infrastructure/PIPELINE.md](infrastructure/PIPELINE.md) - Detailed pipeline guide
- [CI-CD-COMPARISON.md](CI-CD-COMPARISON.md) - Choose your CI/CD solution
- [infrastructure/README.md](infrastructure/README.md) - Deployment guide

### AWS Resources
- [CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [CDK Documentation](https://docs.aws.amazon.com/cdk/)

### GitHub Resources
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/actions/reference/workflow-syntax-for-github-actions)

## Support

If you encounter issues:

1. Check the troubleshooting section in relevant documentation
2. Review build logs for specific errors
3. Verify all prerequisites are met
4. Check GitHub Issues for similar problems

## Contributing

When contributing to the CI/CD setup:

1. Test changes in a separate stack/workflow first
2. Document any new features or changes
3. Update cost estimates if adding new resources
4. Ensure backward compatibility when possible
