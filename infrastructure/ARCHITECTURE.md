# CI/CD Architecture Diagrams

## Current Manual Deployment

```
┌──────────────┐
│  Developer   │
│   Machine    │
└──────┬───────┘
       │
       │ cdk deploy
       │
       ▼
┌──────────────────────────────────────────┐
│           AWS Account                     │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │   CloudFormation Stack             │  │
│  │                                    │  │
│  │  ┌──────────────────────────────┐ │  │
│  │  │   Lambda Function            │ │  │
│  │  │   • Python 3.11              │ │  │
│  │  │   • 512 MB RAM               │ │  │
│  │  │   • 60s timeout              │ │  │
│  │  │   • OPENAI_API_KEY env var   │ │  │
│  │  └──────────────────────────────┘ │  │
│  │                                    │  │
│  │  ┌──────────────────────────────┐ │  │
│  │  │   Function URL               │ │  │
│  │  │   (Public HTTPS endpoint)    │ │  │
│  │  └──────────────────────────────┘ │  │
│  │                                    │  │
│  │  ┌──────────────────────────────┐ │  │
│  │  │   CloudWatch Log Group       │ │  │
│  │  │   (7 day retention)          │ │  │
│  │  └──────────────────────────────┘ │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## AWS CodePipeline CI/CD

```
┌────────────────────────────────────────────────────────────────────────┐
│                              GitHub                                     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AnthusAI/speaker-role-classifier                                │  │
│  │                                                                  │  │
│  │  • main branch                                                   │  │
│  │  • Webhook configured                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 │ Push to main triggers webhook
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           AWS Account                                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      AWS CodePipeline                            │  │
│  │                                                                  │  │
│  │  ┌───────────────┐      ┌───────────────┐      ┌─────────────┐ │  │
│  │  │  Source Stage │─────▶│  Build Stage  │─────▶│Deploy Stage │ │  │
│  │  │               │      │               │      │             │ │  │
│  │  │ • Clone repo  │      │ • Run pytest  │      │ • CDK deploy│ │  │
│  │  │ • Get code    │      │ • Validate    │      │ • Update Λ  │ │  │
│  │  └───────────────┘      └───────────────┘      └─────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                        │           │
│                                    ▼                        ▼           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     AWS CodeBuild Projects                      │   │
│  │                                                                 │   │
│  │  ┌──────────────────────────┐   ┌──────────────────────────┐  │   │
│  │  │  Build Project           │   │  Deploy Project          │  │   │
│  │  │                          │   │                          │  │   │
│  │  │ • Python 3.11            │   │ • Python 3.11            │  │   │
│  │  │ • Install deps           │   │ • Node.js 18             │  │   │
│  │  │ • Run pytest             │   │ • Install CDK            │  │   │
│  │  │ • Generate artifacts     │   │ • Deploy stack           │  │   │
│  │  │                          │   │                          │  │   │
│  │  │ Env vars from:           │   │ Env vars from:           │  │   │
│  │  │ • Secrets Manager        │   │ • Secrets Manager        │  │   │
│  │  └──────────────────────────┘   └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                      │                  │
│                                                      ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Lambda Function (Updated)                     │   │
│  │                                                                 │   │
│  │  • New code deployed                                            │   │
│  │  • Zero downtime update                                         │   │
│  │  • Function URL remains same                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AWS Secrets Manager                          │   │
│  │                                                                 │   │
│  │  • github-token                                                 │   │
│  │  • openai-api-key                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CloudWatch Logs                              │   │
│  │                                                                 │   │
│  │  • Pipeline execution logs                                      │   │
│  │  • CodeBuild logs                                               │   │
│  │  • Lambda function logs                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

## GitHub Actions CI/CD

```
┌────────────────────────────────────────────────────────────────────────┐
│                              GitHub                                     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AnthusAI/speaker-role-classifier                                │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  .github/workflows/deploy.yml                              │ │  │
│  │  │                                                            │ │  │
│  │  │  • Triggers on push to main                                │ │  │
│  │  │  • Triggers on pull requests                               │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Repository Secrets                                        │ │  │
│  │  │                                                            │ │  │
│  │  │  • AWS_ACCESS_KEY_ID                                       │ │  │
│  │  │  • AWS_SECRET_ACCESS_KEY                                   │ │  │
│  │  │  • AWS_REGION                                              │ │  │
│  │  │  • OPENAI_API_KEY                                          │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    GitHub Actions Runner                         │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Test Job                                                  │ │  │
│  │  │                                                            │ │  │
│  │  │  1. Checkout code                                          │ │  │
│  │  │  2. Setup Python 3.11                                      │ │  │
│  │  │  3. Install dependencies                                   │ │  │
│  │  │  4. Run pytest                                             │ │  │
│  │  │  5. Upload coverage                                        │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                            │                                     │  │
│  │                            │ Tests pass                          │  │
│  │                            ▼                                     │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Deploy Job (main branch only)                             │ │  │
│  │  │                                                            │ │  │
│  │  │  1. Checkout code                                          │ │  │
│  │  │  2. Setup Python 3.11 + Node.js 18                         │ │  │
│  │  │  3. Configure AWS credentials                              │ │  │
│  │  │  4. Install AWS CDK                                        │ │  │
│  │  │  5. Deploy Lambda function                                 │ │  │
│  │  │  6. Test deployed endpoint                                 │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 │ AWS API calls
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           AWS Account                                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Lambda Function (Updated)                     │   │
│  │                                                                 │   │
│  │  • New code deployed via CDK                                    │   │
│  │  • CloudFormation handles update                                │   │
│  │  • Zero downtime deployment                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

## Deployment Flow Comparison

### CodePipeline Flow
```
Developer → Git Push → GitHub → Webhook → CodePipeline → CodeBuild (Test) 
                                                              │
                                                              ├─ Pass → CodeBuild (Deploy) → Lambda
                                                              │
                                                              └─ Fail → Stop (notify)
```

### GitHub Actions Flow
```
Developer → Git Push → GitHub → Actions Trigger → Test Job
                                                      │
                                                      ├─ Pass → Deploy Job → AWS CDK → Lambda
                                                      │
                                                      └─ Fail → Stop (PR status)
```

## Security Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Security Layers                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Source Control                                       │  │
│  │     • Branch protection on main                          │  │
│  │     • Required PR reviews                                │  │
│  │     • Status checks must pass                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. Secrets Management                                   │  │
│  │     • AWS Secrets Manager (CodePipeline)                 │  │
│  │     • GitHub Secrets (Actions)                           │  │
│  │     • No secrets in code                                 │  │
│  │     • Encrypted at rest                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3. IAM Permissions                                      │  │
│  │     • Least privilege roles                              │  │
│  │     • Separate roles for build/deploy                    │  │
│  │     • No long-term credentials in code                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  4. Network Security                                     │  │
│  │     • HTTPS only                                         │  │
│  │     • Function URL with optional IAM auth                │  │
│  │     • VPC optional for Lambda                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5. Audit & Monitoring                                   │  │
│  │     • CloudWatch Logs                                    │  │
│  │     • CloudTrail for API calls                           │  │
│  │     • Pipeline execution history                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Cost Breakdown

### CodePipeline Monthly Costs

```
┌─────────────────────────────────────────────────────────┐
│  Service              │  Usage         │  Cost          │
├───────────────────────┼────────────────┼────────────────┤
│  CodePipeline         │  1 pipeline    │  $1.00         │
│  CodeBuild (Build)    │  20 × 5 min    │  $0.50         │
│  CodeBuild (Deploy)   │  20 × 3 min    │  $0.30         │
│  CloudWatch Logs      │  Storage       │  $0.50         │
│  Secrets Manager      │  2 secrets     │  $0.80         │
│  Data Transfer        │  Minimal       │  $0.10         │
├───────────────────────┴────────────────┼────────────────┤
│  Total Monthly Cost                    │  ~$3.20        │
└────────────────────────────────────────┴────────────────┘

Plus Lambda costs (same for both approaches):
- Invocations: $0.20 per 1M requests
- Compute: $0.0000166667 per GB-second
```

### GitHub Actions Monthly Costs

```
┌─────────────────────────────────────────────────────────┐
│  Repository Type      │  Free Minutes  │  Typical Usage │
├───────────────────────┼────────────────┼────────────────┤
│  Public               │  Unlimited     │  FREE          │
│  Private              │  2,000/month   │  ~100 min      │
├───────────────────────┴────────────────┼────────────────┤
│  Total Monthly Cost                    │  FREE          │
└────────────────────────────────────────┴────────────────┘

Plus Lambda costs (same for both approaches)
```

## Scaling Considerations

### Small Team (< 10 developers)
- **GitHub Actions** recommended
- Free tier sufficient
- Simple setup and maintenance

### Medium Team (10-50 developers)
- **Either option** works well
- Consider CodePipeline for AWS integration
- GitHub Actions still cost-effective

### Large Team (> 50 developers)
- **CodePipeline** may be better
- More control and customization
- Better integration with AWS services
- Centralized secret management

### High Frequency Deployments
- **GitHub Actions** more cost-effective
- No per-pipeline charges
- Faster cold starts

## Disaster Recovery

### Backup Strategy

```
┌────────────────────────────────────────────────────────┐
│  Component            │  Backup Method                 │
├───────────────────────┼────────────────────────────────┤
│  Source Code          │  Git (multiple clones)         │
│  Infrastructure       │  CDK code in Git               │
│  Secrets              │  Manual backup (encrypted)     │
│  Lambda Function      │  Versioning enabled            │
│  CloudFormation       │  Stack templates in S3         │
└───────────────────────┴────────────────────────────────┘
```

### Recovery Procedures

1. **Pipeline Failure**: Automatic retry or manual trigger
2. **Lambda Corruption**: Rollback to previous version
3. **Secret Compromise**: Rotate in Secrets Manager/GitHub
4. **Complete AWS Failure**: Redeploy from Git to new region
5. **GitHub Outage**: Use CodePipeline (or vice versa)
