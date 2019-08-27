#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import config
import oauth2 as oauth
from requests_oauthlib import OAuth1Session
import requests
import urllib.request
#from InstagramAPI import InstagramAPI

"""
    params
"""
# https://idtwi.com/
user_id = "555508333" # @malin013
number_of_tweets = 1  #合計ツイート数

keyword = '自炊' # 発火用のキーワード
photo_path = './tmp.jpg' # 一時的に作成して投稿したら削除する
remember_path = 'least_img.txt' #最新の投稿はURLを保存しておく (二重投稿防止)

def get_client():
    CONSUMER_KEY = config.CONSUMER_KEY
    CONSUMER_SECRET = config.CONSUMER_SECRET
    ACCESS_TOKEN = config.ACCESS_TOKEN
    ACCESS_TOKEN_SECRET = config.ACCESS_TOKEN_SECRET

    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    access_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_TOKEN_SECRET)
    client = oauth.Client(consumer, access_token)

    return client


def get_tweets(client,user_id):
    url_base = "https://api.twitter.com/1.1/statuses/user_timeline.json?user_id="
    url = url_base+user_id+"&count="+str(number_of_tweets)
    results = []
    response, data = client.request(url)
    if response.status == 200:
        results = json.loads(data.decode('utf-8'))
    else:
        print(response.status)
    
    return results


def has_keyword(sentence, word):
    # return True if word is in sentence, otherwise return False
    return (word in sentence)


# https://github.com/LevPasha/Instagram-API-python
def post_instagram(photo_path, caption):
    from InstagramAPI import InstagramAPI
    InstagramAPI = InstagramAPI(config.INSTAGRAM_EMAIL_ACCOUNT, config.INSTAGRAM_PASSWORD)
    InstagramAPI.login()  # login
    InstagramAPI.uploadPhoto(photo_path, caption=caption)


def download_media(url, photo_path='./'):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(photo_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)


if __name__ == "__main__":
    with open(remember_path, 'r') as f:
        remember_url = f.read()

    client = get_client()

    results = get_tweets(client,user_id)
    for result in results:
        try:
            if(has_keyword(result['text'], keyword)):
                print("[ついーと]: " + result['text'])
                for media in result["extended_entities"]["media"]:
                    url = media['media_url']
                    if(remember_url == url):
                        continue
                    caption = result['text']
                    # 画像のダウンロード
                    download_media(url, photo_path)
                    # インスタに投稿
                    post_instagram(photo_path, caption)
                    # ダウンロードした画像の削除
                    os.remove(photo_path)
                    os.remove(remember_path)
                    with open(remember_path, 'w') as f:
                        f.write(url)
            else:
                print("自炊でない")
        except:
            print("[Error] something wrong, ask @motacapla")

