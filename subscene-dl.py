# -*- coding: utf-8 -*-
import sys
import re #regex
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWeb"
                  "Kit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safa"
                  "ri/537.36" }
site = "https://subscene.com"

def get_html(url):
    request = Request(url, None, header)
    html = urlopen(request).read().decode("utf-8")
    return html

def get_movie_links(soup):
    found_movie_links = []
    for link in soup.find_all('a'): # <A>
        if "subtitles/" + title in link.get('href'):
            found_movie_links.append(link.get('href'));

    return found_movie_links

#FIX
def get_subtitles(soup):
    for table in soup.find_all('tbody'): # <tr>
        print(table)

def check_imdb(soup):
    for imdb_link in soup.find_all("a", class_="imdb"):
        if imdb in imdb_link.get('href'):
            return True
    return False

class subtitle:
    def __init__(url, lang, hearing_impaired, user):
        self.url = url
        self.lang = lang
        self.hearing_impaired = hearing_impaired
        self.user = user

#url = sys.argv[1]
#language = sys.argv[1]
title = sys.argv[1]
year = sys.argv[2]
imdb = sys.argv[3]

url = site + "/subtitles/title?q=" + title

soup_search = BeautifulSoup(get_html(url), 'html.parser')
for movie_link in get_movie_links(soup_search):
    soup_movie = BeautifulSoup(get_html(site + movie_link), 'html.parser')
    if check_imdb(soup_movie) == True:
        found_movie_soup = soup_movie
        break

get_subtitles(found_movie_soup)
