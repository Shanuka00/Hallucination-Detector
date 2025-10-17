import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f'Testing Anthropic API key (shanukaAPI)...')
print(f'Key starts with: {api_key[:15]}...')

try:
    client = anthropic.Anthropic(api_key=api_key)
    print('✅ Client created successfully')
    
    # Try with Claude Haiku (cheaper model)
    print('Testing with claude-3-haiku-20240307...')
    message = client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'Say hello in one word'}]
    )
    print('✅ SUCCESS: Anthropic API key is valid and working!')
    print(f'Response: {message.content[0].text}')
    
except anthropic.AuthenticationError as e:
    print(f'❌ AUTHENTICATION ERROR: Invalid API key')
    print(f'Details: {e}')
except anthropic.NotFoundError as e:
    print(f'❌ MODEL NOT FOUND: The model is not available with this API key')
    print(f'Details: {e}')
    print('\nThis could mean:')
    print('1. Your API key does not have access to Claude models')
    print('2. You need to check your Anthropic account tier/permissions')
except Exception as e:
    print(f'❌ ERROR: {type(e).__name__}')
    print(f'Details: {e}')
