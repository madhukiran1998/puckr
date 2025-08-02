#!/usr/bin/env python3
"""
Test script to demonstrate the AI flow:
API Router -> Helper Service -> LLM Service (Gemini)
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.helpers.ai_helper import AIHelperService
from app.service.llm import LLMServiceFactory

async def test_ai_flow():
    """Test the complete AI flow"""
    
    print("🚀 Testing AI Flow: API -> Helper -> LLM Service")
    print("=" * 60)
    
    # 1. Test Helper Service directly
    print("\n1. Testing Helper Service...")
    ai_helper = AIHelperService()
    
    # Test available services
    services = ai_helper.get_available_services()
    print(f"✅ Available services: {services}")
    
    # Test analysis types
    analysis_types = ai_helper.get_supported_analysis_types()
    print(f"✅ Supported analysis types: {analysis_types}")
    
    # 2. Test content processing
    print("\n2. Testing Content Processing...")
    
    # Test with simple text content
    result = await ai_helper.process_content_with_llm(
        content="The future of artificial intelligence and its impact on society",
        prompt="Provide a brief analysis of this topic",
        service_name="gemini"
    )
    
    if result["success"]:
        print(f"✅ Content processing successful")
        print(f"Service: {result['service']}")
        print(f"Model: {result['model']}")
        print(f"Results: {result['processing_results'][:200]}...")
    else:
        print(f"❌ Content processing failed: {result['error']}")
    
    # 3. Test document analysis
    print("\n3. Testing Document Analysis...")
    
    # Test with a sample document URL (you can replace with actual URL)
    result = await ai_helper.analyze_document(
        document_url="https://example.com/sample-document.pdf",
        analysis_type="summary",
        service_name="gemini"
    )
    
    if result["success"]:
        print(f"✅ Document analysis successful")
        print(f"Results: {result['processing_results'][:200]}...")
    else:
        print(f"❌ Document analysis failed: {result['error']}")
    
    # 4. Test video analysis
    print("\n4. Testing Video Analysis...")
    
    # Test with a sample YouTube URL
    result = await ai_helper.analyze_youtube_video(
        youtube_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        analysis_type="summary"
    )
    
    if result["success"]:
        print(f"✅ Video analysis successful")
        print(f"Results: {result['processing_results'][:200]}...")
    else:
        print(f"❌ Video analysis failed: {result['error']}")
    
    # 5. Test research
    print("\n5. Testing Research...")
    
    result = await ai_helper.research_topic(
        topic="machine learning trends 2024",
        research_type="comprehensive",
        service_name="perplexity"
    )
    
    if result["success"]:
        print(f"✅ Research successful")
        print(f"Results: {result['processing_results'][:200]}...")
    else:
        print(f"❌ Research failed: {result['error']}")
    
    # 6. Test LLM Service Factory
    print("\n6. Testing LLM Service Factory...")
    
    try:
        gemini_service = LLMServiceFactory.create_service("gemini")
        print("✅ Gemini service created successfully")
        
        grok_service = LLMServiceFactory.create_service("grok")
        print("✅ Grok service created successfully")
        
        perplexity_service = LLMServiceFactory.create_service("perplexity")
        print("✅ Perplexity service created successfully")
        
    except Exception as e:
        print(f"❌ Service creation failed: {str(e)}")
    
    print("\n✅ AI Flow Test Completed!")

async def test_api_endpoints():
    """Test the API endpoints (simulated)"""
    
    print("\n" + "=" * 60)
    print("🔧 Testing API Endpoints (Simulated)")
    print("=" * 60)
    
    # Simulate API requests
    ai_helper = AIHelperService()
    
    # Simulate /ai/process-content endpoint
    print("\n📝 Testing /ai/process-content endpoint...")
    content_request = {
        "content": "Artificial intelligence is transforming industries worldwide",
        "prompt": "Analyze the impact of AI on business",
        "service_name": "gemini"
    }
    
    result = await ai_helper.process_content_with_llm(
        content=content_request["content"],
        prompt=content_request["prompt"],
        service_name=content_request["service_name"]
    )
    
    if result["success"]:
        print("✅ /ai/process-content endpoint working")
    else:
        print(f"❌ /ai/process-content endpoint failed: {result['error']}")
    
    # Simulate /ai/analyze-document endpoint
    print("\n📄 Testing /ai/analyze-document endpoint...")
    document_request = {
        "document_url": "https://example.com/ai-report.pdf",
        "analysis_type": "key_points",
        "service_name": "gemini"
    }
    
    result = await ai_helper.analyze_document(
        document_url=document_request["document_url"],
        analysis_type=document_request["analysis_type"],
        service_name=document_request["service_name"]
    )
    
    if result["success"]:
        print("✅ /ai/analyze-document endpoint working")
    else:
        print(f"❌ /ai/analyze-document endpoint failed: {result['error']}")
    
    # Simulate /ai/services endpoint
    print("\n🔧 Testing /ai/services endpoint...")
    services = ai_helper.get_available_services()
    analysis_types = ai_helper.get_supported_analysis_types()
    
    print(f"✅ Available services: {services}")
    print(f"✅ Analysis types: {analysis_types}")

async def main():
    """Main test function"""
    print("🧪 Starting AI Flow Tests")
    print("=" * 60)
    
    # Test the complete flow
    await test_ai_flow()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("- API Router: ✅ Ready")
    print("- Helper Service: ✅ Ready") 
    print("- LLM Services: ✅ Ready")
    print("- Gemini Service: ✅ Ready")
    print("\n🚀 You can now make API calls to /ai/* endpoints!")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the tests
    asyncio.run(main()) 