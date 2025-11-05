#!/bin/bash
# Send a transcript file to the Lambda function

if [ $# -eq 0 ]; then
    echo "Usage: $0 <transcript_file>"
    echo "Example: $0 example_transcript.txt"
    exit 1
fi

FUNCTION_URL="https://2xvfxghbpy44ix7uoksb45obpa0pfegw.lambda-url.us-east-1.on.aws/"
TRANSCRIPT_FILE="$1"

if [ ! -f "$TRANSCRIPT_FILE" ]; then
    echo "Error: File '$TRANSCRIPT_FILE' not found"
    exit 1
fi

echo "Sending $TRANSCRIPT_FILE to Lambda function..."
echo ""

# Read file and create JSON payload
TRANSCRIPT_CONTENT=$(cat "$TRANSCRIPT_FILE" | jq -Rs .)

# Send to Lambda
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d "{\"transcript\": $TRANSCRIPT_CONTENT}" \
  | python3 -m json.tool

echo ""

