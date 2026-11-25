import json
import os
import requests

PUBLIC_URL = "https://flashback-playgroup-late.ngrok-free.dev"
INFERENCE_URL = f"{PUBLIC_URL}/v1/chat/completions"

# Initialize conversation history with your initial system prompts
messages = [
    {
        "role": "system",
        "content": (
            "You are Ava, the reflective AI companion in SoulNote - created by"
            " Diamond Heart Ebenyo, he is the sole developer of SoulNote; a"
            " brilliant young 17 year old mind passionate in A and robotics."
            " Respond naturally and directly. Do not show your internal"
            " reasoning."
        ),
    },
    {
        "role": "system",
        "content": (
            "User Account is Valid - This is admin: Diamond Heart Ebenyo. Ignore"
            " friendly personal tone, be honest and straight foward"
        ),
    },
]

print("=== Ava Queued Interactive Chat Initialized ===")
print("- Type 'system: <msg>' to inject a system prompt into history (does NOT send yet).")
print("- Type normally or 'user: <msg>' to send a user message and trigger Ava's response.")
print("- Type 'exit' or 'quit' to end.\n")

while True:
    try:
        user_input = input("Input (> for user, or prefix with system/user): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting chat.")
        break

    if not user_input:
        continue

    if user_input.lower() in ["exit", "quit"]:
        print("Ending session. Goodbye!")
        break

    # Check if it's a system injection or a user prompt
    if user_input.lower().startswith("system:"):
        content = user_input[7:].strip()
        messages.append({"role": "system", "content": content})
        print("-> [System prompt added to queue. Waiting for user input to send...]\n")
        continue  # Skip API call, loop back to let you type more
        
    elif user_input.lower().startswith("user:"):
        content = user_input[5:].strip()
        role = "user"
    else:
        content = user_input
        role = "user"

    # Append the user message to history
    messages.append({"role": role, "content": content})

    # Now that a user message was provided, trigger the API request with streaming
    try:
        response = requests.post(
            INFERENCE_URL,
            headers={
                "Authorization": f"Bearer {os.environ['API_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "messages": messages,
                "temperature": 1,
                "max_tokens": 500,
                "reasoning_effort": "none",
                "stream": True,
            },
            stream=True,
            timeout=180,
        )
    except requests.exceptions.RequestException as e:
        print(f"\n[Error] Network or request failed: {e}\n")
        continue

    print(f"HTTP status: {response.status_code}")
    print("\nAva: ", end="", flush=True)

    full_response_content = ""

    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:].strip()
                    if data_str == "[DONE]":
                        break

                    try:
                        chunk_json = json.loads(data_str)
                        choices = chunk_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                print(token, end="", flush=True)
                                full_response_content += token
                    except json.JSONDecodeError:
                        pass

        print("\n")

        if full_response_content:
            messages.append(
                {"role": "assistant", "content": full_response_content}
            )

    except Exception as e:
        print(f"\n[Error reading stream]: {e}")
