import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a sarcastic assistant."
}


def index(request):
    if "conversation_history" not in request.session:
        request.session["conversation_history"] = [SYSTEM_MESSAGE]
    return render(request, 'index.html')


@csrf_exempt
def chat_bot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message")
            if not message:
                return JsonResponse({"error": "Message is required"}, status=400)
            conversation_history = request.session.get("conversation_history", [SYSTEM_MESSAGE])
            conversation_history.append({"role": "user", "content": message})

            # Request gpt-4o for chat completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history
            )
            # Print the response and add it to the messages list
            chat_message = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": chat_message})
            request.session["conversation_history"] = conversation_history
            return JsonResponse({"reply": chat_message})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
