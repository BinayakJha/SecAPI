# secapi/gemini.py (Zero-dependency Google Gemini API Client)

import json
import os
import urllib.request
import urllib.error

def call_gemini(system_instruction, messages, model="gemini-2.5-flash", api_key=None):
    """
    Calls the Google Gemini API using urllib.request.
    
    system_instruction: str (or None)
    messages: list of dict, e.g. [{"role": "user", "content": "..."}]
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            try:
                from secapi.secure import load_key
                api_key = load_key("gemini_api_key")
            except Exception:
                pass

    if not api_key:
        raise ValueError(
            "❌ GEMINI_API_KEY is not set.\n"
            "Please set it in your environment variables: export GEMINI_API_KEY='your_key'\n"
            "Or save it securely in the vault: secapi add (with key name 'gemini_api_key')"
        )

    # Convert OpenAI message roles to Gemini content structure
    # OpenAI: user, assistant, system
    # Gemini: user, model
    contents = []
    for msg in messages:
        role = msg["role"]
        if role == "assistant":
            role = "model"
        elif role == "system":
            # System instruction is handled separately
            continue
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    req_data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            
            # Extract generated text
            text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_content)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = error_content or str(e)
        raise RuntimeError(f"Gemini API Error: {msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with Gemini API: {e}")
