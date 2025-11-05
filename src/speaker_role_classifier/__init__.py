"""Speaker Role Classifier - Identify agents and customers in call center transcripts."""

from .classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError,
)

__version__ = "0.1.0"

__all__ = [
    "classify_speakers",
    "InvalidJSONResponseError",
    "MissingSpeakerMappingError",
    "SpeakerNotFoundError",
]

