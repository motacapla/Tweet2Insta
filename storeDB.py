#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
import urllib.request
import mysql.connector as mydb

path = './html/'
img_path = './img/'
df = pd.read_json('data.json', encoding='utf-8')

def make_html_url(df):
    df['html_url'] = ""
    for i,data in enumerate(df['text']):
        for d in data.split(' '):
            if 'pic.twitter.com' in d:
                df['html_url'][i] = d
    df['html_url'][48] = "pic.twitter.com/3bjq157lU1"
    return df
df = make_html_url(df)

def download_media(url, photo_path='./'):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(photo_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)

for d in df['html_url']:
    if d != "":
        print(d)
        download_media("https://"+d, path+d.split('/')[-1]+'.html')

def get_image(html):
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
        download_media(img['content'], path+photo_path)
    else:
        pass
    return photo_path
        #print('!!not found og:image tag!!')

# Extract image from html files
df['img_url'] = ""
for i,d in enumerate(df['html_url']):
    html_path = path+d.split('/')[-1]+'.html'
    if './html/.html' in html_path:
        continue 
    df['img_url'][i] = img_path+get_image(html_path)

def store_db(df):
    conn = mydb.connect(
        host='localhost',
        port='3306',
        user='root',
        password='root',
        database='tweet2insta'
    )

    cur = conn.cursor()
    # insert into MySQL
    for i in range(len(df)):
        try:
            print(df['tweet_id'][i], df['timestamp'][i], df['text'][i], img_path+df['img_url'][i].split('/')[-1])
            cur.execute("INSERT INTO tweets VALUES (%s, %s, %s, %s)", (int(df['tweet_id'][i]), df['timestamp'][i], df['text'][i], img_path+df['img_url'][i].split('/')[-1]))
        except:
            print("Already there is data")
    cur.close()
    conn.commit()
    conn.close()

store_db(df)