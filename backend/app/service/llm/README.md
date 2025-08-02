# LLM Services

This directory contains services for interacting with various Large Language Model (LLM) APIs to perform research, summarization, and content analysis.

## Enhanced Prompt System

The AI helper service now automatically enhances user prompts with content-type-specific context to improve LLM understanding and response quality. Each content type gets specialized context:

### Content Type Contexts

- **PDF Documents**: "You are analyzing a PDF document. Focus on extracting key information, main points, and insights from the document structure and content."
- **YouTube Videos**: "You are analyzing a YouTube video. Focus on the video content, key topics discussed, and main insights from the visual and audio content."
- **Twitter/X Content**: "You are analyzing Twitter/X content. Focus on the key messages, trends, and insights from the social media content."
- **Reddit Content**: "You are analyzing Reddit content. Focus on the discussion, key points, and community insights from the forum content."
- **Blog Posts**: "You are analyzing a blog post or article. Focus on the main arguments, key insights, and important information from the written content."

### How It Works

1. User provides a simple prompt (e.g., "Summarize the key points")
2. AI helper detects content type from database
3. Enhances prompt with content-specific context
4. LLM service receives enhanced prompt with clear understanding of content type
5. Response includes both original and enhanced prompts for reference

## Available Services

### 1. Gemini Service (`gemini_service.py`)
- **Provider**: Google Gemini
- **API**: Google Generative AI API
- **Model**: gemini-2.5-flash
- **Features**: 
  - PDF document processing with native vision
  - YouTube video analysis
  - Text content processing
  - Research, summarization, content analysis

### 2. Grok Service (`grok_service.py`)
- **Provider**: xAI (Elon Musk's company)
- **API**: xAI Grok API
- **Model**: grok-beta
- **Features**: Research, summarization, content analysis

### 3. Perplexity Service (`perplexity_service.py`)
- **Provider**: Perplexity AI
- **API**: Perplexity API
- **Model**: llama-3.1-sonar-small-128k-online
- **Features**: Research with web search, summarization, content analysis

## Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# xAI Grok API
GROK_API_KEY=your_grok_api_key_here

# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

## Usage

### Basic Usage

```python
from app.service import LLMServiceFactory

# Create a service instance
gemini_service = LLMServiceFactory.create_service("gemini")
grok_service = LLMServiceFactory.create_service("grok")
perplexity_service = LLMServiceFactory.create_service("perplexity")

# Process content with unified interface
result = await gemini_service.process_content(
    content="https://youtube.com/watch?v=abc123",  # YouTube video
    prompt="Summarize this video"
)

# Process multiple content items
result = await gemini_service.process_content(
    content=[
        "https://youtube.com/watch?v=abc123",  # YouTube video
        "https://example.com/document.pdf",    # PDF document
        "This is some text content"            # Text content
    ],
    prompt="Analyze all this content and provide key insights"
)
```

### Service Methods

All services implement the unified `process_content` method:

#### `process_content(content: Union[str, bytes, List[Union[str, bytes]]], prompt: str)`
- Processes any type of content with a specific prompt
- Supports strings, bytes, or lists of content
- Automatically handles different content types (YouTube, PDFs, text)
- Returns processing results

### Response Format

All methods return a dictionary with the following structure:

```python
{
    "success": bool,
    "prompt": str,
    "processing_results": str,
    "youtube_url": str,  # Only for YouTube processing
    "video_id": str,  # Only for YouTube processing
    "content_type": str,  # Type of content processed
    "model": str,
    "service": str,
    "error": str  # Only when success is False
}
```

## Features by Service

### Gemini Service
- ✅ PDF document processing with native vision (up to 1000 pages)
- ✅ YouTube video analysis and understanding
- ✅ Text content processing
- ✅ Research with comprehensive analysis
- ✅ Content summarization
- ✅ Multiple analysis types
- ✅ High-quality text generation

### Grok Service
- ✅ Research with detailed insights
- ✅ Content summarization
- ✅ Multiple analysis types
- ✅ Business-focused analysis

### Perplexity Service
- ✅ Research with web search capabilities
- ✅ Content summarization
- ✅ Multiple analysis types
- ✅ Real-time information access
- ✅ Source citations

## Content Type Support

### Gemini Service Content Types:
1. **PDF Documents**: Native vision understanding, supports up to 1000 pages
2. **YouTube Videos**: Video analysis and content understanding
3. **Text Content**: Standard text processing and generation
4. **URLs**: Automatic content fetching and processing

### Grok & Perplexity Services:
1. **Text Content**: Standard text processing
2. **URLs**: Content fetching and text extraction
3. **Document Bytes**: Basic text extraction from documents

## Error Handling

All services include comprehensive error handling:

```python
try:
    result = await service.research_content("your query")
    if result["success"]:
        print("Success:", result["research_results"])
    else:
        print("Error:", result["error"])
except Exception as e:
    print(f"Service error: {str(e)}")
```

## Example Usage

See `example_usage.py` for complete examples of how to use all services, including the new specialized Gemini functions.

To run the examples:

```bash
cd backend
python -m app.service.example_usage
```

## API Rate Limits

Be aware of the following rate limits:
- **Gemini**: 15 requests per minute
- **Grok**: Varies by plan
- **Perplexity**: 5 requests per minute (free tier)

## Best Practices

1. **Error Handling**: Always check the `success` field in responses
2. **Rate Limiting**: Implement appropriate delays between requests
3. **Content Length**: Be mindful of token limits for each service
4. **API Keys**: Store API keys securely in environment variables
5. **Async Usage**: All methods are async, use `await` when calling them
6. **Content Types**: Use appropriate specialized functions for different content types
7. **PDF Processing**: Ensure PDFs are properly oriented and clear for best results
8. **YouTube URLs**: Use standard YouTube URLs (youtube.com/watch?v=...)

## Dependencies

The services require the following packages (already in requirements.txt):
- `httpx`: For async HTTP requests
- `python-dotenv`: For environment variable management
- `aiohttp`: For additional async HTTP capabilities 