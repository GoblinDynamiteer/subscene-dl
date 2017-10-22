# -*- coding: utf-8 -*-
import sys
import re #regex
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve
import urllib

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

    exact_match = soup.find_all('h2', class_="exact")
    if len(exact_match) == 0:
        return found_movie_links #No exact matches

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
    #print("Subs found:" + str(found) + " Skipped: " + str(failed))
    return subtitles

# Check movie pages for matching IMDb-id
def check_imdb(soup):
    for imdb_link in soup.find_all("a", class_="imdb"):
        if imdb in imdb_link.get('href'):
            #print("Found IMDB-id!")
            return True
    return False

def check_release_name(soup):
    matches = soup.find_all('span')
    for match in matches:
        if release_name in match.text.strip():
            #print("Found release name!")
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
        self.download_link = None

    def print_info(self):
        print("Url: " + site + self.url)
        print("Language: " + self.lang)
        print("Release: " + self.release)
        print("Uploader: " + self.user)
        print("Comment: " + strip_invalid_chars(self.comment))
        hi = "HI" if self.hearing_impaired else "Not HI"
        print("Hearing impaired: " + hi)

    def matches_relase_name(self):
        return True if self.release == release_name else False

    def download_url(self):
        if self.download_link:
            return site + self.download_link

        else:
            soup = make_soup(site + self.url)
            self.download_link = soup.find('div', class_ = 'download').find('a').get('href')
            return site + self.download_link

#Test args: jungle tt3758172 Jungle.2017.1080p.WEB-DL.H264.AC3-EVO
#arguments = len(sys.argv)

title = sys.argv[1].replace(" ", "+")         #Jungle
imdb = sys.argv[2]          #tt3758172
release_name = sys.argv[3]  #Jungle.2017.1080p.WEB-DL.H264.AC3-EVO

soup_search = make_soup(site + "/subtitles/title?q=" + title);
#search by release ... subtitles/release?q=

found = False
count = 0

for movie_link in get_movie_links(soup_search):
    soup_movie = make_soup(site + movie_link);
    count += 1
    #print("Searching.")
    if count > 10:
        break
    if check_imdb(soup_movie) or check_release_name(soup_movie):
        found = True
        subtitles = get_subtitles(soup_movie)
        break

if found == False:
    print("Did not find movie!")

else:
    for sub in subtitles:
        if sub.lang == "English" and sub.matches_relase_name():
            print(sub.download_url())
            break;
