
import requests
import os
import json

PUBLIC_URL = "https://flashback-playgroup-late.ngrok-free.dev"
INFERENCE_URL = f"{PUBLIC_URL}/v1/chat/completions"

response = requests.post(
    INFERENCE_URL,
    headers={
        "Authorization": f"Bearer {os.environ['API_TOKEN']}",
        "Content-Type": "application/json"
    },
    
	json={
		"messages": [
			{
				"role": "system",
				"content": "You are Ava, the reflective AI companion in SoulNote. Respond naturally and directly. Do not show your internal reasoning."
			},
			{
				"role": "user",
				"content": "Hello Ava. In a very long paragraph of poems introduce yourself!"
			}
		],
		"temperature": 0.7,
		"max_tokens": 256,
		"reasoning_effort": "none",
		"stream": False
	},

    timeout=180
)

print("HTTP status:", response.status_code)
print("\n=== COMPLETE RESPONSE ===")

try:
    data = response.json()
    print(json.dumps(data, indent=4))

    if data.get("choices"):
        choice = data["choices"][0]
        message = choice.get("message", {})

        print("\n=== GENERATION DETAILS ===")
        print("Content:", repr(message.get("content")))
        print("Finish reason:", choice.get("finish_reason"))
        print("Other message fields:", {
            key: value
            for key, value in message.items()
            if key != "content"
        })

except ValueError:
    print(response.text)
