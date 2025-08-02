# AI Flow Architecture

This document explains the complete AI flow in the Puckr backend:

**API Router → Helper Service → LLM Service (Gemini)**

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Router    │───▶│  Helper Service  │───▶│  LLM Service    │
│   (ai_router)   │    │   (ai_helper)    │    │   (gemini)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Flow Breakdown

### 1. API Router (`ai_router.py`)
- **Location**: `backend/app/api/ai_router.py`
- **Purpose**: HTTP endpoints for AI operations
- **Authentication**: Uses JWT tokens via `get_current_user`
- **Endpoints**:
  - `POST /ai/process-content` - Process any content with LLM
  - `POST /ai/analyze-document` - Analyze documents (PDF, Word)
  - `POST /ai/analyze-video` - Analyze YouTube videos
  - `POST /ai/research-topic` - Research topics
  - `GET /ai/services` - Get available services
  - `GET /ai/health` - Health check

### 2. Helper Service (`ai_helper.py`)
- **Location**: `backend/app/helpers/ai_helper.py`
- **Purpose**: Intermediary between API and LLM services
- **Features**:
  - Validates service names
  - Handles different content types
  - Provides specialized analysis methods
  - Adds user context to results
  - Error handling and logging

### 3. LLM Service (`gemini_service.py`)
- **Location**: `backend/app/service/llm/gemini_service.py`
- **Purpose**: Direct interaction with Google Gemini API
- **Features**:
  - PDF document processing
  - YouTube video analysis
  - Text content processing
  - Base64 encoding for documents
  - URL content fetching

## API Endpoints

### Process Content
```http
POST /ai/process-content
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "content": "Your content here",
  "prompt": "Analyze this content",
  "service_name": "gemini"
}
```

### Analyze Document
```http
POST /ai/analyze-document
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "document_url": "https://example.com/document.pdf",
  "analysis_type": "summary",
  "service_name": "gemini"
}
```

### Analyze Video
```http
POST /ai/analyze-video
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "youtube_url": "https://youtube.com/watch?v=abc123",
  "analysis_type": "summary"
}
```

### Research Topic
```http
POST /ai/research-topic
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "topic": "machine learning trends 2024",
  "research_type": "comprehensive",
  "service_name": "perplexity"
}
```

## Response Format

All endpoints return the same response format:

```json
{
  "success": true,
  "processing_results": "AI generated content...",
  "error": null,
  "service": "gemini",
  "model": "gemini-2.5-flash",
  "user_id": "user-uuid",
  "user_email": "user@example.com"
}
```

## Supported Analysis Types

### Document Analysis
- `summary` - Comprehensive document summary
- `key_points` - Extract key points and main ideas
- `insights` - Provide valuable insights
- `questions` - Generate relevant questions
- `action_items` - Extract action items and next steps

### Video Analysis
- `summary` - Video summary
- `key_points` - Key points from video
- `insights` - Video insights
- `transcript` - Detailed transcript
- `highlights` - Important moments

### Research Types
- `comprehensive` - Comprehensive research report
- `quick` - Quick overview
- `detailed` - Detailed analysis
- `comparison` - Compare different aspects
- `trends` - Analyze current trends

## Available Services

- **gemini** - Google Gemini (supports PDF, video, text)
- **grok** - xAI Grok (supports text, URLs)
- **perplexity** - Perplexity AI (supports text, web search)

## Environment Variables

Make sure these are set in your `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
GROK_API_KEY=your_grok_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
```

## Testing

Run the test script to verify the complete flow:

```bash
cd backend
python test_ai_flow.py
```

## Usage Examples

### Python Client Example

```python
import requests

# Process content
response = requests.post(
    "http://localhost:8000/ai/process-content",
    json={
        "content": "AI is transforming industries",
        "prompt": "Analyze this statement",
        "service_name": "gemini"
    },
    headers={"Authorization": "Bearer your-jwt-token"}
)

result = response.json()
if result["success"]:
    print(result["processing_results"])
```

### JavaScript/TypeScript Example

```typescript
// Analyze a document
const response = await fetch('/ai/analyze-document', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    document_url: 'https://example.com/report.pdf',
    analysis_type: 'key_points',
    service_name: 'gemini'
  })
});

const result = await response.json();
if (result.success) {
  console.log(result.processing_results);
}
```

## Error Handling

The system includes comprehensive error handling:

1. **Service Validation**: Checks if requested service exists
2. **Content Validation**: Validates content types and formats
3. **API Error Handling**: Handles LLM API errors gracefully
4. **User Context**: Adds user information for auditing
5. **Fallback Responses**: Returns structured error responses

## Security Features

- **JWT Authentication**: All endpoints require valid JWT tokens
- **User Context**: All operations are tied to authenticated users
- **Input Validation**: Pydantic models validate all inputs
- **Error Sanitization**: Errors don't expose sensitive information

## Performance Considerations

- **Async Operations**: All operations are async for better performance
- **Connection Pooling**: HTTP clients are reused
- **Error Recovery**: Graceful handling of API failures
- **Rate Limiting**: Built-in rate limiting considerations

## Monitoring

- **Health Check**: `/ai/health` endpoint for monitoring
- **Service Status**: `/ai/services` shows available services
- **User Tracking**: All operations include user context
- **Error Logging**: Comprehensive error logging

## Future Enhancements

- **Caching**: Add response caching for repeated requests
- **Batch Processing**: Support for batch content processing
- **Streaming**: Real-time streaming responses
- **Custom Models**: Support for custom model configurations
- **Analytics**: Usage analytics and metrics 