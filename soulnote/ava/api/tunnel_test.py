import requests

response = requests.get(
    f"{'https://flashback-playgroup-late.ngrok-free.dev'}/health",
    timeout=15
)

print("HTTP status:", response.status_code)
print("Response:", response.text)
