"""
Example usage of LLM services for research and content analysis
"""

import asyncio
from typing import Dict, Any
from . import LLMServiceFactory

async def example_unified_interface():
    """Example of using the unified process_content interface"""
    
    try:
        print("\n=== Testing Unified Interface ===")
        
        # Test content
        content = [
            "https://youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube video
            "https://example.com/document.pdf",  # PDF document
            "This is some text content to process"  # Text content
        ]
        
        prompt = "Analyze this content and provide key insights"
        
        # Test all available services
        services = LLMServiceFactory.get_available_services()
        
        for service_name in services:
            try:
                print(f"\n--- Testing {service_name.upper()} Service ---")
                
                # Create service instance
                service = LLMServiceFactory.create_service(service_name)
                
                # Process content with unified interface
                result = await service.process_content(content, prompt)
                
                if result["success"]:
                    print(f"✅ {service_name} processing successful")
                    print(f"Results: {result['processing_results'][:200]}...")
                else:
                    print(f"❌ {service_name} processing failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Error with {service_name}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error with unified interface: {str(e)}")

async def example_single_content():
    """Example of processing single content items"""
    
    try:
        print("\n=== Testing Single Content Processing ===")
        
        # Create Gemini service for specialized content
        gemini_service = LLMServiceFactory.create_service("gemini")
        
        # 1. YouTube video
        youtube_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        result = await gemini_service.process_content(youtube_url, "Summarize this video")
        
        if result["success"]:
            print(f"✅ YouTube processing successful")
            print(f"Results: {result['processing_results'][:200]}...")
        else:
            print(f"❌ YouTube processing failed: {result['error']}")
        
        # 2. PDF document
        pdf_url = "https://example.com/document.pdf"
        result = await gemini_service.process_content(pdf_url, "Extract key points from this document")
        
        if result["success"]:
            print(f"✅ PDF processing successful")
            print(f"Results: {result['processing_results'][:200]}...")
        else:
            print(f"❌ PDF processing failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error with single content processing: {str(e)}")

async def main():
    """Main function to run all examples"""
    print("🚀 Starting LLM Service Examples")
    
    print("\n" + "="*50)
    print("UNIFIED INTERFACE EXAMPLE")
    print("="*50)
    await example_unified_interface()
    
    print("\n" + "="*50)
    print("SINGLE CONTENT EXAMPLE")
    print("="*50)
    await example_single_content()
    
    print("\n✅ All examples completed!")

if __name__ == "__main__":
    asyncio.run(main()) 