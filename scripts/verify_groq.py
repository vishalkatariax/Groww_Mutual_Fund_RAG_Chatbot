#!/usr/bin/env python3
"""
Verify Groq LLM Integration

This script checks:
1. Groq API key is configured
2. OpenAI API key is configured (for embeddings)
3. Groq client can connect and generate responses
4. RAG pipeline is properly initialized
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def check_config():
    """Check configuration"""
    print("\n" + "=" * 80)
    print("CHECK 1: Configuration")
    print("=" * 80)
    
    try:
        from config import settings
        
        print(f"✅ LLM Provider: {settings.llm_provider}")
        print(f"✅ LLM Model: {settings.llm_model}")
        print(f"✅ Temperature: {settings.llm_temperature}")
        print(f"✅ Max Tokens: {settings.llm_max_tokens}")
        
        # Check Groq API key
        if settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here":
            print(f"✅ Groq API Key: {settings.groq_api_key[:10]}...{settings.groq_api_key[-4:]}")
        else:
            print("❌ Groq API Key: NOT SET or using placeholder")
            print("   Action: Add your Groq API key to .env file")
            print("   Get one at: https://console.groq.com/keys")
            return False
        
        # Check OpenAI API key
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print(f"✅ OpenAI API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
        else:
            print("❌ OpenAI API Key: NOT SET or using placeholder")
            print("   Action: Add your OpenAI API key to .env (required for embeddings)")
            print("   Get one at: https://platform.openai.com/api-keys")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def test_groq_connection():
    """Test Groq API connection"""
    print("\n" + "=" * 80)
    print("CHECK 2: Groq API Connection")
    print("=" * 80)
    
    try:
        from groq import Groq
        from config import settings
        
        print("Connecting to Groq API...")
        client = Groq(api_key=settings.groq_api_key)
        
        # Test with simple message
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": "Say 'Groq is working!' in exactly 3 words."}
            ],
            temperature=0.0,
            max_tokens=20,
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"✅ Groq API: Connected successfully")
        print(f"✅ Model: {settings.llm_model}")
        print(f"✅ Response: {answer}")
        
        # Safely retrieve response time if available
        resp_time = getattr(response.usage, 'total_time', None) or getattr(response.usage, 'total_time_ms', 'unknown')
        print(f"✅ Response time: {resp_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_rag_pipeline():
    """Test RAG pipeline initialization"""
    print("\n" + "=" * 80)
    print("CHECK 3: RAG Pipeline Initialization")
    print("=" * 80)
    
    try:
        from app.phase1.subphase_1_3_rag_setup.rag_pipeline import RAGPipeline
        from config import settings
        
        print("Initializing RAG pipeline...")
        pipeline = RAGPipeline()
        
        print(f"✅ Vector Store: Connected")
        print(f"✅ LLM Client: {settings.llm_provider} ({pipeline.llm_model})")
        print(f"✅ Embedding Client: OpenAI ({settings.embedding_model})")
        print(f"✅ System Prompt: Loaded")
        
        # Check if collection has data
        stats = pipeline.vector_store.get_stats()
        print(f"✅ Chunks in database: {stats['total_chunks']}")
        
        if stats['total_chunks'] == 0:
            print("⚠️  Warning: No chunks in database")
            print("   Action: Run data ingestion first:")
            print("   python3 scripts/run_phase_1_complete.py")
            return False
        
        return True
        
    except FileNotFoundError:
        print("⚠️  ChromaDB collection not found")
        print("   Action: Run data ingestion first:")
        print("   python3 scripts/run_phase_1_complete.py")
        return False
        
    except Exception as e:
        print(f"❌ RAG pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all checks"""
    print("\n" + "=" * 80)
    print("GROQ LLM INTEGRATION VERIFICATION")
    print("=" * 80)
    
    results = {
        "Configuration": check_config(),
        "Groq API Connection": test_groq_connection(),
        "RAG Pipeline": test_rag_pipeline(),
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Groq integration is working!")
        print("\nNext steps:")
        print("1. Start backend: python3 -m uvicorn app.main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test chat endpoint")
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        print("\nNeed help? See GROQ_INTEGRATION.md for detailed setup instructions")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
