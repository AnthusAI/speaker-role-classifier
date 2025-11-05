# Deployment Guide

## AWS Lambda Deployment with CDK

The Speaker Role Classifier can be deployed as an AWS Lambda function with a Function URL, providing a simple HTTP REST API without needing API Gateway.

### Quick Start

```bash
# 1. Test locally first
python test_lambda_local.py

# 2. Install CDK dependencies
cd infrastructure
pip install -r requirements.txt

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Deploy with your API key
export OPENAI_API_KEY=your_api_key_here
cdk deploy

# 5. Test the deployed endpoint
curl -X POST https://your-function-url.lambda-url.region.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Speaker 0: Hello\nSpeaker 1: Hi"}'
```

### What Gets Deployed

1. **Lambda Function**
   - Runtime: Python 3.11
   - Timeout: 60 seconds
   - Memory: 512 MB
   - Includes all dependencies bundled

2. **Function URL**
   - Direct HTTP endpoint (no API Gateway)
   - CORS enabled for POST requests
   - Public access (can be changed to IAM auth)

3. **CloudWatch Logs**
   - 7-day retention
   - Automatic logging of all requests

### API Usage

**Endpoint:** `POST https://<function-url>.lambda-url.<region>.on.aws/`

**Request:**
```json
{
  "transcript": "Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nSpeaker 1: Hi Jennifer, yes it's 555-0147.\nSpeaker 0: Thank you. I see you're calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nSpeaker 1: Yes, that's correct. We have an emergency situation in one of our units."
}
```

**Response (200 OK):**
```json
{
  "result": "Agent: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nCustomer: Hi Jennifer, yes it's 555-0147.\nAgent: Thank you. I see you're calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nCustomer: Yes, that's correct. We have an emergency situation in one of our units."
}
```

**Error Response (4xx/5xx):**
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### Status Codes

- `200` - Success
- `400` - Bad request (missing/invalid input)
- `422` - Unprocessable entity (speaker mapping issues)
- `502` - OpenAI API error
- `500` - Internal server error

### Cost Estimate

**Lambda:**
- Free tier: 1M requests/month + 400,000 GB-seconds
- After free tier: ~$0.20 per 1M requests
- Compute: $0.0000166667 per GB-second

**OpenAI API:**
- Separate charges based on GPT-5 usage
- Varies by request size

**Example:** 10,000 requests/month ≈ $0.02 Lambda + OpenAI costs

### Security Considerations

**Current Setup (Development):**
- Function URL with NO authentication
- Anyone with the URL can call it
- OPENAI_API_KEY stored in Lambda environment

**Production Recommendations:**
1. Enable IAM authentication on Function URL
2. Use AWS Secrets Manager for OPENAI_API_KEY
3. Add rate limiting via API Gateway
4. Enable AWS WAF for DDoS protection
5. Use CloudFront for caching and additional security

### Monitoring

**View Logs:**
```bash
# Real-time logs
aws logs tail /aws/lambda/SpeakerRoleClassifierStack-ClassifierFunction --follow

# Recent errors
aws logs filter-pattern /aws/lambda/SpeakerRoleClassifierStack-ClassifierFunction --filter-pattern "ERROR"
```

**CloudWatch Metrics:**
- Invocations
- Duration
- Errors
- Throttles

### Updating the Function

```bash
# Make code changes, then:
cd infrastructure
cdk deploy

# CDK will automatically update the Lambda function
```

### Cleanup

```bash
cd infrastructure
cdk destroy

# Confirm deletion when prompted
```

This removes all AWS resources created by the stack.

### Troubleshooting

**"Module not found" during deployment:**
- Ensure `requirements.txt` exists in project root
- Check bundling command in `speaker_role_classifier_stack.py`

**Timeout errors:**
- Increase timeout in stack (currently 60s)
- Check OpenAI API latency

**OPENAI_API_KEY not working:**
- Verify it's exported before `cdk deploy`
- Check Lambda environment variables in AWS Console

**Cold start latency:**
- First request may take 5-10 seconds
- Subsequent requests are faster
- Consider provisioned concurrency for production

### Alternative: Docker Container Deployment

For more control, you can also deploy as a container:

```bash
# Build Docker image
docker build -t speaker-role-classifier .

# Push to ECR
aws ecr create-repository --repository-name speaker-role-classifier
docker tag speaker-role-classifier:latest <account>.dkr.ecr.<region>.amazonaws.com/speaker-role-classifier:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/speaker-role-classifier:latest

# Update Lambda to use container image
```

See AWS documentation for container-based Lambda deployment.

