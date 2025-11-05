#!/usr/bin/env python3
"""CDK app for Speaker Role Classifier Lambda function."""

import aws_cdk as cdk
from speaker_role_classifier_stack import SpeakerRoleClassifierStack

app = cdk.App()

SpeakerRoleClassifierStack(
    app,
    "SpeakerRoleClassifierStack",
    description="Speaker Role Classifier Lambda Function with Function URL"
)

app.synth()

