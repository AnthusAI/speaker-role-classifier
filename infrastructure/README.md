# AWS Lambda Deployment

This directory contains AWS CDK infrastructure code to deploy the Speaker Role Classifier as a Lambda function with a Function URL (HTTP endpoint).

## Architecture

- **Lambda Function**: Python 3.11 runtime with the classifier code
- **Function URL**: Direct HTTP endpoint (no API Gateway needed)
- **Environment Variables**: OPENAI_API_KEY passed from your environment
- **Timeout**: 60 seconds (for API calls)
- **Memory**: 512 MB

## Prerequisites

1. AWS CLI configured with credentials
2. AWS CDK installed: `npm install -g aws-cdk`
3. Python 3.11+
4. Your OpenAI API key

## Setup

```bash
# Navigate to infrastructure directory
cd infrastructure

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap
```

## Deployment

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Deploy the stack
cdk deploy

# The output will show your Function URL like:
# SpeakerRoleClassifierStack.FunctionUrl = https://abc123.lambda-url.us-east-1.on.aws/
```

## Testing

Once deployed, test with curl:

```bash
# Get the Function URL from the deployment output
FUNCTION_URL="https://your-function-url.lambda-url.us-east-1.on.aws/"

# Test the endpoint
curl -X POST $FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nSpeaker 1: Hi Jennifer, yes it'\''s 555-0147.\nSpeaker 0: Thank you. I see you'\''re calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nSpeaker 1: Yes, that'\''s correct. We have an emergency situation in one of our units."
  }'
```

Expected response:
```json
{
  "result": "Agent: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nCustomer: Hi Jennifer, yes it's 555-0147.\nAgent: Thank you. I see you're calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nCustomer: Yes, that's correct. We have an emergency situation in one of our units."
}
```

## API Specification

### Endpoint
`POST https://your-function-url.lambda-url.region.on.aws/`

### Request
```json
{
  "transcript": "Speaker 0: text\nSpeaker 1: text"
}
```

### Response (Success - 200)
```json
{
  "result": "Agent: text\nCustomer: text"
}
```

### Response (Error - 4xx/5xx)
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Status Codes
- `200` - Success
- `400` - Bad request (missing/empty transcript, invalid JSON)
- `422` - Unprocessable entity (speaker mapping issues)
- `502` - Bad gateway (OpenAI API error)
- `500` - Internal server error

## Security

**⚠️ WARNING**: The Function URL is currently configured with `NONE` authentication, making it publicly accessible. 

For production use, consider:

1. **Enable IAM Authentication**: Change `auth_type=lambda_.FunctionUrlAuthType.AWS_IAM` in the stack
2. **Add API Gateway**: For more advanced features (rate limiting, API keys, etc.)
3. **Use Secrets Manager**: Store OPENAI_API_KEY in AWS Secrets Manager instead of environment variables

## Cost Considerations

- Lambda: Pay per request + compute time
- Typical cost: ~$0.20 per 1M requests + $0.0000166667 per GB-second
- OpenAI API: Separate charges based on GPT-5 usage

## Monitoring

View logs in CloudWatch:
```bash
# Get function name from output
aws logs tail /aws/lambda/SpeakerRoleClassifierStack-ClassifierFunction --follow
```

## Cleanup

To delete all resources:
```bash
cdk destroy
```

## Troubleshooting

### "Module not found" errors
- Ensure `requirements.txt` is in the project root
- Check that bundling command includes all dependencies

### Timeout errors
- Increase timeout in `speaker_role_classifier_stack.py`
- Check OpenAI API response times

### OPENAI_API_KEY not set
- Ensure you export the variable before `cdk deploy`
- Check Lambda environment variables in AWS Console

