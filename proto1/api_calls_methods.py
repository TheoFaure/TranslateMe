import http.client, urllib.request, urllib.parse, urllib.error
import json
import re
import time
import sys
import subprocess
from xml.etree import ElementTree
from base64 import b64encode

import unicodedata

emo_api_key = open('proto1/api_keys/microsoft_emo', 'r').readline()

speech_api_key = open('proto1/api_keys/microsoft_speech', 'r').readline()
text_analytics_api_key = open('proto1/api_keys/microsoft_text_analytics', 'r').readline()
translation_api_key = open('proto1/api_keys/microsoft_translation', 'r').readline()
token_speech_to_text = ''
token_translation = ''

yandex_api_key = open('proto1/api_keys/yandex_translation', 'r').readline()

username_IBM = open('proto1/api_keys/ibm_user', 'r').readline()
password_IBM = open('proto1/api_keys/ibm_password', 'r').readline()
userAndPass = b64encode(("%s:%s" % (username_IBM, password_IBM)).encode("ascii")).decode("ascii")


def send_request(method, host, url, body=None, params=None, headers=None):
    try:
        conn = http.client.HTTPSConnection(host)
        if params is None:
            if body is None:
                conn.request(method, url, headers=headers)
            else:
                conn.request(method, url, body=body, headers=headers)
        else:
            if body is None and headers is None:
                conn.request(method, "%s?%s" % (url, params))
            else:
                conn.request(method, "%s?%s" % (url, params), body=body, headers=headers)
        response = conn.getresponse()
        data = response.read()
        headers = response.getheaders()
        status = response.status
        conn.close()
        return data, headers, status
    except Exception as e:
        print("Error. HTML Response: ")
        print(response.status)
        print(response.read().decode('utf-8'))
        print(response.getheaders())
        raise e


def send_video_emo_api(video_path):
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': emo_api_key,
    }

    params = urllib.parse.urlencode({
        'outputStyle': 'aggregate',
    })

    with open(video_path, mode='rb') as file: # b is important -> binary
        file_content = file.read()

        try:
            data, headers, status = send_request("POST", 'westus.api.cognitive.microsoft.com', "/emotion/v1.0/recognizeinvideo",
                                    headers=headers, body=file_content, params=params)
            results_url = [tuple for tuple in headers if "Operation-Location" in tuple][0][1]
            print("Url to get the results : curl \"{results_url}\" -H \"Ocp-Apim-Subscription-Key:{emo_api_key}\"".format(results_url=results_url, emo_api_key=emo_api_key))
            return results_url
        except Exception as e:
            print("Error. HTML Response: ")
            print(data)
            print(status)
            print(headers)
            raise e


def get_video_emo_response(results_url):
    headers = {
        'Ocp-Apim-Subscription-Key': emo_api_key,
    }

    timeout = 0
    while not timeout > 100:
        regex = r"[a-z0-9-]+$"
        matches = re.finditer(regex, results_url)
        results_url_num = [m.group() for m in matches][0]
        results_url_ext = "/emotion/v1.0/operations/" + str(results_url_num)

        print("The API is processing the video, this might take time.")
        time.sleep(30)

        try:
            data, headers, status = send_request("POST", 'westus.api.cognitive.microsoft.com', results_url_ext,
                                    headers=headers)
        except Exception as e:
            raise e

        if "Succeeded" in str(data):
            return data
        timeout += 1
        print("Getting the results... Attempted {timeout} times.".format(timeout=timeout))
        print(data)

    return "Timeout!"


def get_video_emo(results_url):
    headers = {
        'Ocp-Apim-Subscription-Key': emo_api_key,
    }

    try:
        regex = r"[a-z0-9-]+$"
        matches = re.finditer(regex, results_url)
        results_url_num = [m.group() for m in matches][0]
        results_url_ext = "/emotion/v1.0/operations/" + str(results_url_num)

        data, headers, status = send_request("GET", 'westus.api.cognitive.microsoft.com', results_url_ext, headers=headers)
        return data
    except Exception as e:
        raise e


def create_audio_file(video_path):
    command = "ffmpeg -i {video_path} -ab 160k -ac 2 -ar 44100 -vn {video_path}.wav".format(video_path=video_path)
    subprocess.call(command, shell=True)
    return "{video_path}.wav".format(video_path=video_path)


def speech_to_text(audio_path):
    try:
        get_token_speech_to_text()
        print(token_speech_to_text)
        # regenerate token every 10 minutes!
        text = get_speech(audio_path)
        return text
    except Exception as e:
        raise e


def get_token_speech_to_text():
    print("Getting access token for speech recognition")
    headers = {
        'Ocp-Apim-Subscription-Key': speech_api_key,
        'Content-Length': 0,
    }
    global token_speech_to_text

    try:
        data, headers, status = send_request("POST", 'api.cognitive.microsoft.com', "/sts/v1.0/issueToken",
                                             headers=headers)
        token_speech_to_text = data.decode('utf-8')
    except Exception as e:
        raise e


def get_speech(audio_path):
    headers = {
        'Content-Type': 'audio/wav',
        'Authorization': 'Bearer {token}'.format(token=token_speech_to_text)
    }

    params = urllib.parse.urlencode({
        'outputStyle': 'aggregate',
        'scenarios': 'catsearch',
        'appid': 'D4D52672-91D7-4C74-8AD8-42B1D98141A5',
        'locale': 'en-US',
        'device.os': 'Ubuntu16.04',
        'version': 3.0,
        'format': 'json',
        'requestid': '1d4b6030-9099-11e0-91e4-0800200c9a66',
        'instanceid': '1d4b6030-9099-11e0-91e4-0800200c9a66'
    })

    with open(audio_path, mode='rb') as file:  # b is important -> binary
        file_content = file.read()

        try:
            data, headers, status = send_request("POST", "speech.platform.bing.com", "/recognize",
                                    headers=headers, body=file_content, params=params)
            json_obj = json.loads(data.decode('utf-8'))
            return json_obj['header']['name']
        except Exception as e:
            print(json_obj)
            raise e


def speech2text_ibm(audio_path):
    headers = {
        'Content-Type': 'audio/wav',
        'Authorization': 'Basic %s' % userAndPass
    }

    with open(audio_path, mode='rb') as file:  # b is important -> binary
        file_content = file.read()

        try:
            data, headers, status = send_request("POST", "stream.watsonplatform.net", "/speech-to-text/api/v1/recognize",
                                    headers=headers, body=file_content)
            json_obj = json.loads(data.decode('utf-8'))
            return json_obj['results'][0]['alternatives'][0]['transcript']
        except Exception as e:
            print(json_obj)
            raise e




def get_sentiment_text(text, language):
    headers = {
        'Ocp-Apim-Subscription-Key': text_analytics_api_key,
        'Content-Type': 'text/json',
    }

    body = ("{\"documents\": [{\"language\": \"%s\", \"id\": \"text\", \"text\": \"%s\"}]}" % (language, text))

    try:
        data, headers, status = send_request("POST", 'westus.api.cognitive.microsoft.com', "/text/analytics/v2.0/sentiment", headers=headers, body=body)
        json_obj = json.loads(data.decode('utf-8'))
        return json_obj['documents'][0]['score']
    except Exception as e:
        raise e


def get_token_translation():
    print("Getting access token for text translation")
    headers = {
        'Ocp-Apim-Subscription-Key': translation_api_key,
        'Content-Length': 0,
    }
    global token_translation

    try:
        data, headers, status = send_request("POST", 'api.cognitive.microsoft.com', "/sts/v1.0/issueToken", headers=headers)
        token_translation = data.decode('utf-8')
    except Exception as e:
        raise e


def get_microsoft_translation(text, language):
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token_translation)
    }

    params = urllib.parse.urlencode({
        'text': text,
        'to': language,
    })

    try:
        data, headers, status = send_request("GET", 'api.microsofttranslator.com', "/v2/http.svc/Translate", headers=headers, params=params)
        tree = ElementTree.fromstring(data.decode('utf-8'))
        return tree.text
    except Exception as e:
        raise e


def translate_microsoft(text, language):
    get_token_translation()
    translation = get_microsoft_translation(text, language)
    return translation


def translate_yandex(text, language):
    params = urllib.parse.urlencode({
        'key': yandex_api_key,
        'text': text,
        'lang': language,
    })

    try:
        data, headers, status = send_request("GET", 'translate.yandex.net', "/api/v1.5/tr.json/translate", params=params)
        json_obj = json.loads(data.decode('utf-8'))
        return json_obj['text'][0]
    except Exception as e:
        raise e


if __name__ == '__main__' and len(sys.argv) > 1:
    try:
        video_path = sys.argv[1]
        api_response = send_video_emo_api(video_path)
        audio_path = create_audio_file(video_path)
        print("Audio file created at: %s" % audio_path)
        text_video = speech2text_ibm(audio_path)
        print("Speech-to-text finnished. The video says: %s" % text_video)
        sentiment = get_sentiment_text(text_video, "en")
        print("The sentiment captured in this text is %s" % sentiment)

        microsoft_translated = translate_microsoft(text_video, "fr")
        print("Translated by Microsoft: %s" % microsoft_translated)
        microsoft_sentiment = get_sentiment_text("".join((c for c in unicodedata.normalize('NFD', microsoft_translated.replace("’", " ")) if unicodedata.category(c) != 'Mn')), "fr")
        print("Microsoft sentiment: %s" % microsoft_sentiment)

        yandex_translated = translate_yandex(text_video, "fr")
        print("Translated by Yandex: %s" % yandex_translated)
        yandex_sentiment = get_sentiment_text("".join((c for c in unicodedata.normalize('NFD', yandex_translated) if unicodedata.category(c) != 'Mn')), "fr")
        print("Yandex sentiment: %s" % yandex_sentiment)

        #delete the audio file
        command = "rm {video_path}.wav"
        subprocess.call(command, shell=True)

        emo_video = get_video_emo_response(api_response)

        print("\n The emotion captured from the video is:")
        print(emo_video)

    except Exception as e:
        print("Somewhere, something went wrong.")
