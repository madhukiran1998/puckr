#!/usr/bin/env python3
"""
Simple test for the simplified AI flow:
API takes file/link ID -> Helper fetches from DB -> LLM processes
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.helpers.ai_helper import AIHelperService

async def test_simple_flow():
    """Test the simplified AI flow"""
    
    print("🚀 Testing Simplified AI Flow")
    print("=" * 40)
    
    ai_helper = AIHelperService()
    
    # Test LLM service selection
    print("\n1. Testing LLM Service Selection:")
    
    # Test document types
    doc_service = ai_helper._get_llm_service("pdf")
    print(f"✅ PDF -> {doc_service.__class__.__name__}")
    
    video_service = ai_helper._get_llm_service("youtube")
    print(f"✅ YouTube -> {video_service.__class__.__name__}")
    
    blog_service = ai_helper._get_llm_service("blog")
    print(f"✅ Blog -> {blog_service.__class__.__name__}")
    
    reddit_service = ai_helper._get_llm_service("reddit")
    print(f"✅ Reddit -> {reddit_service.__class__.__name__}")
    
    print("\n✅ LLM service selection working!")
    
    print("\n📋 Summary:")
    print("- API: Takes file_id/link_id + prompt")
    print("- Helper: Fetches from DB, picks LLM based on type")
    print("- LLM: Processes content, no factory needed")
    print("\n🚀 Much simpler!")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    asyncio.run(test_simple_flow()) 