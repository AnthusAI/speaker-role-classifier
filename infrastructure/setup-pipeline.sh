#!/bin/bash
# Setup script for CI/CD Pipeline

set -e

echo "=========================================="
echo "Speaker Role Classifier Pipeline Setup"
echo "=========================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "Installing AWS CDK..."
    npm install -g aws-cdk
fi

echo "Step 1: Configure AWS Region"
echo "-----------------------------"
echo ""

# Check for AWS region
if [ -z "$AWS_REGION" ] && [ -z "$AWS_DEFAULT_REGION" ]; then
    echo "Enter your AWS region (e.g., us-east-1, us-west-2):"
    read -r AWS_REGION
    export AWS_REGION
    export AWS_DEFAULT_REGION=$AWS_REGION
    echo "Using region: $AWS_REGION"
else
    echo "Using region: ${AWS_REGION:-$AWS_DEFAULT_REGION}"
fi

echo ""
echo "Step 2: Configure Secrets"
echo "--------------------------"
echo ""

# GitHub Token
echo "Do you want to create/update the GitHub token secret? (y/n)"
read -r CREATE_GITHUB_SECRET

if [ "$CREATE_GITHUB_SECRET" = "y" ]; then
    echo "Enter your GitHub Personal Access Token:"
    echo "(Create one at: https://github.com/settings/tokens)"
    echo "Required scopes: repo, admin:repo_hook"
    read -r -s GITHUB_TOKEN
    echo ""
    
    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id github-token &> /dev/null; then
        echo "Updating existing github-token secret..."
        aws secretsmanager update-secret \
            --secret-id github-token \
            --secret-string "{\"token\":\"$GITHUB_TOKEN\"}"
    else
        echo "Creating github-token secret..."
        aws secretsmanager create-secret \
            --name github-token \
            --description "GitHub token for CodePipeline" \
            --secret-string "{\"token\":\"$GITHUB_TOKEN\"}"
    fi
    echo "✓ GitHub token configured"
fi

echo ""

# OpenAI API Key
echo "Do you want to create/update the OpenAI API key secret? (y/n)"
read -r CREATE_OPENAI_SECRET

if [ "$CREATE_OPENAI_SECRET" = "y" ]; then
    echo "Enter your OpenAI API Key:"
    echo "(Get one at: https://platform.openai.com/api-keys)"
    read -r -s OPENAI_API_KEY
    echo ""
    
    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id openai-api-key &> /dev/null; then
        echo "Updating existing openai-api-key secret..."
        aws secretsmanager update-secret \
            --secret-id openai-api-key \
            --secret-string "{\"OPENAI_API_KEY\":\"$OPENAI_API_KEY\"}"
    else
        echo "Creating openai-api-key secret..."
        aws secretsmanager create-secret \
            --name openai-api-key \
            --description "OpenAI API key for Speaker Role Classifier" \
            --secret-string "{\"OPENAI_API_KEY\":\"$OPENAI_API_KEY\"}"
    fi
    echo "✓ OpenAI API key configured"
fi

echo ""
echo "Step 3: Install CDK Dependencies"
echo "---------------------------------"
pip install -r requirements.txt

echo ""
echo "Step 4: Bootstrap CDK (if needed)"
echo "---------------------------------"
echo "Checking if CDK is bootstrapped..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
    echo "Bootstrapping CDK..."
    cdk bootstrap
else
    echo "✓ CDK already bootstrapped"
fi

echo ""
echo "Step 5: Deploy Pipeline Stack"
echo "------------------------------"
echo "Do you want to deploy the pipeline stack now? (y/n)"
read -r DEPLOY_NOW

if [ "$DEPLOY_NOW" = "y" ]; then
    echo "Deploying SpeakerRoleClassifierPipelineStack..."
    cdk deploy SpeakerRoleClassifierPipelineStack
    echo ""
    echo "✓ Pipeline deployed successfully!"
else
    echo "Skipping deployment. You can deploy later with:"
    echo "  cd infrastructure"
    echo "  cdk deploy SpeakerRoleClassifierPipelineStack"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to AWS CodePipeline console to view your pipeline"
echo "2. Push changes to the main branch to trigger the pipeline"
echo "3. Monitor pipeline execution in the AWS Console"
echo ""
echo "For more information, see infrastructure/PIPELINE.md"
