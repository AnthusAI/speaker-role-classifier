"""Core speaker classification logic with configurable roles and logging."""

import os
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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


def _extract_speaker_labels(transcript: str) -> set:
    """Extract all unique speaker labels from transcript."""
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
    """Identify speaker labels that are not in the target roles list."""
    all_labels = _extract_speaker_labels(transcript)
    non_target = {label for label in all_labels if label not in target_roles}
    return non_target


def _call_gpt5_api(transcript: str, target_roles: List[str], labels_to_map: set, log: List[Dict]) -> Dict[str, str]:
    """
    Call GPT-5 API to map speaker labels to target roles.
    
    Args:
        transcript: The transcript to analyze
        target_roles: List of target role names
        labels_to_map: Set of labels that need to be mapped
        log: Log list to append to
        
    Returns:
        Dictionary mapping speaker labels to target roles
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    role_desc = " and ".join(target_roles)
    labels_str = ', '.join(sorted(labels_to_map))
    
    prompt = f"""You are analyzing a conversation transcript. Your task is to identify which speaker has which role.

The valid roles are: {role_desc}

Here is the transcript:

{transcript}

The following speaker labels need to be mapped to roles: {labels_str}

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
        'labels_to_map': list(labels_to_map)
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
            'step': 'mapping_decision',
            'mapping': mapping
        })
        
        return mapping
        
    except json.JSONDecodeError as e:
        log.append({'step': 'error', 'error': f"JSON decode error: {str(e)}"})
        raise InvalidJSONResponseError(f"Failed to parse JSON response from API: {e}")
    except Exception as e:
        log.append({'step': 'error', 'error': str(e)})
        if isinstance(e, InvalidJSONResponseError):
            raise
        raise InvalidJSONResponseError(f"API call failed: {e}")


def _validate_mapping(transcript: str, mapping: Dict[str, str], target_roles: List[str]) -> None:
    """Validate that the speaker mapping is complete and correct."""
    non_target_labels = _identify_non_target_labels(transcript, target_roles)
    speakers_in_mapping = set(mapping.keys())
    
    unmapped_speakers = non_target_labels - speakers_in_mapping
    if unmapped_speakers:
        raise MissingSpeakerMappingError(
            f"Not all speakers are mapped. Missing: {', '.join(sorted(unmapped_speakers))}"
        )
    
    all_labels = _extract_speaker_labels(transcript)
    extra_speakers = speakers_in_mapping - all_labels
    if extra_speakers:
        raise SpeakerNotFoundError(
            f"Mapped speakers not found in transcript: {', '.join(sorted(extra_speakers))}"
        )


def _replace_speakers(transcript: str, mapping: Dict[str, str], log: List[Dict]) -> str:
    """Replace speaker labels with roles in the transcript."""
    result = transcript
    replacements_made = []
    
    for speaker_label in sorted(mapping.keys(), reverse=True):
        role = mapping[speaker_label]
        old_pattern = f"{speaker_label}:"
        new_pattern = f"{role}:"
        
        if old_pattern in result:
            count = result.count(old_pattern)
            result = result.replace(old_pattern, new_pattern)
            replacements_made.append({
                'from': speaker_label,
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
    enable_safeguard: bool = False
) -> Dict:
    """
    Classify speakers in a transcript with configurable roles and logging.
    
    Args:
        transcript: The transcript to classify
        target_roles: List of target role names (default: ["Agent", "Customer"])
        enable_safeguard: Whether to run validation safeguard (default: False)
        
    Returns:
        Dict with 'transcript' (classified text) and 'log' (list of log entries)
    """
    if target_roles is None:
        target_roles = ["Agent", "Customer"]
    
    log = []
    
    log.append({
        'step': 'configuration',
        'target_roles': target_roles,
        'enable_safeguard': enable_safeguard
    })
    
    non_target_labels = _identify_non_target_labels(transcript, target_roles)
    
    log.append({
        'step': 'label_analysis',
        'all_labels': list(_extract_speaker_labels(transcript)),
        'target_roles': target_roles,
        'non_target_labels': list(non_target_labels)
    })
    
    result_transcript = transcript
    
    if non_target_labels:
        mapping = _call_gpt5_api(transcript, target_roles, non_target_labels, log)
        _validate_mapping(transcript, mapping, target_roles)
        result_transcript = _replace_speakers(transcript, mapping, log)
    
    if enable_safeguard:
        log.append({
            'step': 'safeguard',
            'status': 'not_yet_implemented'
        })
    
    return {
        'transcript': result_transcript,
        'log': log
    }
