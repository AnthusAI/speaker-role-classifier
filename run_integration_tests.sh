#!/bin/bash

# Script to run integration tests with real OpenAI API calls
# Usage: ./run_integration_tests.sh

echo "================================================"
echo "Running Integration Tests with Real OpenAI API"
echo "================================================"
echo ""
echo "⚠️  Warning: This will make real API calls to OpenAI"
echo "   - Requires OPENAI_API_KEY in .env"
echo "   - Will cost money (GPT-5 API calls)"
echo "   - Takes 10-15 minutes to complete"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Starting integration tests..."
echo ""

export REAL_API_TESTS=1
pytest tests/ -v --tb=short

echo ""
echo "================================================"
echo "Integration Tests Complete"
echo "================================================"
