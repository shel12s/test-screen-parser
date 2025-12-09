import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def transcribe_screenshot(image_path):
    """
    Sends screenshot to mistralai/ministral-14b-2512 for transcription.
    """
    if not API_KEY:
        return "Error: OPENROUTER_API_KEY not found in .env"

    base64_image = encode_image(image_path)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/screen-helper", # Required by OpenRouter
        "X-Title": "Screen Helper"
    }

    # Note: Assuming the model supports vision/image input in standard OpenAI format
    payload = {
        "model": "mistralai/mistral-large-2512",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe the text from this image. Extract the test question and options exactly as they appear. YOU MUST RETURN ONLY THE TEXT WITHOUT ANY ADDITIONAL COMMENTS OR FORMATTING."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return f"Error: Unexpected response format: {result}"
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def get_answer(question_text):
    """
    Sends text to google/gemini-2.0-flash-exp:free for the answer.
    """
    if not API_KEY:
        return "Error: OPENROUTER_API_KEY not found in .env"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/screen-helper",
        "X-Title": "Screen Helper"
    }

    payload = {
        "model": "mistralai/mistral-large-2512",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Provide the SHORTEST possible answer to the test question in as few words as possible, you can just give the correct answer in one letter or text. If it's multiple choice, just give the correct option letter or text."
            },
            {
                "role": "user",
                "content": question_text
            }
        ]
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return f"Error: Unexpected response format: {result}"
    except Exception as e:
        return f"Error getting answer: {str(e)}"
