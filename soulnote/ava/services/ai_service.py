# ava/services/ai_service.py

import requests

from django.conf import settings

class AvaAIServiceError(Exception):
	"""Raised when Ava's inference service fails."""
	pass


class AvaAIService:

	def __init__(self):
		self.api_url = getattr(settings, "AVA_API_URL", None)
		self.api_token = getattr(settings, "AVA_API_TOKEN", None)

		if not self.api_url or not self.api_token:
			raise AvaAIServiceError(
				"Ava API configuration is incomplete."
			)

		self.api_url = self.api_url.rstrip("/")
		self.endpoint = f"{self.api_url}/v1/chat/completions"

	def generate_response(self, messages):

		headers = {
			"Authorization": f"Bearer {self.api_token}",
			"Content-Type": "application/json"
		}

		payload = {
			"messages": messages,
			"temperature": 0.7,
			"max_tokens": 512,
			"reasoning_effort": "none",
			"stream": False
		}

		try:
			response = requests.post(
				self.endpoint,
				headers=headers,
				json=payload,
				timeout=(10, 180)
			)

			response.raise_for_status()

			data = response.json()

			content = (
				data.get("choices", [{}])[0]
				.get("message", {})
				.get("content", "")
			)

			if not content.strip():
				raise AvaAIServiceError(
					"Ava returned an empty response."
				)

			return content.strip()

		except requests.RequestException as error:
			raise AvaAIServiceError(
				f"Could not communicate with Ava's AI server: {error}"
			) from error

		except (ValueError, KeyError, IndexError, TypeError) as error:
			raise AvaAIServiceError(
				"Ava's AI server returned an invalid response."
			) from error

