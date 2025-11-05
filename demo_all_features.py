#!/usr/bin/env python3
"""
Demonstration of all Speaker Role Classifier features.
"""

from speaker_role_classifier import classify_speakers
import json

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def demo_basic_classification():
    print_section("1. Basic Classification (Default Roles)")
    
    transcript = """Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services.
Speaker 1: Hi, I need help with a plumbing issue."""
    
    print("Input:")
    print(transcript)
    
    result = classify_speakers(transcript)
    
    print("\nOutput:")
    print(result['transcript'])
    print(f"\nLog entries: {len(result['log'])}")

def demo_custom_roles():
    print_section("2. Custom Role Names (Sales/Lead)")
    
    transcript = """Speaker 0: Hello, thanks for your interest in our product.
Speaker 1: Hi, I'd like to learn more about your services."""
    
    print("Input:")
    print(transcript)
    
    result = classify_speakers(
        transcript,
        target_roles=['Sales', 'Lead']
    )
    
    print("\nOutput:")
    print(result['transcript'])

def demo_mixed_labels():
    print_section("3. Mixed Speaker Labels")
    
    transcript = """Speaker 0: Good morning.
Unknown: Hi there.
Speaker 1: How can I help?
Speaker 0: I need assistance."""
    
    print("Input:")
    print(transcript)
    
    result = classify_speakers(transcript)
    
    print("\nOutput:")
    print(result['transcript'])
    
    # Show label analysis from log
    label_analysis = next(e for e in result['log'] if e.get('step') == 'label_analysis')
    print(f"\nFound labels: {label_analysis.get('found_labels')}")

def demo_safeguard_no_corrections():
    print_section("4. Safeguard Validation (Correct Classification)")
    
    transcript = """Speaker 0: Good afternoon, how may I help you?
Speaker 1: Hi, I need assistance with my account."""
    
    print("Input:")
    print(transcript)
    
    result = classify_speakers(transcript, enable_safeguard=True)
    
    print("\nOutput:")
    print(result['transcript'])
    
    corrections = [e for e in result['log'] if e.get('step') == 'utterance_corrected']
    print(f"\nSafeguard corrections: {len(corrections)}")
    print("✓ Classification was accurate, no corrections needed")

def demo_safeguard_with_corrections():
    print_section("5. Safeguard Validation (With Corrections)")
    
    # Intentionally misclassified transcript
    transcript = """Agent: Hi, I'm calling about my account.
Customer: Good afternoon, thank you for calling. How can I help you?
Agent: My password isn't working.
Customer: Let me reset that for you."""
    
    print("Input (intentionally misclassified):")
    print(transcript)
    
    result = classify_speakers(
        transcript,
        target_roles=['Agent', 'Customer'],
        enable_safeguard=True
    )
    
    print("\nOutput (after safeguard):")
    print(result['transcript'])
    
    corrections = [e for e in result['log'] if e.get('step') == 'utterance_corrected']
    print(f"\nSafeguard made {len(corrections)} correction(s):")
    for c in corrections:
        print(f"  Line {c['line_index']}: {c['old_role']} → {c['new_role']}")
        print(f"    Reason: {c.get('reason', 'N/A')}")

def demo_structured_logging():
    print_section("6. Structured Logging")
    
    transcript = """Speaker 0: Hello.
Speaker 1: Hi."""
    
    result = classify_speakers(transcript, enable_safeguard=True)
    
    print("Log structure:")
    for entry in result['log']:
        step = entry.get('step')
        print(f"\n  {step}:")
        # Show key fields for each step
        if step == 'configuration':
            print(f"    - target_roles: {entry.get('target_roles')}")
            print(f"    - enable_safeguard: {entry.get('enable_safeguard')}")
        elif step == 'label_analysis':
            print(f"    - found_labels: {entry.get('found_labels')}")
        elif step == 'mapping_decision':
            print(f"    - mapping: {entry.get('mapping')}")
        elif step == 'safeguard_end':
            print(f"    - total_corrections: {entry.get('total_corrections')}")

def main():
    print("\n" + "="*70)
    print("  SPEAKER ROLE CLASSIFIER - FEATURE DEMONSTRATION")
    print("="*70)
    
    try:
        demo_basic_classification()
        demo_custom_roles()
        demo_mixed_labels()
        demo_safeguard_no_corrections()
        demo_safeguard_with_corrections()
        demo_structured_logging()
        
        print("\n" + "="*70)
        print("  All demonstrations completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
