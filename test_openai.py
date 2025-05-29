import os
from openai import OpenAI

# Test script to check OpenAI API access
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY:
    print(f"API Key found: {OPENAI_API_KEY[:10]}...")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        # Try to list available models
        print("Checking available models...")
        models = client.models.list()
        available_models = [model.id for model in models.data]
        print(f"Available models: {available_models[:10]}")  # Show first 10
        
        # Try a simple completion with the most basic model
        if available_models:
            test_model = available_models[0]
            print(f"Testing with model: {test_model}")
            
            response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=50
            )
            print(f"Test response: {response.choices[0].message.content}")
        else:
            print("No models available")
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API key found")