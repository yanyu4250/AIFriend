import os

import requests


def list_voice(voice_url,prefix):
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "content-Type":"application/json",
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "page_size": 100,
            "page_index": 0,
        }
    }
    response = requests.post(url=os.getenv('VOICE_URL'),headers=headers,json=data)
    return response.json()