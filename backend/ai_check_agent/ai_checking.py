import requests
import json
from agents import function_tool


@function_tool()
def check_ai(text: str):
    """
    Detects whether a given text is human-written or AI-generated.

    Args:
        text (str): The text to be analyzed.

    Returns:
        dict: A dictionary containing the detection results with the following keys:
            - success (bool): Whether the API request was successful.
            - is_human (float): The percentage likelihood that the text is human-written (0-100).
            - fake_percentage (float): The percentage likelihood that the text is AI-generated (0-100).
            - feedback (str): Human-readable feedback about the detection result.
            - additional_feedback (str): Additional notes or suggestions (e.g., "Input more text for accuracy").
            - text_words (int): Total number of words in the input text.
            - ai_words (int): Number of words detected as AI-generated.
            - detected_language (str): The language detected in the input text.
            - error (str, optional): Error message if the request fails.
    """
    url = "https://api.zerogpt.com/api/detect/detectText"

    payload = json.dumps({
        "input_text": text
    })
    headers = {
        # Replace with your actual API key if needed
        'ApiKey': '1150188d-ee4e-4c7a-b831-e0f3c5d0c366',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        data = response.json()

        if not data.get("success", False):
            return {
                "success": False,
                "error": data.get("message", "Unknown error from ZeroGPT API.")
            }

        parsed = {
            "success": True,
            "is_human": data["data"].get("isHuman", 0),
            "fake_percentage": data["data"].get("fakePercentage", 0.0),
            "feedback": data["data"].get("feedback", ""),
            "additional_feedback": data["data"].get("additional_feedback", ""),
            "text_words": data["data"].get("textWords", 0),
            "ai_words": data["data"].get("aiWords", 0),
            "detected_language": data["data"].get("detected_language", ""),
        }
        return parsed

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Failed to decode JSON response from ZeroGPT API."
        }
