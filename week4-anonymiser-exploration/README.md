# AICE Anonymiser Demo

A demonstration text anonymization service built with FastAPI and Presidio, showcasing reversible PII (Personally Identifiable Information) anonymization.

## Features

- **Text Anonymization**: Automatically detect and anonymize sensitive data
- **Reversible Anonymization**: Restore original text using session-based mappings
- **Batch Processing**: Anonymize multiple texts concurrently
- **Session Management**: Persistent storage of anonymization mappings
- **Custom Entity Handling**: Special handling for predefined names and organizations
- **REST API**: Modern FastAPI-based web service

## Quick Start

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Run the service (development with auto-reload)
./dev.sh

# Or run without auto-reload
./serve.sh
```

### Using Docker (if you have python env challenges)

```bash
# Build the image
docker build -t aice-anonymiser .

# Run the container
docker run -p 9000:9000 -v $(pwd)/data:/app/data aice-anonymiser
```

## API Endpoints

### Anonymize Text
```bash
curl -X POST "http://localhost:9000/anonymise" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Smith works at Acme Corp. His email is john@example.com"
  }'
```

### Batch Anonymize
```bash
curl -X POST "http://localhost:9000/anonymise_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Jane Doe's phone is 555-1234",
      "Contact Smith at smith@example.com"
    ]
  }'
```

### De-anonymize Text
```bash
curl -X POST "http://localhost:9000/deanonymise" \
  -H "Content-Type: application/json" \
  -d '{
    "anonymised_text": "<PERSON> works at <ORGANIZATION>. His email is <EMAIL>",
    "session_id": "your-session-id"
  }'
```

### Health Check
```bash
curl "http://localhost:9000/health"
```

## How It Works

1. **Entity Detection**: Uses SpaCy and Presidio to identify PII entities
2. **Custom Preprocessing**: Replaces predefined names with placeholders
3. **Anonymization**: Replaces detected entities with type tags (e.g., `<PERSON>`)
4. **Session Storage**: Saves mappings to disk for later reversal
5. **De-anonymization**: Restores original values using stored mappings

## Architecture

- **FastAPI**: Async web framework for high performance
- **Presidio**: Microsoft's data protection SDK
- **SpaCy**: NLP model for entity recognition
- **LangChain**: Provides reversible anonymization wrapper
- **ThreadPoolExecutor**: Parallel processing for batch operations

## Development

```bash
# Run with auto-reload for development
./dev.sh

# Or run without auto-reload
./serve.sh

# View API documentation
# Open http://localhost:9000/docs
```

## Session Management

Sessions are automatically created and stored in `./data/mappings/`. Each session maintains:
- Entity mappings for reversible anonymization
- Custom name replacements
- Timestamp information

To clean up a session:
```bash
curl -X DELETE "http://localhost:9000/sessions/{session_id}"
```
