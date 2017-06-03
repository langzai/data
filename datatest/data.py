# coding: utf-8

import os
import re
import time
import numpy
import copy
import math
import heapq


def filePathList(dirname):
    file_path_list = os.listdir(dirname)
    file_path_list = list( map( lambda path : os.path.join(dirname,path) ,file_path_list))
    return file_path_list
  

def fileRename(dirname):
    file_path_list = filePathList(dirname)
    i = 0
    for file_name in file_path_list :
        os.rename(file_name,os.path.join(dirname,str(i)))
        i = i+1


def wordSegment(words):
    words = re.split('[\s/]' , words)     #划分单词  数字中含有'.,' 不能用 '.,'分词
    words = map( lambda word : word.strip('., ;:?\'\"') , words)
    words = [ word.lower()  for word in words if len (word) >0 ]
    return list(words)


def getWordList(dirname):
    #用时454s
    #word_list = []
    #dir_list = filePathList(dirname)
    #for file_name in dir_list:
    #   with open(file_name) as file:
    #       words = file.read()
    #       words = wordSegment(words)
    #       for word in words :
    #           if word not in word_list :
    #               word_list.append(word)
    #return word_list
    
    #用时6.27s
    #word_list = set()
    #dir_list = filePathList(dirname)
    #for file_name in dir_list:
    #   with open(file_name) as file:
    #       words = file.read()
    #        words = wordSegment(words)
    #       word_list = word_list | set(words)
    #return word_list  
    word_list = {}
    dir_list = filePathList(dirname)
    i = 0
    for file_name in dir_list:
        with open(file_name) as file:
            words = file.read()
            words = wordSegment(words)
            for word in words:
                 if word not in word_list.keys():
                        word_list[word] = i
                        i= i + 1
    return word_list 


def getIndex(dirname):
    index = {}
    words_num = 0
    file_list = filePathList(dirname)
    for file_name in file_list:
        id_file = os.path.split(file_name)[-1]
        with open(file_name) as file:
            words = file.read()
            words = wordSegment(words)
            words_num = words_num + len(words)
            #print(words)
            for i in range(len(words)):
                if words[i] in index.keys() :
                    if id_file in index[words[i]].keys():
                        index[words[i]][id_file][0] = index[words[i]][id_file][0] + 1
                        index[words[i]][id_file].append(i)
                    else:
                        index[words[i]][id_file]=[1,i]    
                else :
                    index[words[i]] = {id_file : [1,i]}
    for word in index.keys():
        word_count =0
        for file_id in index[word].keys():
            word_count = word_count + index[word][file_id][0]
        index[word]['t'] = word_count  #保存每个单词出现的总次数
    index['word_count'] = len(index.keys())
    index['file_num'] = len(file_list) #保存总文档数
    index['words_num'] = words_num #保存总单词数        
    return index            


def getFrequencyVector(dirname):
    frequency_vector = {}
    dir_list = filePathList(dirname)
    for file_name in dir_list:
        id_file = os.path.split(file_name)[-1]
        with open(file_name) as file:
            words = file.read()
            words = wordSegment(words)
            for word in words:
                if id_file in frequency_vector.keys():
                    if word in frequency_vector[id_file].keys():
                        frequency_vector[id_file][word] = frequency_vector[id_file][word] + 1
                    else :
                        frequency_vector[id_file][word] = 1
                else:
                    frequency_vector[id_file] ={word:1}     
    return frequency_vector     


def getTf(frequency_vector):
    Tf = copy.deepcopy(frequency_vector)
    for id_file in Tf.keys():
        for word in Tf[id_file].keys():
            Tf[id_file][word] = 1 + math.log(Tf[id_file][word],2)
    return Tf


def getIDF(index):
    IDF = {}
    for word in index.keys():
        if word != 'word_count' and word !='file_num' and word != 'words_num':
            IDF[word] = math.log(index['file_num']/(len( index[word].keys() )-1),2)
    return IDF

def getWordWeight(Tf,IDF):
    word_weight = {}
    for id_file in Tf.keys():
        word_weight[id_file] = {}
    for id_file in Tf.keys():  
        sum_document_weights_squares = 0
        for word in Tf[id_file].keys():
            word_weight[id_file][word]= Tf[id_file][word] * IDF[word]
            sum_document_weights_squares = sum_document_weights_squares + (Tf[id_file][word] * IDF[word])**2
        word_weight[id_file]['sum_weights_squares'] = sum_document_weights_squares
    return word_weight


def getOptimalFileTwoWord(search_all_word,word_weight,index,num):
    if search_all_word[0] not in index.keys() and search_all_word[1] not in index.keys() :
        return None
    word_position = {}
    files = set()
    for search_word in search_all_word :
        #word_position[search_word] = index[search_word]
        word_position[search_word] = index.get(search_word)
        if search_word in index.keys():
            files = files | set(index.get(search_word).keys())
    #print('###',word_position,'###')
    files = files - set('t')
    article_relevance = {}
    for file in files :
        article_relevance[file] = 0
        for search_word in search_all_word :
            article_relevance[file] = article_relevance[file] + word_weight[file].get(search_word,0)
      
        if article_relevance[file] !=0 :
            article_relevance[file] = article_relevance[file]/math.sqrt(len(search_all_word) * word_weight[file]['sum_weights_squares'])
    article_relevance = list(article_relevance.items())
    OptimalFile = heapq.nlargest(len(article_relevance),article_relevance,key = lambda x :x[1])
    #OptimalFile = article_relevance.items()
    Optimal =[]
    for id_file , relevance in OptimalFile :
        Optimal.append([id_file , relevance])
    files = set()
    #for i in range(len(Optimal)) :
    if search_all_word[0] in index.keys() and search_all_word[1] in index.keys():
        files = set(index[search_all_word[0]].keys()) & set(index[search_all_word[1]].keys()) - set('t')

    for file in files :
        for m  in range(len(Optimal)) :
            if file == Optimal[m][0] :
                Optimal[m][1] = Optimal[m][1] +1
                break
        
    for file in files :
        for i in index[search_all_word[0]][file][1:] :
            isphrase = False
            for j in index[search_all_word[1]][file][1:] :
                if i - j == -1 :
                    for m  in range(len(Optimal)) :
                        if file == Optimal[m][0] :
                            Optimal[m][1] = Optimal[m][1] +1
                            Optimal[m].append(i)
                            isphrase = True
                            break
                    break
            if isphrase :
                break
    Optimal = heapq.nlargest(num,Optimal,key = lambda x :x[1])
    return Optimal
    

def getOptimalFileOneWord(search_word,word_weight,index,num):
    if search_word not in index.keys():
        return None
    word_position = index[search_word]
    #print('###',word_position)
    files = [file for file in index[search_word].keys() if file !='t']
    article_relevance = {}
    for file in files :
        if word_weight[file].get(search_word,0)!=0 :
            article_relevance[file] = word_weight[file].get(search_word,0)/math.sqrt(word_weight[file]['sum_weights_squares'])
        else :
            article_relevance[file] = 0           
    article_relevance = list(article_relevance.items())
    OptimalFile = heapq.nlargest(num,article_relevance,key = lambda x :x[1])
    Optimal = []
    for id_file , relevance in OptimalFile :
        Optimal.append([id_file , relevance])
    return Optimal

def getOneWordContent(Optimal , index ,search_word,dirname) :
    Optimal = copy.deepcopy(Optimal)
    if not Optimal :
        return None
    search_word = search_word.lower()
    #print("**************")
    #print(Optimal)
    for i  in  range (len(Optimal)) :
        if  Optimal[i][1] <2:
            Optimal[i].append(index[search_word][Optimal[i][0]])
    
    #print(Optimal)
    contents = []
    for i  in  range (len(Optimal)) :
        if  Optimal[i][1] >2:
            position = Optimal[i][2] 
        else:
            position = Optimal[i][2][1];
        if position <10 :
            start_position = 0
        else :
            start_position = position - 10
        f = open(os.path.join(dirname,str(Optimal[i][0])),'r')
        words = f.read()
        f.close()
        words = wordSegment(words)
        j = 0
        content = ''
        while start_position < len(words) and j <20 :
            content = content + words[start_position] + ' '
            start_position = start_position + 1
            j = j+1
        contents.append([Optimal[i][0],Optimal[i][1],content + '......'])
    return contents

def getTwoWordContent(Optimal , index ,search_all_word,dirname) :
    if not Optimal :
        return None
    contents = []
    for i in range(len(Optimal)) :
        if Optimal[i][1] > 2 :
            contents.append(getOneWordContent([Optimal[i] ], index ,search_all_word[0],dirname))
        elif Optimal[i][1] >1 :
            content = getOneWordContent([Optimal[i]] , index ,search_all_word[0],dirname)
            #print(Optimal[i][0])
            if search_all_word[1] not in content[0][2] :
                content[0][2] = content[0][2] + '...' + getOneWordContent([Optimal[i]] , index ,search_all_word[1],dirname)[0][2]
            contents.append(content)
        else :
            if search_all_word[0] in index.keys() and Optimal[i][0] in index[search_all_word[0]].keys() and search_all_word[0] !='word_count' and search_all_word[0] !='file_num'  and search_all_word[0] !='words_num':
                #try :
                    contents.append(getOneWordContent([Optimal[i]] , index ,search_all_word[0],dirname))
                #except :
                    #print(([Optimal[i]] , index ,search_all_word[0],dirname))
                    pass
            else :
                contents.append(getOneWordContent([Optimal[i]] , index ,search_all_word[1],dirname))
                #pass
    return contents
                




