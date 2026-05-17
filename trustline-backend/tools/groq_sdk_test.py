import os
import sys
import json

try:
    from groq import Groq
except Exception as e:
    print('ERROR: groq package not installed:', e)
    print('Install with: pip install groq')
    sys.exit(2)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-13b-instant')

if not GROQ_API_KEY:
    print('ERROR: GROQ_API_KEY not set in environment')
    sys.exit(2)

client = Groq(api_key=GROQ_API_KEY)

try:
    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": "Health-check: reply OK"}],
        model=GROQ_MODEL,
    )
    try:
        print('\nRESPONSE:\n')
        print(resp.choices[0].message.content)
    except Exception:
        print(json.dumps(resp, indent=2))
except Exception as e:
    print('ERROR during request:', type(e).__name__, str(e))
    sys.exit(3)
