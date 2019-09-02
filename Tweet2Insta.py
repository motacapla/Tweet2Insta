#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import config
import pandas as pd
import urllib.request
import mysql.connector as mydb
import subprocess as sp


#sp.call(["twitterscraper", keyword, "-l "+limit, "-o"+output_path])


"""
    params
"""
sleep_time = 120

#user = "malin013"
#keyword = "自炊 from:"+user
keyword = "スタバ"
limit = "1000"

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
path = './html/'
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


def make_html_url(df):
    df['html_url'] = ""
    for i,data in enumerate(df['text']):
        for d in data.split(' '):
            if 'pic.twitter.com' in d:
                df['html_url'][i] = d
    df['html_url'][48] = "pic.twitter.com/3bjq157lU1"
    return df


def get_image_from_html(html):
    from bs4 import BeautifulSoup
    with open(html, mode='r') as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    photo_path = ""
    img = soup.find("meta", attrs={'property': 'og:image', 'content': True})
    if img is not None:
        if ':large' in img['content']:
            img['content'] = img['content'][:-6]
        print(img['content'])
        photo_path = img['content'].split('/')[-1]
        download_media(img['content'], img_path+photo_path)
    else:
        pass
    return photo_path


def post_instragram_store_db(df):
    # insert into MySQL and post Instagram if it is new 
    for i in range(len(df)):
        new_data = False
        try:
            img_name = img_path+df['img_url'][i].split('/')[-1]
            print(df['tweet_id'][i], df['timestamp'][i], df['text'][i], img_name)
            cur.execute("INSERT INTO tweets VALUES (%s, %s, %s, %s)", (int(df['tweet_id'][i]), df['timestamp'][i], df['text'][i], img_name))
            new_data = True
        except:
            print("Already there is data")
        finally: 
            if new_data and len(img_name) >= 7:
                print("New tweet is found. Trying to post in Instragram...")
                post_instagram(img_name, df['text'][i])
                time.sleep(sleep_time)
    conn.commit()


# https://github.com/LevPasha/Instagram-API-python
def post_instagram(photo_path, caption):
    from InstagramAPI import InstagramAPI
    InstagramAPI = InstagramAPI(config.INSTAGRAM_EMAIL_ACCOUNT, config.INSTAGRAM_PASSWORD)
    InstagramAPI.login()  # login
    InstagramAPI.uploadPhoto(photo_path, caption=caption)


if __name__ == '__main__':
    if not os.path.exists(output_path):
        sp.call(["twitterscraper", keyword, "-l "+limit, "-o"+output_path])
    else:
        print(output_path + " is found, skip scraping...")
    df = pd.read_json(output_path, encoding='utf-8')
    df = make_html_url(df)

    if len([name for name in os.listdir(path)]) == 0:
        # Extract html from text(e.g., pic.twitter.com/hogefugapiyo)
        for d in df['html_url']:
            if d != "":
                download_media("https://"+d, path+d.split('/')[-1]+'.html')
    else:
        print("html found, skip downloading html...")
    # Extract image from html files
    df['img_url'] = ""
    for i,d in enumerate(df['html_url']):
        html_path = path+d.split('/')[-1]+'.html'
        if './html/.html' in html_path:
            continue 
        df['img_url'][i] = img_path+get_image_from_html(html_path)

    # Store data into MySQL
    # post_instragram_store_db(df)

    cur.close()
    conn.close()

