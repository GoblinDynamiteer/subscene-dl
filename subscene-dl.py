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
            found_movie_links.append(link.get('href'))

    return found_movie_links

#FIX
def get_subtitles(soup):
    subtitles = []
    tables = soup.findChildren('table')
    rows = tables[0].findChildren('tr')
    failed = 0
    found = 0
    for row in rows:
        cols = row.findChildren('td')
        try:
            link = cols[0].find('a').get('href')
            lang = cols[0].text.strip()
            cut = re.sub('\s\s+', '|', lang).split('|')
            lang = cut[0]
            release = cut[1]
            user = cols[3].text.strip()
            comment = cols[4].text.strip()
            subtitles.append(Subtitle(link, lang, release, user, comment))
            found += 1
        except:
            failed += 1
            pass
    print("Found:" + str(found) + " Skipped: " + str(failed))
    return subtitles

# Check movie pages for matching IMDb-id
def check_imdb(soup):
    for imdb_link in soup.find_all("a", class_="imdb"):
        if imdb in imdb_link.get('href'):
            return True
    return False

# Generate soup from url
def make_soup(url):
    success = False
    while success == False:
        try:
            soup = BeautifulSoup(get_html(url), 'html.parser')
            success = True
        except:
            pass
    return soup

def strip_invalid_chars(string):
    return re.sub('[^\x00-\x7f]',' ', string)

def string_hearing_impaired(string):
    string = strip_invalid_chars(string)
    hi = re.compile('\sSDH', re.IGNORECASE) #Add more
    nohi = re.compile('NON.SDH', re.IGNORECASE) #Add more
    result_hi = hi.search(string)
    result_nohi = nohi.search(string)
    # FIX return values#
    if result_hi != None and result_nohi == None:
        return True
    if result_hi == None:
        return False
    if result_hi != None and result_nohi != None:
        return False

class Subtitle:
    def __init__(self, url, lang, release, user, comment):
        self.url = url
        self.lang = lang
        self.release = release
        self.user = user
        self.comment = comment
        self.hearing_impaired = string_hearing_impaired(comment)

    def print_info(self):
        print("Url: " + site + self.url)
        print("Language: " + self.lang)
        print("Release: " + self.release)
        print("Uploader: " + self.user)
        print("Comment: " + strip_invalid_chars(self.comment))
        hi = "HI" if self.hearing_impaired else "Not HI"
        print("Hearing impaired: " + hi)

    def download(self):
        print("Downloading.... ")


#url = sys.argv[1]
#language = sys.argv[1]
title = sys.argv[1]
year = sys.argv[2]
imdb = sys.argv[3]

soup_search = make_soup(site + "/subtitles/title?q=" + title);

for movie_link in get_movie_links(soup_search):
    soup_movie = make_soup(site + movie_link);
    if check_imdb(soup_movie) == True:
        found_movie_soup = soup_movie
        break

subtitles = get_subtitles(found_movie_soup)
for sub in subtitles:
    if sub.lang == "English":
        sub.print_info()
        print("\n")
