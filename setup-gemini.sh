#!/bin/bash

# Gemini CLI Setup Script
# Run this after getting your API key from https://aistudio.google.com/app/apikey

echo "🚀 Setting up Gemini CLI for your AI workflow..."

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your API key as an argument:"
    echo "   ./setup-gemini.sh your-api-key-here"
    echo ""
    echo "Get your free API key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

API_KEY="$1"

# Create config directory
mkdir -p ~/.gemini

# Create settings file
echo "{\"auth\": {\"apiKey\": \"$API_KEY\"}}" > ~/.gemini/settings.json

echo "✅ Gemini CLI configured successfully!"
echo ""
echo "🧪 Testing your setup..."

# Test the configuration
cd /root/overview/my-ai-workflow
gemini "Hello! Can you read setup.md and tell me you understand my workflow preferences?"

echo ""
echo "🎉 If you see a response above, your Gemini CLI is working!"
echo "Now you can use: gemini \"activate the [workflow-name] workflow\""