#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import config
import pandas as pd
import urllib.request
import mysql.connector as mydb
import subprocess as sp
import re
import tweepy
from PIL import Image

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

"""
    params
"""
user = "malin013"
keyword = "自炊"
limit = 1000

"""
    settings
"""
# インスタグラムの投稿感覚
sleep_time = 120

# 画像リサイズのアスペクト比 4:5
ratio_width = 4
ratio_height = 5


conn = mydb.connect(
    host='localhost',
    port='3306',
    user='hoge',
    password='root',
    database='tweet2insta'
)
cur = conn.cursor()

img_path = './img/'
output_path = "data.json"
img_url = []

"""
    funcs
"""
def download_media(url, photo_path='./'):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(photo_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)


pattern = r"pic.twitter.com/[a-zA-Z0-9]{10}"
reg = re.compile(pattern)
def extract_pics_url(sentence):
    m = reg.search(sentence)
    if m == None:
        return ""
    return m.group(0)

# Downloading img from tweet url
def get_image_from_url(url):
    from bs4 import BeautifulSoup
    photo_path = ""
    with urllib.request.urlopen(url) as web_file:
        data = web_file.read()
        soup = BeautifulSoup(data, "html.parser")
        img = soup.find("meta", attrs={'property': 'og:image', 'content': True})
        if img is not None:
            if ':large' in img['content']:
                img['content'] = img['content'][:-6]
            if not 'profile_images' in img['content']:
                print(img['content'])
                photo_path = img['content'].split('/')[-1]
                download_media(img['content'], img_path+photo_path)
        else:
            pass
    return photo_path

# Storing data in DB and Post instagram
def store_db(df):
    for i in range(len(df)):
        cur.execute("SELECT id from tweets WHERE id = %s", (int(df['tweet_id'].iloc[i]),))
        row = cur.fetchone()
        if row == "" or row == None:
            if img_url[i] == "" or img_url[i] == None or img_url[i] == './img/':
                continue            
            img_name = img_path+img_url[i].split('/')[-1]
            print(df['tweet_id'].iloc[i], df['timestamp'].iloc[i], df['text'].iloc[i], img_name)
            # Insert into db
            cur.execute("INSERT INTO tweets VALUES (%s, %s, %s, %s)", (int(df['tweet_id'].iloc[i]), df['timestamp'].iloc[i], df['text'].iloc[i], img_name))
            conn.commit()
            # Change aspect ratio
            resize_img(img_name)
            # Post instagram
            post_instagram(img_name, df['text'].iloc[i])
            time.sleep(sleep_time)
        else:
            print("This tweet has already been posted on Instagram")

# Instagram requires a picture with 4:5 aspect ratio
def resize_img(url):
    img = Image.open(url)
    if img.width > img.height:
        img_resize = img.resize((int(img.height*ratio_width/ratio_height), img.height), Image.LANCZOS)
    else :
        img_resize = img.resize((img.width, int(img.width*ratio_height/ratio_width)), Image.LANCZOS)
    img_resize.save(url)


# https://github.com/LevPasha/Instagram-API-python
def post_instagram(photo_path, caption):
    from InstagramAPI import InstagramAPI
    InstagramAPI = InstagramAPI(config.INSTAGRAM_EMAIL_ACCOUNT, config.INSTAGRAM_PASSWORD)
    InstagramAPI.login()  # login
    InstagramAPI.uploadPhoto(photo_path, caption=caption)


# Get specified tweets include keyword from a user 
def get_tweets():
    tweet_data = pd.DataFrame()
    for tweet in tweepy.Cursor(api.user_timeline, screen_name = user, exclude_replies = True).items(limit):
        url = "http://twitter.com/"+str(user)+"/status/"+str(tweet.id)
        if keyword in tweet.text :
            tmp = pd.DataFrame({'tweet_id': tweet.id, 'timestamp': tweet.created_at, 'text': tweet.text.replace('\n',''), 'tweet_url': url}, index=['datetime',])
            tweet_data = pd.concat([tweet_data, tmp])
    return tweet_data


if __name__ == '__main__':
    # Get tweets
    df = get_tweets()
    print(df.head())
    if(df.empty):
        print("no data")
        sys.exit(0)

    # Extract image from tweet_url
    for i,d in enumerate(df['tweet_url']):
        img_url.append(img_path+get_image_from_url(d))

    # Store data into MySQL
    store_db(df)
    cur.close()
    conn.close()
