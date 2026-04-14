from django.core.cache import cache
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from json import loads
import google.generativeai as genai
# import vertexai
# from vertexai.generative_models import GenerativeModel
from .config import *

# Create your views here.
# vertexai.init(api)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def chat(request, s=None):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return redirect('authentication:verify')
    else:
        return redirect('authentication:signin')
    context = {
        'location': 'chat',
        'abbreviatedname': (request.user.first_name if len(request.user.first_name)<18 else request.user.first_name[:15]+'...') if request.user.is_authenticated and request.user.email_verified else "",
    }
    return render(request, "ai/chat.html", context)


def conversation(request):
    if request.user.is_authenticated:
        if not request.user.email_verified:
            return HttpResponse('verify your account', status=400)
    else:
        return HttpResponse('login to your account or create a new account', status=400)
    if not request.user.is_authenticated:
        return JsonResponse({
            '_action': '_ask',
            'success': False,
            "error": f"User not authenticated"
        }, status=401)
    
    if not request.user.email_verified:
        return JsonResponse({
            '_action': '_ask',
            'success': False,
            "error": f"User not verified"
        }, status=401)
    # try:
    json_data = loads(request.body)
    _conversation = json_data['meta']['content']['conversation']
    conversation_history = []
    for c in _conversation:
        chi = {
            'role': c['role'] if c['role']=='user' else 'model',
            'parts': {str(c['content'])}
        }
        conversation_history.append(chi)
    prompt = json_data['meta']['content']['parts'][0]
    try:
    # if True:
        # model = genai.GenerativeModel('gemini-pro')
        model = genai.GenerativeModel("gemini-2.5-flash")
        instruction = "Start your response by a asking the user about there name before extending a warm greeting and addressing their inquiries. When discussing mathematical topics, ensure that you not only provide explanations but also include numerical calculations and worked-out examples to enhance clarity and understanding."
        chat = model.start_chat(history=[{'role': 'user', 'parts': {instruction}}, {'role': 'model', 'parts': {"Okay I will do that"}}]+conversation_history)
        gpt_resp = chat.send_message(prompt.get("content"), stream=True)
    except:
    # else:
        gpt_resp=None
    def stream():
        if not gpt_resp:
            yield "error connecting to the server, check your network connection, reload and try again"
            return
        for chunk in gpt_resp:
            try:
                token = chunk.text
                if token is not None:
                    yield token

            except GeneratorExit:
                break
            except Exception as e:
                print(e)
                continue

    return StreamingHttpResponse(stream(), content_type='text/event-stream')

    

# pre written suggestions
# [
#     ["Create a workout plan", "for resistance training", "I need to start resistance training. Can you create a 7-day workout plan for me to ease into it?"],
#     ["Give me ideas", "about how to plan New Years resolution", "Give me 3 ideas about how to plan good New Years resolutions. Give me some that are personal, family, and professionally-oriented."],
#     ["Write a thank-you note", "to my interviewer", "Write 2-3 sentences to thank my interviewer, reiterating my excitement for the job opportunity while keeping it cool. Don't make it too formal."],
#     ["Create a content calendar", "for a TikTok account", "Create a content calendar for a TikTok account on reviewing real estate listings."],
#     ["Help me pick", "an outfit that will look good on camera", "I have a photoshoot tomorrow. Can you recommend me some colors and outfit options that will look good on camera?"]
#     ["Design a database schema", "for an online merch store", "Design a database schema for an online merch store."]
#     ["Tell me a fun fact", "about the Roman Empire", "Tell me a random fun fact about the Roman Empire"],
#     ["Write a Python script" ,"to automate sending daily email reports", "Write a script to automate sending daily email reports in Python, and walk me through how I would set it up."],
#     ["Plan a trip" ,"to see the northern lights in Norway", "Plan a 3-day trip to see the northern lights in Norway. Also recommend any ideal dates."],
# ]

