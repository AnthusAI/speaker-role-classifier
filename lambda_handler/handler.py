import json
import os
from speaker_role_classifier.classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError
)

def lambda_handler(event, context):
    """
    AWS Lambda handler for the Speaker Role Classifier.
    Expects a JSON body with a 'transcript' field and optional 'target_roles' field.
    """
    try:
        # Handle both Function URL and direct invocation formats
        if 'body' in event and event['body'] is not None:
            body = json.loads(event['body'])
        else:
            body = event  # Direct invocation

        transcript = body.get('transcript')
        target_roles = body.get('target_roles')  # Optional

        if transcript is None:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing required field: transcript',
                    'message': 'Request body must include a "transcript" field with the diarized transcript text'
                })
            }

        if not transcript.strip():
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Empty transcript',
                    'message': 'The transcript field cannot be empty'
                })
            }

        # Classify speakers (returns dict with transcript and log)
        result = classify_speakers(transcript, target_roles=target_roles)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'transcript': result['transcript'],
                'log': result['log']
            })
        }

    except InvalidJSONResponseError as e:
        return {
            'statusCode': 422,  # Unprocessable Entity
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Invalid API Response',
                'message': str(e)
            })
        }
    except (MissingSpeakerMappingError, SpeakerNotFoundError) as e:
        return {
            'statusCode': 422,  # Unprocessable Entity
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Speaker Classification Error',
                'message': str(e)
            })
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON'
            })
        }
    except Exception as e:
        print(f"Unhandled error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred.'
            })
        }
