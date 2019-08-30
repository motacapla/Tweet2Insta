import time
import config
import urllib.request
import mysql.connector as mydb

# sec
sleep_time = 15

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

conn = mydb.connect(
    host='localhost',
    port='3306',
    user='root',
    password='root',
    database='tweet2insta'
)
cur = conn.cursor()
cur.execute("SELECT * FROM tweets")
rows = cur.fetchall()

# tweet_id, datetime, text, img_path
for row in rows:
    # remove './img/'
    if len(row[3]) < 7:
        continue 
    #print(row[3], row[2])
    post_instagram(row[3], row[2])
    time.sleep(sleep_time)


