# CI/CD Options Comparison

This project supports two CI/CD approaches for automated testing and deployment. Choose the one that best fits your needs.

## Quick Comparison

| Feature | AWS CodePipeline | GitHub Actions |
|---------|-----------------|----------------|
| **Cost** | ~$5-10/month | Free for public repos, 2000 min/month for private |
| **Setup Complexity** | Medium (AWS resources) | Simple (YAML file) |
| **Integration** | Native AWS | GitHub native |
| **Secrets Management** | AWS Secrets Manager | GitHub Secrets |
| **Build Minutes** | Pay per minute | 2000 free/month (private repos) |
| **Monitoring** | CloudWatch | GitHub UI |
| **Best For** | AWS-heavy workflows | GitHub-centric teams |

## Option 1: AWS CodePipeline

### Pros
- ✅ Native AWS integration
- ✅ Centralized secrets in AWS Secrets Manager
- ✅ Better for complex AWS workflows
- ✅ Can integrate with other AWS services easily
- ✅ No dependency on GitHub Actions availability

### Cons
- ❌ Costs ~$1/month for pipeline + build minutes
- ❌ More complex setup
- ❌ Requires AWS Secrets Manager configuration
- ❌ Harder to debug (must check CloudWatch logs)

### Setup

See **[infrastructure/PIPELINE.md](infrastructure/PIPELINE.md)** for complete instructions.

Quick start:
```bash
cd infrastructure
./setup-pipeline.sh
```

### When to Use
- You're already using AWS services extensively
- You want centralized secret management in AWS
- You need to integrate with other AWS services
- You prefer AWS-native tooling

## Option 2: GitHub Actions

### Pros
- ✅ Free for public repos, generous free tier for private
- ✅ Simple YAML configuration
- ✅ Easy to debug in GitHub UI
- ✅ Integrated with GitHub features (PR comments, etc.)
- ✅ Faster setup

### Cons
- ❌ Requires GitHub secrets configuration
- ❌ Limited build minutes on free tier (private repos)
- ❌ Dependent on GitHub Actions availability
- ❌ Less integrated with AWS ecosystem

### Setup

1. **Configure GitHub Secrets**

   Go to your repository → Settings → Secrets and variables → Actions

   Add these secrets:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
   - `AWS_REGION` - AWS region (e.g., us-east-1)
   - `OPENAI_API_KEY` - Your OpenAI API key

2. **Enable GitHub Actions**

   The workflow file is already in `.github/workflows/deploy.yml`
   
   Push to main branch to trigger the workflow:
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Add GitHub Actions CI/CD"
   git push origin main
   ```

3. **Monitor Workflow**

   Go to your repository → Actions tab to see workflow runs

### When to Use
- You prefer GitHub-native tools
- You want simpler setup and debugging
- Your repository is public (free unlimited minutes)
- You're comfortable with GitHub Secrets

## Hybrid Approach

You can use both! For example:
- **GitHub Actions** for PR testing and validation
- **AWS CodePipeline** for production deployments

To do this:
1. Keep the GitHub Actions workflow but remove the deploy job
2. Set up CodePipeline for deployments
3. GitHub Actions runs tests on every PR
4. CodePipeline deploys when merged to main

Modify `.github/workflows/deploy.yml`:
```yaml
# Remove the 'deploy' job, keep only 'test' job
jobs:
  test:
    # ... existing test configuration
```

## Migration Between Options

### From GitHub Actions to CodePipeline

1. Deploy the pipeline stack:
   ```bash
   cd infrastructure
   ./setup-pipeline.sh
   ```

2. Optionally disable GitHub Actions:
   ```bash
   git rm .github/workflows/deploy.yml
   git commit -m "Switch to CodePipeline"
   ```

### From CodePipeline to GitHub Actions

1. Configure GitHub Secrets (see GitHub Actions setup above)

2. Destroy the pipeline stack:
   ```bash
   cd infrastructure
   cdk destroy SpeakerRoleClassifierPipelineStack
   ```

3. Commit the GitHub Actions workflow:
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Switch to GitHub Actions"
   git push
   ```

## Cost Analysis

### AWS CodePipeline
```
Monthly costs:
- CodePipeline: $1/month (1 active pipeline)
- CodeBuild: ~$0.005/minute × ~5 min/build × ~20 builds/month = $0.50
- CloudWatch Logs: ~$0.50/month
- Secrets Manager: $0.40/secret/month × 2 = $0.80
Total: ~$2.80-5/month
```

### GitHub Actions
```
Monthly costs:
- Public repository: FREE (unlimited minutes)
- Private repository: 
  - Free tier: 2000 minutes/month
  - Typical usage: ~5 min/build × ~20 builds = 100 minutes
  - Cost: FREE (within free tier)
```

## Recommendation

**For most teams**: Start with **GitHub Actions**
- Simpler setup
- Free for most use cases
- Easier debugging
- Good enough for most projects

**Upgrade to CodePipeline when**:
- You need more than 2000 build minutes/month
- You want AWS-native secret management
- You're building complex AWS workflows
- You need integration with other AWS services

## Testing Both Locally

Before committing to either approach, test locally:

```bash
# Test the build process
cd /path/to/project
pip install -e .[dev]
pytest tests/ -v

# Test CDK deployment
cd infrastructure
export OPENAI_API_KEY=your_key
cdk synth  # Just synthesize, don't deploy
```

## Support and Troubleshooting

### GitHub Actions Issues
- Check the Actions tab in your GitHub repository
- Review workflow logs directly in GitHub
- Common issues: AWS credentials, secret configuration

### CodePipeline Issues
- Check CodePipeline console in AWS
- Review CodeBuild logs in CloudWatch
- Common issues: IAM permissions, Secrets Manager access

See respective documentation:
- [GitHub Actions Documentation](.github/workflows/deploy.yml)
- [CodePipeline Documentation](infrastructure/PIPELINE.md)
