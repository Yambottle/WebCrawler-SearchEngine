#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*-
# @Time    : 3/19/18 19:09
# @Author  : Yam
# @Site    : 
# @File    : mainCrawler.py
# @Software: PyCharm

import urllib.request
import urllib.robotparser
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import re
from nltk import stem
import hashlib
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

starturl = "http://s2.smu.edu/~fmoore"
starturl2 = "http://lyle.smu.edu/~fmoore"
headers = {'User-Agent': 'YamCrawler'}  # add a user-agent name
history = []
waiting = []
img = []
file = []
docID = []
docMap = {}
words = []
titlewords = []
stemwords = []
count_vect = CountVectorizer()
tfMap = {}
stopwords = ['to', 'be', 'not']
# time delay


def init():
    waiting.append(starturl+"/index.htm")
    print('Init Crawler......')


# parse robots.txt
def read_robots(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url + "/robots.txt")
    rp.read()
    return rp


def suburl(url):
    sub = url.split(starturl)[1]
    return sub


# crawl
def get_data(url, robotparser):
    # doesn't work...Because just match /dontgohere/, now it works
    if robotparser.can_fetch("*", suburl(url)):
        request = urllib.request.Request(url=url, headers=headers)
        print("Now URL:"+url)
        response = urllib.request.urlopen(request)
        data = response.read()
        data = data.decode('utf-8')
        history.append(url)
        # print("All History:"+''.join(str(e) for e in history))
        return data
    else:
        return None


# page perser
def page_perser(inpage):
    soup = BeautifulSoup(inpage, 'html.parser')
    print("Now Title:"+soup.title.string)
    for nextlink in soup.find_all('a'):
        linkstr = nextlink.get('href')
        newlink = url_filter(linkstr)
        if newlink is not None:
            waiting.append(newlink)
    # print("All Waiting:"+', '.join(str(e) for e in waiting))
    return soup.title.string, soup.get_text()


def url_filter(inlink):
    if inlink.startswith(starturl) | inlink.startswith(starturl2):
        return inlink
    elif inlink.startswith('http') | inlink.startswith('mailto:'):
        print("\n"+inlink+" This is an out-going link.\n")
        return None
    else:
        inlink = starturl+'/'+inlink
        return inlink


# valid word filter
def valid_filter(instr):
    outstr = re.findall('[a-z]+', instr)
    return outstr


# stemming
def stem_filter(instr):
    newstr = []
    stemmer = stem.PorterStemmer()
    for flagstr in instr:
        flagstr = stemmer.stem(flagstr)
        newstr.append(flagstr)
    return newstr


# exact duplicate detection(just about the content text): fingerprint as DocID
def gen_fingerprint(instr):
    encrypter = hashlib.md5()
    encrypter.update(instr.encode('utf-8'))
    return encrypter.hexdigest()


# output term-doc matrix
def analyze_str(inwords):
    bag_words = count_vect.fit_transform(inwords)
    # print(count_vect.vocabulary_)
    pd.options.display.max_columns = 999
    df = pd.DataFrame(data=bag_words.toarray(), columns=count_vect.get_feature_names())
    # print(df)
    # print(df.sum().sort_values()[-20:])
    return df


def run_crawler():
    pagestr = ""
    titlestr = ""
    init()
    rparser = read_robots(starturl)
    crawlnum = 1
    totalnum = input("Enter number of pages:")
    #totalnum = 60
    stopwords = input("Enter stopwords:(seperate by ,)")

    while crawlnum < int(totalnum):
        if len(waiting) == 0:
            break
        link = waiting.pop(0)
        if link not in history:
            if link.startswith("http://lyle"):
                history.append(link)
                print("Here replace URL from lyle to s2. ")
                link = link.replace("lyle", "s2")
            if link.endswith('htm') | link.endswith('html') | link.endswith('php') | link.endswith('txt'):
                try:
                    page = get_data(link, rparser)
                    if page is None:
                        print(link + " This is disallowed path.\n")
                        continue
                except HTTPError:
                    print(link + " HTTPError\n")
                    continue
                except URLError:
                    print(link + " URLError\n")
                    continue
                if link.endswith('txt'):
                    pagestr = page
                    print("This is a text.")
                else:
                    titlestr, pagestr = page_perser(page)
                # gen doc ID
                doc = gen_fingerprint(pagestr)
                if doc in docID:
                    print("This is exact duplicate with " + doc + "\n")
                    continue
                # store into map(raw doc)
                docID.append(doc)
                docMap[doc] = [titlestr]
                docMap[doc].append(pagestr)
                docMap[doc].append(link)
                # filter valid word(words array)
                pagestr = valid_filter(pagestr.lower())
                if type(titlestr) is list:
                    titlestr = ' '.join(str(e) for e in titlestr)
                titlestr = valid_filter(titlestr.lower())
                # bag_words
                titlewords.append(' '.join(str(e) for e in titlestr))
                words.append(' '.join(str(e) for e in pagestr))
                # stemming
                stempagestr = stem_filter(pagestr)
                stemwords.append(' '.join(str(e) for e in stempagestr))

            elif link.endswith('gif') | link.endswith('jpg') | link.endswith('jpeg') | link.endswith('png'):
                img.append(link)
                history.append(link)
            else:
                file.append(link)
                print(link + " This is a file.\n")
                history.append(link)
        else:
            print(link + " Already crawled...\n")
            continue
        crawlnum += 1

    print("Images are:")
    print(img)

    print("Files are:")
    print(file)

    # original matrix
    # print("\nOriginal TF Matrix--------------")
    # analyze_str(words)
    # stemmed matrix
    # print("\nStemmed TF Matrix--------------")
    # analyze_str(stemwords)

    # print(len(docMap))
    print('Finished Crawler......')
    return docMap

