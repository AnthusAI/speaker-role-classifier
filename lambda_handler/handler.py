"""AWS Lambda handler for speaker role classifier."""

import json
import os
from speaker_role_classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError,
)


def lambda_handler(event, context):
    """
    AWS Lambda handler for HTTP requests via Function URL.
    
    Expects POST request with JSON body:
    {
        "transcript": "Speaker 0: Hello...\nSpeaker 1: Hi..."
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "result": "Agent: Hello...\nCustomer: Hi..."
        }
    }
    """
    try:
        # Parse the request body
        if 'body' in event:
            # Function URL format
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation format
            body = event
        
        # Validate input
        if 'transcript' not in body:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing required field: transcript',
                    'message': 'Request body must include a "transcript" field with the diarized transcript text'
                })
            }
        
        transcript = body['transcript']
        
        if not transcript or not transcript.strip():
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Empty transcript',
                    'message': 'The transcript field cannot be empty'
                })
            }
        
        # Classify the speakers
        result = classify_speakers(transcript)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'result': result
            })
        }
    
    except InvalidJSONResponseError as e:
        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'API Error',
                'message': f'Invalid response from OpenAI API: {str(e)}'
            })
        }
    
    except MissingSpeakerMappingError as e:
        return {
            'statusCode': 422,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Missing Speaker Mapping',
                'message': str(e)
            })
        }
    
    except SpeakerNotFoundError as e:
        return {
            'statusCode': 422,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Speaker Not Found',
                'message': str(e)
            })
        }
    
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Invalid JSON',
                'message': f'Request body must be valid JSON: {str(e)}'
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }

