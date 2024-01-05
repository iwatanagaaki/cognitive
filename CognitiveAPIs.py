import requests
import json

def recognizeFace(filename):
    subscription_key = '17026dde24924755a51598f003a09946'
    face_api_url = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'
    Request_URL = face_api_url + 'detect'

    Request_headers = {
        #Request_bodyで送る内容がバイナリ形式
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

    Request_params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,smile,glasses,emotion,makeup,hair,accessories',
    }

    with open(filename, 'rb') as f:
        Request_body = f.read()

    response = requests.post(Request_URL, headers=Request_headers, params=Request_params, data=Request_body)
    analysis = response.json()

    response_list = []
    for x in analysis:
        #forで繰り返すごとにresponse_dicを空にする
        response_dic = {}

        response_dic['faceId'] = x['faceId']
        response_dic['faceRectangle'] = x['faceRectangle']
        response_dic['age'] = x['faceAttributes']['age']
        response_dic['gender'] = x['faceAttributes']['gender']
        
        response_list.append(response_dic)

    return response_list


def recognizeImage(filename):
    subscription_key = '345bda86aa7d43aa8c66f1a5694e4d82'
    vision_base_url = 'https://eastasia.api.cognitive.microsoft.com/vision/v1.0/'
    Request_URL = vision_base_url + 'ocr'

    Request_headers = {
        #Content-TypeはRequest_bodyで送る内容がバイナリですよという意味。application/jsonの場合はjsonフォーマット(pythonでの辞書)で送るという事。
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key
    }

    #language unkはAutoDetect(自動判別)、
    Request_params = {'language': 'unk', 'detectOrientation': 'true'}

    #バイナリモードでファイルを読み込み
    with open(filename, 'rb') as f:
        Request_body = f.read()

    #headers= params= data= は名前付き引数という headers, paramsは辞書型、dataはバイナリ
    response = requests.post(Request_URL, headers=Request_headers, params=Request_params, data=Request_body)

    #バイナリのresponseを辞書型（pythonで扱えるjsonフォーマット）に変換
    analysis = response.json()

    response_text = ''

    for region in analysis['regions']:
        for line in region['lines']:
            for word in line['words']:
                response_text += word['text']
    
    return response_text


