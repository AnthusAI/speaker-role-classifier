import click
from .classifier import classify_speakers

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
@click.option('--target-roles', multiple=True, help='Target role names (e.g., --target-roles Sales --target-roles Lead)')
@click.option('--safeguard/--no-safeguard', default=False, help='Enable safeguard validation layer to check for misclassifications.')
def main(input_file, output_file, target_roles, safeguard):
    """Classify speaker roles in a transcript."""
    transcript = input_file.read()
    try:
        # Convert target_roles tuple to list if provided
        roles_list = list(target_roles) if target_roles else None
        
        result = classify_speakers(
            transcript,
            target_roles=roles_list,
            enable_safeguard=safeguard
        )
        
        # Write just the transcript to the output file
        output_file.write(result['transcript'])
        click.echo("Classification successful. Output saved.")
        
        # Show safeguard activity if enabled
        if safeguard:
            corrections = [e for e in result['log'] if e.get('step') == 'utterance_corrected']
            if corrections:
                click.echo(f"\nSafeguard made {len(corrections)} correction(s):")
                for c in corrections:
                    click.echo(f"  Line {c['line_index']}: {c['old_role']} → {c['new_role']}")
            else:
                click.echo("\nSafeguard validation: No corrections needed.")
                
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    main()
