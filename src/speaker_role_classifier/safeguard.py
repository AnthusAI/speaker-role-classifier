"""Safeguard validation layer with tool calling for spot corrections."""

import json
import re
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
import os


def _find_utterance_by_prefix(transcript: str, current_role: str, utterance_prefix: str, max_words: int = 10) -> Optional[Tuple[int, str]]:
    """
    Find a specific utterance in the transcript by role and text prefix.
    
    Args:
        transcript: The full transcript
        current_role: The current (possibly incorrect) role label
        utterance_prefix: First few words of the utterance
        max_words: Maximum words to match
        
    Returns:
        Tuple of (line_index, full_line) if found, None otherwise
    """
    lines = transcript.split('\n')
    
    # Normalize the prefix for matching
    prefix_words = utterance_prefix.strip().lower().split()[:max_words]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with the current role
        if line.startswith(f"{current_role}:"):
            # Extract the text after the role label
            text_after_role = line[len(f"{current_role}:"):].strip()
            text_words = text_after_role.lower().split()[:max_words]
            
            # Check if the prefix matches
            if text_words[:len(prefix_words)] == prefix_words:
                return (i, line)
    
    return None


def _correct_single_utterance(transcript: str, line_index: int, old_role: str, new_role: str, log: List[Dict]) -> str:
    """
    Correct a single utterance by replacing its role label.
    
    Args:
        transcript: The full transcript
        line_index: Index of the line to correct
        old_role: Current (incorrect) role
        new_role: Correct role
        log: Log list to append to
        
    Returns:
        Corrected transcript
    """
    lines = transcript.split('\n')
    
    if line_index >= len(lines):
        log.append({
            'step': 'correction_error',
            'error': f'Line index {line_index} out of range'
        })
        return transcript
    
    old_line = lines[line_index]
    new_line = old_line.replace(f"{old_role}:", f"{new_role}:", 1)
    lines[line_index] = new_line
    
    log.append({
        'step': 'utterance_corrected',
        'line_index': line_index,
        'old_role': old_role,
        'new_role': new_role,
        'old_line': old_line,
        'new_line': new_line
    })
    
    return '\n'.join(lines)


def run_safeguard_validation(transcript: str, target_roles: List[str], log: List[Dict]) -> str:
    """
    Run safeguard validation with tool calling to spot-check and correct misclassifications.
    
    Args:
        transcript: The classified transcript to validate
        target_roles: List of valid target role names
        log: Log list to append to
        
    Returns:
        Validated and corrected transcript
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    log.append({
        'step': 'safeguard_start',
        'target_roles': target_roles
    })
    
    # Define the correction tool
    tools = [{
        "type": "function",
        "function": {
            "name": "correct_speaker_role",
            "description": "Correct a single misclassified utterance by specifying its current (wrong) role and the beginning of the utterance text. Use this when you identify a speaker role that seems incorrect based on the conversation context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_role": {
                        "type": "string",
                        "description": f"The current (incorrect) role label on the utterance. Must be one of: {', '.join(target_roles)}"
                    },
                    "utterance_prefix": {
                        "type": "string",
                        "description": "The first 5-10 words of the utterance text (after the role label). This helps locate the specific utterance."
                    },
                    "correct_role": {
                        "type": "string",
                        "description": f"The correct role this utterance should have. Must be one of: {', '.join(target_roles)}"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why this utterance is misclassified"
                    }
                },
                "required": ["current_role", "utterance_prefix", "correct_role", "reason"]
            }
        }
    }]
    
    role_desc = " and ".join(target_roles)
    
    prompt = f"""You are validating speaker role classifications in a conversation transcript. The valid roles are: {role_desc}

Here is the classified transcript:

{transcript}

Review this transcript carefully. Look for any utterances that seem misclassified based on:
- The content of what they're saying
- The conversational context and flow
- Typical patterns (e.g., agents greet customers, customers describe problems)

If you find any misclassified utterances, use the correct_speaker_role function to fix them. Provide the current (wrong) role, the first 5-10 words of the utterance, the correct role, and your reasoning.

If everything looks correct, simply respond that the classification is accurate."""
    
    max_iterations = 3  # Prevent infinite loops
    current_transcript = transcript
    corrections_made = []
    
    for iteration in range(max_iterations):
        log.append({
            'step': 'safeguard_iteration',
            'iteration': iteration + 1
        })
        
        try:
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"You are a conversation analyst validating speaker role classifications. The valid roles are: {role_desc}. Use the correct_speaker_role function to fix any misclassifications you identify."},
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Check if LLM wants to call tools
            if message.tool_calls:
                log.append({
                    'step': 'tool_calls_requested',
                    'count': len(message.tool_calls)
                })
                
                tool_results = []
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    log.append({
                        'step': 'tool_call',
                        'function': function_name,
                        'arguments': function_args
                    })
                    
                    if function_name == "correct_speaker_role":
                        current_role = function_args.get('current_role')
                        utterance_prefix = function_args.get('utterance_prefix')
                        correct_role = function_args.get('correct_role')
                        reason = function_args.get('reason')
                        
                        # Try to find and correct the utterance
                        found = _find_utterance_by_prefix(
                            current_transcript,
                            current_role,
                            utterance_prefix
                        )
                        
                        if found:
                            line_index, full_line = found
                            current_transcript = _correct_single_utterance(
                                current_transcript,
                                line_index,
                                current_role,
                                correct_role,
                                log
                            )
                            
                            corrections_made.append({
                                'current_role': current_role,
                                'correct_role': correct_role,
                                'reason': reason
                            })
                            
                            tool_result = {
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({
                                    "success": True,
                                    "message": f"Successfully corrected utterance from {current_role} to {correct_role}"
                                })
                            }
                        else:
                            log.append({
                                'step': 'utterance_not_found',
                                'current_role': current_role,
                                'prefix': utterance_prefix
                            })
                            
                            tool_result = {
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({
                                    "success": False,
                                    "message": f"Could not locate utterance with role '{current_role}' and prefix '{utterance_prefix}'. Please provide more specific text or check the role label."
                                })
                            }
                        
                        tool_results.append(tool_result)
                
                # If we made corrections, continue to next iteration to check if more needed
                if corrections_made and iteration < max_iterations - 1:
                    # Update prompt with corrected transcript for next iteration
                    prompt = f"""Here is the updated transcript after corrections:

{current_transcript}

Review again. Are there any remaining misclassifications? If so, correct them. If everything is now correct, confirm that the classification is accurate."""
                    continue
                else:
                    # No more corrections or max iterations reached
                    break
            else:
                # No tool calls, LLM thinks everything is correct
                log.append({
                    'step': 'safeguard_complete',
                    'message': 'No corrections needed' if not corrections_made else 'All corrections completed',
                    'total_corrections': len(corrections_made)
                })
                break
                
        except Exception as e:
            log.append({
                'step': 'safeguard_error',
                'error': str(e)
            })
            # Return the best transcript we have so far
            break
    
    log.append({
        'step': 'safeguard_end',
        'corrections_made': corrections_made,
        'total_corrections': len(corrections_made)
    })
    
    return current_transcript
