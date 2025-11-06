#!/usr/bin/env python3
"""CDK app for Speaker Role Classifier Lambda function and CI/CD Pipeline."""

import aws_cdk as cdk
from speaker_role_classifier_stack import SpeakerRoleClassifierStack
from pipeline_stack import PipelineStack

app = cdk.App()

# Lambda function stack
SpeakerRoleClassifierStack(
    app,
    "SpeakerRoleClassifierStack",
    description="Speaker Role Classifier Lambda Function with Function URL"
)

# CI/CD Pipeline stack
PipelineStack(
    app,
    "SpeakerRoleClassifierPipelineStack",
    description="CI/CD Pipeline for Speaker Role Classifier"
)

app.synth()
