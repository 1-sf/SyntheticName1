from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

API_KEY = "TWfVrlX659GSTS9hcsgUcPZ8uNzfoQsg"

def run_mistral(user_message, model="mistral-large"):
    client = MistralClient(api_key=API_KEY)
    messages = [
        ChatMessage(role="user", content=user_message)
    ]
    chat_response = client.chat(
        model=model,
        messages=messages
    )
    return (chat_response.choices[0].message.content)