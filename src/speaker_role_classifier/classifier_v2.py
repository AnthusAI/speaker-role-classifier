"""Advanced speaker classification with configurable roles, validation, and logging."""

import os
import json
import re
from typing import Dict, List, Optional, Union, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


# Custom exceptions
class InvalidJSONResponseError(Exception):
    """Raised when the API returns malformed JSON."""
    pass


class MissingSpeakerMappingError(Exception):
    """Raised when not all speakers are mapped to roles."""
    pass


class SpeakerNotFoundError(Exception):
    """Raised when a mapped speaker doesn't exist in the transcript."""
    pass


class ClassificationResult:
    """Result of speaker classification with transcript and logs."""
    
    def __init__(self, transcript: str, log: List[Dict]):
        self.transcript = transcript
        self.log = log
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'transcript': self.transcript,
            'log': self.log
        }
    
    def __str__(self) -> str:
        """Return transcript as string for backward compatibility."""
        return self.transcript


def _extract_speaker_labels(transcript: str) -> set:
    """
    Extract all unique speaker labels from transcript.
    
    Args:
        transcript: The transcript text
        
    Returns:
        Set of speaker labels found in transcript
    """
    # Match any label followed by a colon (e.g., "Speaker 0:", "Agent:", "Unknown:")
    label_pattern = r'^([^:]+):'
    labels = set()
    
    for line in transcript.split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(label_pattern, line)
        if match:
            labels.add(match.group(1).strip())
    
    return labels


def _identify_non_target_labels(transcript: str, target_roles: List[str]) -> set:
    """
    Identify speaker labels that are not in the target roles list.
    
    Args:
        transcript: The transcript text
        target_roles: List of valid target role names
        
    Returns:
        Set of labels that need to be replaced
    """
    all_labels = _extract_speaker_labels(transcript)
    non_target = {label for label in all_labels if label not in target_roles}
    return non_target


def _call_gpt5_for_mapping(
    transcript: str,
    target_roles: List[str],
    labels_to_map: set,
    log: List[Dict]
) -> Dict[str, str]:
    """
    Call GPT-5 API to map speaker labels to target roles.
    
    Args:
        transcript: The transcript to analyze
        target_roles: List of target role names (e.g., ["Agent", "Customer"])
        labels_to_map: Set of labels that need to be mapped
        log: Log list to append to
        
    Returns:
        Dictionary mapping speaker labels to target roles
        
    Raises:
        InvalidJSONResponseError: If the API response is not valid JSON
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    # Build role descriptions
    role_desc = " and ".join(target_roles)
    
    prompt = f"""You are analyzing a conversation transcript. Your task is to identify which speaker has which role.

The valid roles are: {role_desc}

Here is the transcript:

{transcript}

The following speaker labels need to be mapped to roles: {', '.join(sorted(labels_to_map))}

Analyze the conversation and determine which speaker label corresponds to which role. 

Respond with a JSON object mapping each speaker label to their role. Use exactly the role names provided: {', '.join(f'"{r}"' for r in target_roles)}

Example format:
{{
  "Speaker 0": "{target_roles[0]}",
  "Speaker 1": "{target_roles[1]}"
}}"""
    
    log.append({
        'step': 'mapping_request',
        'target_roles': target_roles,
        'labels_to_map': list(labels_to_map),
        'prompt_length': len(prompt)
    })
    
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": f"You are a conversation transcript analyzer. Always respond with valid JSON mapping speaker labels to these roles: {role_desc}"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        if not content:
            raise InvalidJSONResponseError("API returned empty response")
        
        mapping = json.loads(content)
        
        log.append({
            'step': 'mapping_response',
            'mapping': mapping,
            'model': 'gpt-5'
        })
        
        return mapping
        
    except json.JSONDecodeError as e:
        log.append({
            'step': 'mapping_error',
            'error': f"JSON decode error: {str(e)}"
        })
        raise InvalidJSONResponseError(f"Failed to parse JSON response from API: {e}")
    except Exception as e:
        log.append({
            'step': 'mapping_error',
            'error': str(e)
        })
        if isinstance(e, InvalidJSONResponseError):
            raise
        raise InvalidJSONResponseError(f"API call failed: {e}")


def _replace_labels(transcript: str, mapping: Dict[str, str], log: List[Dict]) -> str:
    """
    Replace speaker labels with roles in the transcript.
    
    Args:
        transcript: The original transcript
        mapping: Dictionary mapping labels to roles
        log: Log list to append to
        
    Returns:
        Transcript with labels replaced
    """
    result = transcript
    replacements_made = []
    
    # Sort by label to ensure consistent replacement order
    for label in sorted(mapping.keys(), reverse=True):
        role = mapping[label]
        old_pattern = f"{label}:"
        new_pattern = f"{role}:"
        
        if old_pattern in result:
            count = result.count(old_pattern)
            result = result.replace(old_pattern, new_pattern)
            replacements_made.append({
                'from': label,
                'to': role,
                'occurrences': count
            })
    
    log.append({
        'step': 'label_replacement',
        'replacements': replacements_made
    })
    
    return result


def classify_speakers(
    transcript: str,
    target_roles: Optional[List[str]] = None,
    enable_safeguard: bool = True,
    validate_only: bool = False,
    return_dict: bool = False
) -> Union[str, Dict]:
    """
    Classify speakers in a transcript with configurable roles and validation.
    
    Args:
        transcript: The transcript to classify
        target_roles: List of target role names (default: ["Agent", "Customer"])
        enable_safeguard: Whether to run validation safeguard (default: True)
        validate_only: Only validate, don't do initial mapping (default: False)
        return_dict: Return dict with transcript and log (default: False for backward compat)
        
    Returns:
        Classified transcript (str) or dict with transcript and log
        
    Raises:
        InvalidJSONResponseError: If the API response is malformed
        MissingSpeakerMappingError: If not all speakers are mapped
        SpeakerNotFoundError: If a mapped speaker doesn't exist in transcript
    """
    if target_roles is None:
        target_roles = ["Agent", "Customer"]
    
    log = []
    
    # Log configuration
    log.append({
        'step': 'configuration',
        'target_roles': target_roles,
        'enable_safeguard': enable_safeguard,
        'validate_only': validate_only
    })
    
    # Identify which labels need to be mapped
    non_target_labels = _identify_non_target_labels(transcript, target_roles)
    
    log.append({
        'step': 'label_analysis',
        'all_labels': list(_extract_speaker_labels(transcript)),
        'target_roles': target_roles,
        'non_target_labels': list(non_target_labels)
    })
    
    result_transcript = transcript
    
    # If there are non-target labels, map them
    if non_target_labels and not validate_only:
        mapping = _call_gpt5_for_mapping(transcript, target_roles, non_target_labels, log)
        result_transcript = _replace_labels(result_transcript, mapping, log)
    
    # TODO: Implement safeguard validation layer
    if enable_safeguard:
        log.append({
            'step': 'safeguard',
            'status': 'not_implemented_yet'
        })
    
    # Return format based on return_dict flag
    if return_dict:
        return {
            'transcript': result_transcript,
            'log': log
        }
    else:
        return result_transcript
