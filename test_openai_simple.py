#!/usr/bin/env python3
"""
Simple test to isolate OpenAI client initialization issue
"""

from openai import OpenAI
from config import get_openai_api_key

def test_openai_client():
    """Test OpenAI client initialization."""
    print("Testing OpenAI client initialization...")
    
    # Get API key
    api_key = get_openai_api_key()
    print(f"API key length: {len(api_key) if api_key else 0}")
    
    if not api_key:
        print("No API key found!")
        return False
    
    try:
        # Try to initialize the client
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized successfully!")
        
        # Try a simple API call
        print("Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello!"}],
            max_tokens=10
        )
        print(f"✓ API call successful: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_openai_client() 