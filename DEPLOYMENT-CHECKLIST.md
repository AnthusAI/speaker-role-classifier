# CI/CD Deployment Checklist

Use this checklist to ensure a smooth CI/CD pipeline setup.

## Pre-Deployment Checklist

### Prerequisites
- [ ] AWS account with appropriate permissions
- [ ] AWS CLI installed and configured
- [ ] GitHub repository access (AnthusAI/speaker-role-classifier)
- [ ] OpenAI API key
- [ ] Node.js 18+ installed (for CDK)
- [ ] Python 3.11+ installed

### Local Testing
- [ ] All tests pass locally: `pytest tests/ -v`
- [ ] Lambda handler works locally: `python test_lambda_local.py`
- [ ] CDK synth succeeds: `cd infrastructure && cdk synth`

## Option 1: AWS CodePipeline Setup

### Step 1: Prepare Secrets
- [ ] Create GitHub Personal Access Token
  - [ ] Go to GitHub Settings → Developer settings → Tokens
  - [ ] Generate new token (classic)
  - [ ] Select scopes: `repo`, `admin:repo_hook`
  - [ ] Copy token (you won't see it again!)

- [ ] Have OpenAI API key ready
  - [ ] Get from https://platform.openai.com/api-keys

### Step 2: Configure AWS Secrets Manager
- [ ] Store GitHub token:
  ```bash
  aws secretsmanager create-secret \
      --name github-token \
      --secret-string '{"token":"YOUR_TOKEN_HERE"}'
  ```

- [ ] Store OpenAI API key:
  ```bash
  aws secretsmanager create-secret \
      --name openai-api-key \
      --secret-string '{"OPENAI_API_KEY":"YOUR_KEY_HERE"}'
  ```

- [ ] Verify secrets created:
  ```bash
  aws secretsmanager list-secrets
  ```

### Step 3: Deploy Pipeline Stack
- [ ] Navigate to infrastructure directory: `cd infrastructure`
- [ ] Install CDK dependencies: `pip install -r requirements.txt`
- [ ] Bootstrap CDK (if not done): `cdk bootstrap`
- [ ] Deploy pipeline: `cdk deploy SpeakerRoleClassifierPipelineStack`
- [ ] Note the stack outputs

### Step 4: Verify Pipeline
- [ ] Go to AWS CodePipeline console
- [ ] Find "SpeakerRoleClassifierPipeline"
- [ ] Verify pipeline is created
- [ ] Check if initial execution started
- [ ] Monitor execution through all stages

### Step 5: Test Pipeline
- [ ] Make a small change to code
- [ ] Commit and push to main branch
- [ ] Verify pipeline triggers automatically
- [ ] Check all stages complete successfully
- [ ] Verify Lambda function updated

## Option 2: GitHub Actions Setup

### Step 1: Configure GitHub Secrets
- [ ] Go to repository Settings → Secrets and variables → Actions
- [ ] Add secret: `AWS_ACCESS_KEY_ID`
- [ ] Add secret: `AWS_SECRET_ACCESS_KEY`
- [ ] Add secret: `AWS_REGION` (e.g., us-east-1)
- [ ] Add secret: `OPENAI_API_KEY`

### Step 2: Verify Workflow File
- [ ] Check `.github/workflows/deploy.yml` exists
- [ ] Review workflow configuration
- [ ] Ensure branch names match (main)

### Step 3: Enable Workflow
- [ ] Commit workflow file if not already:
  ```bash
  git add .github/workflows/deploy.yml
  git commit -m "Add GitHub Actions CI/CD"
  git push origin main
  ```

### Step 4: Monitor First Run
- [ ] Go to repository → Actions tab
- [ ] Find the workflow run
- [ ] Monitor test job
- [ ] Monitor deploy job (if on main branch)
- [ ] Check for any errors

### Step 5: Test Workflow
- [ ] Create a new branch
- [ ] Make a small change
- [ ] Push and create PR
- [ ] Verify tests run on PR
- [ ] Merge PR to main
- [ ] Verify deployment runs

## Post-Deployment Checklist

### Verify Lambda Function
- [ ] Get Function URL from stack outputs
- [ ] Test endpoint with curl:
  ```bash
  curl -X POST YOUR_FUNCTION_URL \
    -H "Content-Type: application/json" \
    -d '{"transcript": "Speaker 0: Hello\nSpeaker 1: Hi"}'
  ```
- [ ] Verify response is correct
- [ ] Check CloudWatch logs for function execution

### Configure Monitoring
- [ ] Set up CloudWatch alarms (optional)
- [ ] Configure SNS notifications (optional)
- [ ] Set up log retention policies
- [ ] Enable X-Ray tracing (optional)

### Security Hardening
- [ ] Review IAM roles and permissions
- [ ] Enable branch protection on main:
  - [ ] Require PR reviews
  - [ ] Require status checks
  - [ ] Prevent force pushes
- [ ] Consider enabling Function URL IAM auth
- [ ] Review CloudTrail logs
- [ ] Set up AWS Config rules (optional)

### Documentation
- [ ] Update team documentation with Function URL
- [ ] Document deployment process
- [ ] Share access to AWS console/GitHub
- [ ] Document secret rotation procedures

## Ongoing Maintenance Checklist

### Weekly
- [ ] Review pipeline execution logs
- [ ] Check for failed deployments
- [ ] Monitor Lambda error rates
- [ ] Review CloudWatch metrics

### Monthly
- [ ] Review and optimize Lambda memory/timeout
- [ ] Check AWS costs
- [ ] Review security group rules
- [ ] Update dependencies if needed

### Quarterly
- [ ] Rotate GitHub token
- [ ] Rotate OpenAI API key
- [ ] Review and update IAM policies
- [ ] Update CDK and dependencies
- [ ] Review and optimize costs

### As Needed
- [ ] Update Python runtime version
- [ ] Update Lambda dependencies
- [ ] Modify pipeline stages
- [ ] Add new environments (staging, prod)

## Troubleshooting Checklist

### Pipeline Not Triggering
- [ ] Check GitHub webhook exists
- [ ] Verify webhook is active
- [ ] Check GitHub token permissions
- [ ] Review CodePipeline source configuration
- [ ] Check CloudWatch Events rules

### Tests Failing
- [ ] Run tests locally first
- [ ] Check test output in logs
- [ ] Verify OPENAI_API_KEY is set
- [ ] Check for dependency issues
- [ ] Review recent code changes

### Deployment Failing
- [ ] Check IAM permissions
- [ ] Verify CDK bootstrap completed
- [ ] Check CloudFormation events
- [ ] Review CodeBuild logs
- [ ] Verify all secrets are set correctly

### Lambda Function Issues
- [ ] Check CloudWatch logs
- [ ] Verify environment variables
- [ ] Test locally with test_lambda_local.py
- [ ] Check Lambda timeout settings
- [ ] Verify OpenAI API key is valid

## Rollback Procedures

### Rollback Lambda Function
```bash
# List function versions
aws lambda list-versions-by-function \
  --function-name SpeakerRoleClassifierStack-ClassifierFunction

# Update alias to previous version
aws lambda update-alias \
  --function-name SpeakerRoleClassifierStack-ClassifierFunction \
  --name live \
  --function-version <previous-version>
```

### Rollback Pipeline Changes
```bash
# Revert CDK changes
git revert <commit-hash>
git push origin main

# Or redeploy previous version
git checkout <previous-commit>
cd infrastructure
cdk deploy SpeakerRoleClassifierPipelineStack
```

### Emergency Shutdown
```bash
# Disable pipeline
aws codepipeline disable-stage-transition \
  --pipeline-name SpeakerRoleClassifierPipeline \
  --stage-name Deploy \
  --transition-type Inbound \
  --reason "Emergency maintenance"

# Or delete Function URL
aws lambda delete-function-url-config \
  --function-name SpeakerRoleClassifierStack-ClassifierFunction
```

## Success Criteria

Your CI/CD pipeline is successfully deployed when:

- ✅ Pipeline/workflow is visible in AWS/GitHub
- ✅ All stages/jobs complete successfully
- ✅ Lambda function is deployed and accessible
- ✅ Function URL returns correct responses
- ✅ Tests run automatically on new commits
- ✅ Deployments happen automatically on merge to main
- ✅ CloudWatch logs show function executions
- ✅ No errors in pipeline/workflow logs

## Getting Help

If you encounter issues:

1. **Check Documentation**
   - [infrastructure/PIPELINE.md](infrastructure/PIPELINE.md)
   - [CI-CD-COMPARISON.md](CI-CD-COMPARISON.md)
   - [CI-CD-SETUP-SUMMARY.md](CI-CD-SETUP-SUMMARY.md)

2. **Review Logs**
   - CodeBuild logs in CloudWatch
   - GitHub Actions logs in Actions tab
   - Lambda logs in CloudWatch

3. **Common Issues**
   - See troubleshooting sections in documentation
   - Check AWS service health dashboard
   - Review GitHub status page

4. **Support Channels**
   - GitHub Issues
   - AWS Support (if applicable)
   - Team Slack/communication channel

## Notes

- Keep this checklist updated as your pipeline evolves
- Document any custom modifications
- Share lessons learned with the team
- Regular reviews help catch issues early
