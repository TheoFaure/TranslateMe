import sys
from django.shortcuts import render
from proto1.api_calls_methods import *
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import pdb
import json
import urllib.parse
from os import listdir
from os.path import isfile, join


@csrf_exempt
def run_emotion_recog(request):
    message = request.read()
    video_path = "/home/theo/SentimentalTranslator_Proto1/proto1/static/proto1/video/" + message.decode('UTF-8').split("=")[1] #str(message.decode('UTF-8').split("%5C",2)[2])

    api_response = send_video_emo_api(video_path)

    audio_path = create_audio_file(video_path)
    print("1")
    original_text = speech2text_ibm(audio_path)
    print("2")
    emo_original_text = get_sentiment_text(original_text, "en")
    print("3")
    microsoft_text = translate_microsoft(original_text, "fr")
    print("4")
    emo_microsoft_text = get_sentiment_text("".join(
        (c for c in unicodedata.normalize('NFD', microsoft_text.replace("’", " ")) if
         unicodedata.category(c) != 'Mn')), "fr")
    print("5")
    yandex_text = translate_yandex(original_text, "fr")
    print("6")
    emo_yandex_text = get_sentiment_text(
        "".join((c for c in unicodedata.normalize('NFD', yandex_text) if unicodedata.category(c) != 'Mn')), "fr")
    print("7")
    # delete the audio file
    command = "rm {video_path}.wav".format(video_path=video_path)
    subprocess.call(command, shell=True)
    print("8")
    # emo_video = "Emo_video processing..."#get_video_emo_response(api_response)

    context = {
        'original-text': original_text,
        'emo-original-text': emo_original_text,
        # 'emo-video': emo_video,
        'microsoft-text': microsoft_text,
        'emo-microsoft-text': emo_microsoft_text,
        'yandex-text': yandex_text,
        'emo-yandex-text': emo_yandex_text,
        # 'api-response': "Url to get the results : curl \"{results_url}\" -H \"Ocp-Apim-Subscription-Key:{emo_api_key}\"".format(results_url=api_response, emo_api_key=emo_api_key),
        'url-results': api_response,
    }

    j = json.dumps(context)
    return HttpResponse(j)


@csrf_exempt
def get_video_results(request):
    message = request.read().decode('UTF-8').split("url-results=",1)[1]
    message = urllib.parse.unquote(message)
    emo_video = get_video_emo(message).decode('UTF-8')
    emo_video = emo_video.replace("\\r\\n\"", "").replace("\"{", "{").replace("\\", "")
    return HttpResponse(emo_video)


@csrf_exempt
def get_video(request):
    video_name = request.read().decode('UTF-8').split("=")[1]
    video_path = "/home/theo/SentimentalTranslator_Proto1/proto1/static/proto1/video/%s" % video_name

    with open(video_path, mode='rb') as file:
        file_content = file.read()
        return HttpResponse(file_content)


@csrf_exempt
def import_video(request):
    data = request.FILES
    json.load(data)

    open(video_path, mode='rb')

def index(request):
    video_path = "/home/theo/SentimentalTranslator_Proto1/proto1/static/proto1/video/"
    list_files = [f for f in listdir(video_path) if re.match(r'[0-9a-z]*.mp4$',f)]

    context = {
        "video_list": list_files
    }
    return render(request, 'proto1/index.html', context)
