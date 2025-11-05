"""Command-line interface for speaker role classifier."""

import sys
import click
from .classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError,
)


@click.command()
@click.argument('input_file', type=click.File('r'), default='-')
@click.argument('output_file', type=click.File('w'), default='-')
def main(input_file, output_file):
    """
    Classify speakers in a diarized call center transcript.
    
    Reads a transcript with generic speaker labels (Speaker 0, Speaker 1, etc.)
    and outputs the transcript with speakers labeled as Agent or Customer.
    
    INPUT_FILE: Path to input transcript file (use '-' for stdin)
    OUTPUT_FILE: Path to output file (use '-' for stdout)
    
    Examples:
    
        # Process a file
        speaker-role-classifier input.txt output.txt
        
        # Use stdin/stdout
        cat input.txt | speaker-role-classifier - -
        
        # Read from file, write to stdout
        speaker-role-classifier input.txt -
    """
    try:
        # Read the input transcript
        transcript = input_file.read()
        
        if not transcript.strip():
            click.echo("Error: Input transcript is empty", err=True)
            sys.exit(1)
        
        # Classify speakers
        result = classify_speakers(transcript)
        
        # Write the output
        output_file.write(result)
        
        # Only show success message if not writing to stdout
        if output_file.name != '<stdout>':
            click.echo(f"Successfully classified speakers. Output written to {output_file.name}")
    
    except InvalidJSONResponseError as e:
        click.echo(f"Error: Invalid response from API - {e}", err=True)
        sys.exit(2)
    
    except MissingSpeakerMappingError as e:
        click.echo(f"Error: Not all speakers were mapped - {e}", err=True)
        sys.exit(3)
    
    except SpeakerNotFoundError as e:
        click.echo(f"Error: Speaker not found in transcript - {e}", err=True)
        sys.exit(4)
    
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(5)
    
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(99)


if __name__ == '__main__':
    main()

