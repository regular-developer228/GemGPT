import os
from django.shortcuts import render
from django.views.decorators.http import require_POST
from openai import OpenAI
from django.http import JsonResponse

from .models import Conversation, Message

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = 'Ты персональный ассистент, дружелюбный'

def get_conversation(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    conversation, _ = Conversation.objects.get_or_create(session_key=session_key)
    return conversation


# Create your views here.
def index(request):
    conversation = get_conversation(request)
    messages = conversation.messages.all()
    return render(request, 'chat_app/index.html', {'messages': messages})

@require_POST
def send(request):
    """Приймає нове повідомлення, кличе OpenAI, повертає відповідь у JSON."""
    user_text = request.POST.get("message", "").strip()
    if not user_text:
        return JsonResponse({"error": "Порожнє повідомлення"}, status=400)

    conversation = get_conversation(request)

    # 1. Зберігаємо повідомлення користувача в базу.
    Message.objects.create(conversation=conversation, role="user", content=user_text)

    # 2. Збираємо ВСЮ історію діалогу — це і є «пам'ять».
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation.messages.all():
        history.append({"role": msg.role, "content": msg.content})
    # 3. Відправляємо історію в OpenAI.
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # дешева і швидка модель, гарна для старту
            messages=history,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        # Якщо щось пішло не так (немає коштів, неправильний ключ тощо)
        return JsonResponse({"error": f"Помилка OpenAI: {e}"}, status=500)

    # 4. Зберігаємо відповідь асистента в базу.
    Message.objects.create(conversation=conversation, role="assistant", content=answer)

    # 5. Повертаємо відповідь браузеру.
    return JsonResponse({"reply": answer})

@require_POST
def clear(request):
    """Очищає історію поточного діалогу."""
    conversation = get_conversation(request)
    conversation.messages.all().delete()
    return JsonResponse({"status": "ok"})