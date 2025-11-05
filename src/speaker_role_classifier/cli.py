import click
from .classifier import classify_speakers

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
@click.option('--target-roles', multiple=True, help='Target role names (e.g., --target-roles Sales --target-roles Lead)')
def main(input_file, output_file, target_roles):
    """Classify speaker roles in a transcript."""
    transcript = input_file.read()
    try:
        # Convert target_roles tuple to list if provided
        roles_list = list(target_roles) if target_roles else None
        
        result = classify_speakers(transcript, target_roles=roles_list)
        
        # Write just the transcript to the output file
        output_file.write(result['transcript'])
        click.echo("Classification successful. Output saved.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    main()
