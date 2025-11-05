"""Core speaker classification logic."""

import os
import json
import re
from typing import Dict
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


def _call_gpt5_api(transcript: str) -> Dict[str, str]:
    """
    Call GPT-5 API to classify speakers.
    
    Args:
        transcript: The diarized transcript to classify
        
    Returns:
        Dictionary mapping speaker labels to roles (Agent/Customer)
        
    Raises:
        InvalidJSONResponseError: If the API response is not valid JSON
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are analyzing a call center transcript. Your task is to identify which speaker is the agent (call center representative) and which is the customer.

Here is the transcript:

{transcript}

Analyze the conversation and determine which speaker is the agent and which is the customer. The agent typically:
- Greets the caller with a company name
- Offers help or asks how they can assist
- Uses professional language
- Responds to the customer's needs

Respond with a JSON object mapping each speaker label to their role. Use exactly "Agent" or "Customer" as the role values.

Example format:
{{
  "Speaker 0": "Agent",
  "Speaker 1": "Customer"
}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a call center transcript analyzer. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        if not content:
            raise InvalidJSONResponseError("API returned empty response")
        
        mapping = json.loads(content)
        return mapping
        
    except json.JSONDecodeError as e:
        raise InvalidJSONResponseError(f"Failed to parse JSON response from API: {e}")
    except Exception as e:
        if isinstance(e, InvalidJSONResponseError):
            raise
        raise InvalidJSONResponseError(f"API call failed: {e}")


def _validate_mapping(transcript: str, mapping: Dict[str, str]) -> None:
    """
    Validate that the speaker mapping is complete and correct.
    
    Args:
        transcript: The original transcript
        mapping: Dictionary mapping speaker labels to roles
        
    Raises:
        MissingSpeakerMappingError: If not all speakers are mapped
        SpeakerNotFoundError: If a mapped speaker doesn't exist in transcript
    """
    # Extract all unique speaker labels from the transcript
    speaker_pattern = r'^(Speaker \d+):'
    speakers_in_transcript = set()
    
    for line in transcript.split('\n'):
        match = re.match(speaker_pattern, line.strip())
        if match:
            speakers_in_transcript.add(match.group(1))
    
    # Check if all speakers in transcript are mapped
    speakers_in_mapping = set(mapping.keys())
    
    unmapped_speakers = speakers_in_transcript - speakers_in_mapping
    if unmapped_speakers:
        raise MissingSpeakerMappingError(
            f"Not all speakers are mapped. Missing: {', '.join(sorted(unmapped_speakers))}"
        )
    
    # Check if any mapped speakers don't exist in transcript
    extra_speakers = speakers_in_mapping - speakers_in_transcript
    if extra_speakers:
        raise SpeakerNotFoundError(
            f"Mapped speakers not found in transcript: {', '.join(sorted(extra_speakers))}"
        )


def _replace_speakers(transcript: str, mapping: Dict[str, str]) -> str:
    """
    Replace speaker labels with roles in the transcript.
    
    Args:
        transcript: The original transcript with speaker labels
        mapping: Dictionary mapping speaker labels to roles
        
    Returns:
        Transcript with speaker labels replaced by roles
    """
    result = transcript
    
    # Replace each speaker label with its role
    # Sort by speaker label to ensure consistent replacement order
    for speaker_label in sorted(mapping.keys(), reverse=True):
        role = mapping[speaker_label]
        # Replace "Speaker N:" with "Role:"
        result = result.replace(f"{speaker_label}:", f"{role}:")
    
    return result


def classify_speakers(transcript: str) -> str:
    """
    Classify speakers in a diarized transcript as Agent or Customer.
    
    Args:
        transcript: A diarized transcript with speaker labels (e.g., "Speaker 0: text")
        
    Returns:
        The transcript with speaker labels replaced by roles (Agent/Customer)
        
    Raises:
        InvalidJSONResponseError: If the API response is malformed
        MissingSpeakerMappingError: If not all speakers are mapped
        SpeakerNotFoundError: If a mapped speaker doesn't exist in transcript
        
    Example:
        >>> transcript = "Speaker 0: Hello\\nSpeaker 1: Hi"
        >>> result = classify_speakers(transcript)
        >>> print(result)
        Agent: Hello
        Customer: Hi
    """
    # Step 1: Call the API to get speaker-to-role mapping
    mapping = _call_gpt5_api(transcript)
    
    # Step 2: Validate the mapping
    _validate_mapping(transcript, mapping)
    
    # Step 3: Replace speaker labels with roles
    result = _replace_speakers(transcript, mapping)
    
    return result

