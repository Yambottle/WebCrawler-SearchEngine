#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*-
# @Time    : 5/3/18 14:49
# @Author  : Yam
# @Site    : 
# @File    : searchEngine.py
# @Software: PyCharm

import mainCrawler
import pandas as pd
import enchant

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import cosine_similarity


def init_engine():
    # run crawler to get docs
    docMap = mainCrawler.run_crawler()
    # print(len(docMap))
    df = get_matrix(mainCrawler.words)
    tdf = get_matrix(mainCrawler.titlewords)

    mappingMap = {}
    idx = 0
    for i in docMap.keys():
        mappingMap[idx] = i
        idx += 1

    print('Init Engine......')
    clsMap = clustering(df, 5)
    cluster_analysis(df, clsMap)
    print('Finished Init Engine......')
    print()
    return docMap, df, tdf, mappingMap, clsMap


def get_matrix(words):
    with open('dict.txt') as f:
        vocab = f.read().split('\n')
    # get normalized term freq matrix
    #tfidf_vect = TfidfVectorizer(stop_words=mainCrawler.stopwords, vocabulary=vocab) # stopwords and dict can put here
    tfidf_vect = TfidfVectorizer()
    tfidf_mat = tfidf_vect.fit_transform(words)
    df = pd.DataFrame(data=tfidf_mat.toarray(), columns=tfidf_vect.get_feature_names())
    # print(df.head())
    return df


def clustering(df, leadnum):
    clsMap = {}
    leaders = []

    # pick leader
    for i in range(0, leadnum):
        leader = df.sample(n=1, replace=False)
        while leader.index[0] in clsMap.keys():
            leader = df.sample(n=1, replace=False)
        leaders.append(leader.iloc[:, 0:-1])
        clsMap[leader.index[0]] = []

    # assign followers
    for i in range(0, len(df)):
        doc = df.iloc[i, 0:-1]
        mindist = 1000
        templeader = None
        for leader in leaders:
            if doc.index[0] == leader.index[0]:
                continue
            if euclidean_distances(leader.values, [doc.values])[0][0] < mindist:
                mindist = euclidean_distances(leader.values, [doc.values])[0][0]
                templeader = leader
        clsMap[templeader.index[0]].append(i)

    print('Cluster Map:')
    print(clsMap)

    return clsMap


def cluster_analysis(df, clsMap):
    print('Cluster Analysis:')
    for k, v in clsMap.items():
        print('Cluster:', k)
        if len(v) == 1:
            print('Lone leader! T-T')
            continue
        for i in v:
            if i == k:
                continue
            print(i, '-', k, ':', cosine_similarity([df.iloc[i, 0:-1], df.iloc[k, 0:-1]])[0][1])
    return


def check_in_dict(qlist):
    print('Word in Englist Checking: ')
    d = enchant.Dict("en_US")
    for word in qlist:
        if not d.check(word):
            # qlist.remove(word)
            print(word, ' is not an Englist word.')
    return qlist


def check_stopwords(qlist):
    print('Stopwords Checking: ')
    for word in qlist:
        if word in mainCrawler.stopwords:
            print(word, 'is a stop word.')
    return qlist


def init_thesaurus():
    thsMap = {}
    thsMap['beautiful'] = ['nice', 'fancy']
    thsMap['chapter'] = ['chpt']
    thsMap['responsible'] = ['owner', 'accountable']
    thsMap['freemanmoore'] = ['freeman', 'moore']
    thsMap['dept'] = ['department']
    thsMap['brown'] = ['beige','tan','auburn']
    thsMap['tues'] = ['Tuesday']
    thsMap['sole'] = ['owner','single','shoe','boot']
    thsMap['homework'] = ['hmwk','home','work']
    thsMap['novel'] = ['book','unique']
    thsMap['computer'] = ['cse']
    thsMap['story'] = ['novel','book']
    thsMap['hocuspocus'] = ['magic','abracadabra']
    thsMap['thisworks'] = ['this','work']
    return thsMap


    return thsMap


def search(qlist, mappingMap, docMap, time):
    print('Query is: ', ' '.join(str(e) for e in qlist))
    mainCrawler.words.append(' '.join(str(e) for e in qlist))
    mainCrawler.titlewords.append(' '.join(str(e) for e in qlist))
    df = get_matrix(mainCrawler.words)
    tdf = get_matrix(mainCrawler.titlewords)
    df_docq = df.iloc[len(df)-1, 0:-1]
    df_titq = tdf.iloc[len(tdf) - 1, 0:-1]

    scoreMap = {}
    for i in range(0, len(df)-time):
        doc = df.iloc[i, 0:-1]
        title = tdf.iloc[i, 0:-1]
        scoreMap[i] = cosine_similarity([df_docq, doc])[0][1]

        if cosine_similarity([df_titq, title])[0][1] != 0:
            scoreMap[i] += 0.25

    sortMap = {}
    for k in sorted(scoreMap, key=scoreMap.get, reverse=True):
        sortMap[k] = scoreMap[k]

    resultnum = 0
    print('')
    print('Search result:')
    print(sortMap, '\n')
    for key in sortMap.keys():
        if resultnum == 6:
            break
        if sortMap[key] == 0:
            print('Not enough results.\n')
            break
        docID = mappingMap.get(key)
        page = docMap.get(docID)
        if not page[0]:
            print('Title: None')
        else:
            print('Title:', page[0])
        print('Brief:', ' '.join(str(e) for e in mainCrawler.valid_filter(page[1].lower())[0:20]))
        print('link:', page[2])
        print()
        resultnum += 1
    return resultnum


docMap, df, tdf, mappingMap, clsMap = init_engine()

query = input("Enter query:")  # and much more to moow stop
qlist = query.lower().split(' ')
qlist.remove('stop')

qlist = check_in_dict(qlist)
qlist = check_stopwords(qlist)
thsdict = init_thesaurus()
print(thsdict)
resultnum = search(qlist, mappingMap, docMap, 1)
newqlist = []
if resultnum < 3:
    for word in qlist:
        if word in thsdict.keys():
            newqlist.append(thsdict[word])
    newqlist.append(qlist)
    print("Query Expansion Search:")
    search(newqlist, mappingMap, docMap, 2)











