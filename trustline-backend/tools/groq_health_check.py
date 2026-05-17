import os
import sys
import json
import requests

# Load simple .env in project root
env = {}
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
except FileNotFoundError:
    print('ERROR: .env file not found')
    sys.exit(2)

model = env.get('GROQ_MODEL', '')
key = env.get('GROQ_API_KEY', '')
if not model or not key:
    print('ERROR: GROQ_MODEL or GROQ_API_KEY not set in .env')
    sys.exit(2)

api_url = env.get('GROQ_API_URL')
if not api_url:
    # Use Groq OpenAI-compatible base and test chat/completions
    api_url = 'https://api.groq.com/openai/v1'

endpoint = api_url.rstrip('/') + '/chat/completions'

print('POST', endpoint)
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
payload = {
    'model': model,
    'messages': [{'role': 'user', 'content': 'Health-check: reply OK'}],
    'max_tokens': 16,
}

try:
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=8)
    print('HTTP', resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
except Exception as e:
    print('ERROR', type(e).__name__, str(e))
    sys.exit(3)
