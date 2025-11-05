#!/bin/bash
# Test the deployed Lambda function

# Set your Function URL here
FUNCTION_URL="https://2xvfxghbpy44ix7uoksb45obpa0pfegw.lambda-url.us-east-1.on.aws/"

echo "Testing Lambda Function URL..."
echo "URL: $FUNCTION_URL"
echo ""

# Test 1: Realistic multi-turn conversation
echo "Test 1: Realistic multi-turn conversation"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nSpeaker 1: Hi Jennifer, yes it'\''s 555-0147.\nSpeaker 0: Thank you. I see you'\''re calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nSpeaker 1: Yes, that'\''s correct. We have an emergency situation in one of our units.\nSpeaker 0: I'\''m sorry to hear that. Which unit is experiencing the problem?\nSpeaker 1: It'\''s unit 3B. The tenant just called me - their kitchen sink is completely backed up and water is overflowing onto the floor."}' \
  | python3 -m json.tool

echo -e "\n\n"

# Test 2: Error case - missing transcript
echo "Test 2: Error case - missing transcript"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -m json.tool

echo -e "\n\n"

# Test 3: Error case - empty transcript
echo "Test 3: Error case - empty transcript"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{"transcript": ""}' \
  | python3 -m json.tool

echo -e "\n"
echo "Testing complete!"

