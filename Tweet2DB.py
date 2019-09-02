#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import config
import pandas as pd
import urllib.request
import mysql.connector as mydb
import subprocess as sp
import re

"""
    params
"""
#user = "malin013"
#keyword = "自炊 from:"+user
keyword = "スタバ"
limit = str(20*1000)

conn = mydb.connect(
    host='localhost',
    port='3306',
    user='root',
    password='root',
    database='tweet2insta'
)
cur = conn.cursor()

"""
    settings(do not touch)
"""
img_path = './img/'
output_path = "data.json"

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


def store_db(df):
    # insert into MySQL and post Instagram if it is new 
    for i in range(len(df)):
        try:
            img_name = img_path+df['img_url'][i].split('/')[-1]
            print(df['tweet_id'][i], df['timestamp'][i], df['text'][i], img_name)
            cur.execute("INSERT INTO tweets VALUES (%s, %s, %s, %s)", (int(df['tweet_id'][i]), df['timestamp'][i], df['text'][i], img_name))
        except:
            print("Already there is data")
    conn.commit()


# https://github.com/LevPasha/Instagram-API-python
def post_instagram(photo_path, caption):
    from InstagramAPI import InstagramAPI
    InstagramAPI = InstagramAPI(config.INSTAGRAM_EMAIL_ACCOUNT, config.INSTAGRAM_PASSWORD)
    InstagramAPI.login()  # login
    InstagramAPI.uploadPhoto(photo_path, caption=caption)


if __name__ == '__main__':
    # Scraping
    if not os.path.exists(output_path):
        sp.call(["twitterscraper", keyword, "-l "+limit, "-o"+output_path])
    else:
        print(output_path + " is found, skip scraping...")
    df = pd.read_json(output_path, encoding='utf-8')

    # Extract image from html url
    df['img_url'] = ""
    for i,d in enumerate(df['tweet_url']):
        html_path = "https://twitter.com" + str(d)
        df['img_url'][i] = img_path+get_image_from_url(html_path)
        print(df['text'][i])

    # Store data into MySQL
    store_db(df)

    cur.close()
    conn.close()