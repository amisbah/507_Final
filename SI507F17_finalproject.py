import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import urllib.request
import time
import psycopg2
import psycopg2.extras
from config import *
from psycopg2 import sql
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

plotly.tools.set_credentials_file(username='amisbah13', api_key='oJRU1rD5N7353t52nvh5')

## SETUP CACHE

CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True

try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

def get_from_cache(url):
    if url in CACHE_DICTION:
        url_dict = CACHE_DICTION[url]
        html = CACHE_DICTION[url]['html']
    else:
        html = None

    return html

def set_in_cache(url, html):
    CACHE_DICTION[url] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT)
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def get_html_from_url(url):
    html = get_from_cache(url)
    if html:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
            print()
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(url))
            print()
        browser = webdriver.Chrome()
        browser.get(url)
        delay = 3
        try:
            myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'c-compact-river')))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")

        html = browser.execute_script("return document.body.innerHTML")
        set_in_cache(url, html)
    return html

## CREATING FUNCTIONS FOR DATA EXTRACTION
def extract_video_data(soup_list):
    video_data_list = []

    for video in soup_list:
        video_title = video.find('h2')
        video_text = video_title.get_text()
        video_link = video.find('a')
        video_href = video_link.get('href')
        video_byline = video.find_next('span',{'class':'c-byline__item'})
        video_authors = video_byline.find_all('a')
        authors = []
        for author in video_authors:
            author_text = author.get_text()
            authors.append(author_text)
        video_date = video_byline.find_next('time',{'class':'c-byline__item'})
        video_date_text = video_date.get_text(strip=True)
        video_data_list.append([video_text,video_href,authors,video_date_text])

    return video_data_list

def extract_pod_data(show_soup, p_list):
    if bool(p_list):
        if DEBUG:
            print('Loading from dictionary')
    else:
        if DEBUG:
            print('Fetching from soup')
        p_list = []
        for show in p_shows:
            ## 5 iframes to access podcast episode-specific HTML for the 5 podcast shows
            p_section = show.find_next('iframe')

            browser = webdriver.Chrome()
            browser.get(p_section['src'])
            delay = 3
            try:
                myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'chorus-snippet')))
                print("Page is ready!")
            except TimeoutException:
                print("Loading took too much time!")
            while True:
                try:
                    elem1 = browser.find_element_by_class_name("awp-playlist-item-load-more")
                    browser.execute_script("arguments[0].scrollIntoView(true);", elem1)
                    time.sleep(3)
                except NoSuchElementException:
                    break
            html = browser.execute_script("return document.body.innerHTML")
            iframe_soup = Soup(html,'html.parser')
            ## Using beautiful soup to get HTML from iframes
            p_date = iframe_soup.find_all("div", class_ = "awp-playlist-item-right")
            p_title_text = []
            show_title = show.get_text()
            for date in p_date:
                p_title = date.find_next('div')
                title_text = p_title.get_text()
                date_text = date.get_text()
                p_title_text.append([show_title,title_text,date_text])
            p_list.append(p_title_text)

    return p_list

# Invoking function for videos
video_url = "https://www.vox.com/videos"
v_html = get_html_from_url(video_url)
v_soup = Soup(v_html, 'html.parser')

# video_list is the main section of videos and video_tops is the 4 headliner (or most recent) videos
video_list = v_soup.find_all('div',{'class':'c-entry-box--compact'})

video_tops = v_soup.find_all('div',{'class':'l-hero'})

# invoking extraction function
main_videos = extract_video_data(video_list)
headline_videos = extract_video_data(video_tops)

# Repeating the same steps but for the more recent archived videos
video_archives_url = "https://www.vox.com/videos/archives"
v_archives_html = get_html_from_url(video_archives_url)
v_archives_soup = Soup(v_archives_html, 'html.parser')
video_archive_list = v_archives_soup.find_all('div',{'class':'c-entry-box--compact'})

archived_videos = extract_video_data(video_archive_list)

# Adding all lists from the extract_video_data function into another list
video_dict_list = [main_videos,headline_videos,archived_videos]

# Invoking HTML scraping function and extraction function for podcasts
p_list = []

podcast_url = "https://www.vox.com/pages/podcasts"
p_html = get_html_from_url(podcast_url)
p_soup = Soup(p_html, 'html.parser')
p_shows = p_soup.find_all('h4')

p_list = extract_pod_data(p_shows,p_list)

# Creating class definition for Video objects
class Video(object):
    def __init__(self,object):
        self.title = object[0]
        self.url = object[1]
        self.authors = object[2]
        self.date = object[3]

    def __repr__(self):
        return "By {}".format(', '.join(self.authors))

    def __contains__(self,val):
        return "{} in video title.".format(val)

    def get_video_dict(self):
        return {
            'video_title': self.title,
            'video_url':self.url,
            'authors':self.__repr__(),
            'video_date':self.date
        }

# Creating instances of Videos
video_objects = []
for eachlist in video_dict_list:
    for video in eachlist:
        video_objects.append(Video(video))

# Creating class definition for Podcast objects
class Podcast(object):
    def __init__(self,pod_list):
        self.showtitle = pod_list[0]
        self.eptitle = pod_list[1]
        self.epdate = pod_list[2]

    def get_pod_dict(self):
        return {
            'pod_title':self.eptitle,
            'pod_date':self.epdate
        }

# Creating instances of Podcast objects
pod_show_objects = []
for eachlist in p_list:
    for each in eachlist:
        pod_show_objects.append(Podcast(each))

# Setting up database connection
def get_connection_and_cursor():
    try:
        if db_password != "":
            db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
            print("Success connecting to database")
        else:
            db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
    except:
        print("Unable to connect to the database. Check server and credentials.")
        sys.exit(1) # Stop running program if there's no db connection.

    db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

conn, cur = get_connection_and_cursor()

# Creating the two tables
cur.execute("""CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    video_title VARCHAR(128),
    url VARCHAR(500),
    authors VARCHAR(255),
    video_date VARCHAR(128)
    )""");


cur.execute("""CREATE TABLE IF NOT EXISTS podcasts(
    id SERIAL PRIMARY KEY,
    podcast_title VARCHAR(255),
    pod_date VARCHAR(128)
)""")

conn.commit()

# Inserting data into tables using objects
for video in video_objects:
    cur.execute("""INSERT INTO videos (video_title,url,authors,video_date) VALUES (%(video_title)s,%(video_url)s,%(authors)s,%(video_date)s) ON CONFLICT DO NOTHING""", video.get_video_dict())

for pod in pod_show_objects:
    cur.execute("""INSERT INTO podcasts (podcast_title,pod_date) VALUES (%(pod_title)s,%(pod_date)s) ON CONFLICT DO NOTHING""", pod.get_pod_dict())

conn.commit()

# Querying data for visualization
cur.execute("""SELECT COUNT(*) FROM videos WHERE video_title ILIKE '%border%' """)
border_videos = cur.fetchall()


cur.execute("""SELECT COUNT(*) FROM podcasts WHERE podcast_title ILIKE '%border%' """)
border_pods = cur.fetchall()


cur.execute("""SELECT COUNT(*) FROM videos WHERE video_title LIKE '%health%' """)
health_videos = cur.fetchall()


cur.execute("""SELECT COUNT(*) FROM podcasts WHERE podcast_title LIKE '%health%' """)
health_pods = cur.fetchall()


cur.execute("""SELECT COUNT(video_title) FROM videos WHERE video_title LIKE '%DC%' """)
dc_videos = cur.fetchall()


cur.execute("""SELECT COUNT(podcast_title) FROM podcasts WHERE podcast_title LIKE '%DC%' """)
dc_pods = cur.fetchall()


cur.execute("""SELECT COUNT(video_title) FROM videos WHERE video_title ILIKE '%music%' """)
music_videos = cur.fetchall()


cur.execute("""SELECT COUNT(podcast_title) FROM podcasts WHERE podcast_title ILIKE '%music%' """)
music_pods = cur.fetchall()

# Configuring barchart
trace1 = go.Bar(
    x = ["Border","Health","DC","Music"],
    y = [border_videos[0]['count'],health_videos[0]['count'],dc_videos[0]['count'],music_videos[0]['count']],
    name = 'Vox Videos'
    )

trace2 = go.Bar(
    x = ["Border","Health","DC","Music"],
    y = [border_pods[0]['count'],health_pods[0]['count'],dc_pods[0]['count'],music_pods[0]['count']],
    name = 'Vox Podcasts'
    )

data = [trace1, trace2]
layout = go.Layout(
    barmode='group'
    )

fig = go.Figure(data = data, layout = layout)
py.plot(fig, filename ='vox-grouped-bar', sharing = 'public')

# Please find graph's URL in the terminal

