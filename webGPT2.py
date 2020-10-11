import re
import time
import json
import argparse
import linecache
import random
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from random import sample
from random import randint
import nltk
import nltk.data
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import operator
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import argparse
import req
import spacy
from nltk.corpus import wordnet as wn


parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str)
parser.add_argument('--file_name', type=str)
parser.add_argument('--trigger', type=str)
parser.add_argument('--analyze', type=str)
parser.add_argument('--sample_size', type=int)
parser.add_argument('--flip_size', type=float)


args = parser.parse_args()
model = args.model
file_name = args.file_name
trigger = args.trigger
sample_size = args.sample_size
flip_cent = args.flip_size

#initialization
human_data = []
machine_data = []


nltk.download('wordnet')
ner = en_core_web_sm.load()
lemma = WordNetLemmatizer()
nlp = en_core_web_sm.load()

vocabulary = {}
vocab2tag = {}
ct = 0
with open(file_name) as json_file:
    while True:
        line = json_file.readline()
        if len(line)!=0:
            doc = ner(json.loads(line).get('article'))
            for each in doc.ents:
                if each.label_ not in vocabulary.keys():
                    vocabulary[each.label_] = set([each.text])
                else:
                    vocabulary[each.label_].add(each.text)

                if each.text not in vocab2tag.keys():
                    vocab2tag[each.text] = each.label_
        else:
            break

#print(vocabulary)
vocabulary_machine = {}
vocab2tag_machine = {}
ner = en_core_web_sm.load()
ct = 0
if trigger == 'entity_shuffle':
    with open('processed_machine.json') as json_file:
        while True:
            line = json_file.readline()
       	    if len(line) != 0:
                ct +=1
                doc = ner(json.loads(line).get('article'))
                for each in doc.ents:
                    if (each.label_ not in vocabulary_machine.keys()) and (each.text not in vocab2tag.keys()):
                        vocabulary_machine[each.label_] = set([each.text])
                    elif each.label_ not in vocabulary_machine.keys():
                        vocabulary_machine[each.label_] = set([each.text])
                    else:
                        vocabulary_machine[each.label_].add(each.text)

                    if (each.text not in vocab2tag_machine.keys()) and (each.text not in vocab2tag.keys()):
                        vocab2tag_machine[each.text] = each.label_
            else:
                break
    print(vocabulary_machine)

def entity_shuffle_old(text):
    altered_text = text
    length = text.split()
    alt = False
    count = 0

    entity_significance = dict()
    for idx, w in enumerate(length):
        if (w in vocab2tag.keys()) and (len(vocabulary[vocab2tag[w]]) > 1):
            entity_significance[w] = length.count(w)

    sorted_order = {k: v for k, v in sorted(entity_significance.items(), key=lambda item: item[1], reverse=True)}
    for word in sorted_order.keys():
        temp = sample(vocabulary[vocab2tag[word]],1)[0]
        print(temp, word)
        while temp == word:
            temp = sample(vocabulary[vocab2tag[word]],1)[0]
        alt = True
        count += length.count(word)
        altered_text = altered_text.replace(word, temp)
        if count > int(flip_cent*len(sorted_order)):
            break

    if alt:
        print(altered_text)
        return altered_text
    else:
        return ''
    #return text

def entity_shuffle(text):
    altered_text = text
    length = text.split()
    alt = False
    count = 0

    entity_significance = dict()
    for idx, w in enumerate(length):
        if (w in vocab2tag.keys()) and (len(vocabulary[vocab2tag[w]]) > 1):
            entity_significance[w] = length.count(w)

    sorted_order = {k: v for k, v in sorted(entity_significance.items(), key=lambda item: item[1], reverse=True)}
    for word in sorted_order.keys():
        temp = sample(vocabulary_machine[vocab2tag[word]],1)[0]
        while temp == word:
            temp = sample(vocabulary_machine[vocab2tag[word]],1)[0]
        alt = True
        count += length.count(word)
        print(count)
        altered_text = altered_text.replace(word, temp)
        if count > int(flip_cent*len(sorted_order)):
            break

    if alt:
        #print(altered_text)
        return altered_text
    else:
        return ''

#Trigger 2 - Sentences random shuffling
#Part a) within the article - 20% removal, 20% shuffle
#Part b) shuffle 2 random articles - 20% of lines

def sentence_shuffle(news, shuffler):
    count = 0
    length = len(news)
    while(count <= int((flip_cent)*length)):
        val = randint(0,len(news)-1)
        del news[val]
        count +=1

    count = 0
    while count <= int((flip_cent)*length):
        val1 = randint(0,len(news)-1)
        val2 = randint(0,len(news)-1)
        temp = news[val1]
        news[val1] = news[val2]
        news[val2] = temp
        count +=1

    count = 0
    while count <= int((flip_cent)*len(news)-1):
        val1 = randint(0, len(news) - 1)
        val2 = randint(0, len(shuffler) - 1)
        news[val1] = shuffler[val2]
        count +=1

    print('.'.join(news))
    return '.'.join(news)


def subjectObject_excahnge(tt):
    wordMap = ['neither', 'nor', 'either', 'or', 'and', 'together']
    new_news = []
    map1 = ['PERSON', 'NORP', 'ORG', 'PRODUCT']
    map3 = ['FAC', 'GPE', 'LOC']
    map5 = ['PRODUCT', 'EVENT', 'WORK_OF_ART']
    entity_labels = ['PERSON', 'NORP', 'ORG', 'LOC', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART']
    news = tt.split('.')
    count = 0
    for y, line in enumerate(news):
        flag = False
        words = line.split()
        for l in words:
            if l in wordMap:
                flag = True
                break
        if not flag:
            temp = ner(line)
            word1 = ""
            tag1 = ""
            for w in temp.ents:
                if (w.text in vocab2tag.keys()) and (vocab2tag[w.text] in entity_labels):
                    if word1:
                        print(w, word1)
                        word2 = vocab2tag[w.text]
                        if (tag1 == word2) or ((tag1 in map1) and (word2 in map1)) or ((tag1 in map3) or (word2 in map3)) or ((tag1 in map5) or (word2 in map5)):
                            if (word1 not in word2) or (word2 not in word1):
                                temp1 = line.replace(w.text, word1)
                                line = temp1.replace(word1, w.text, 1)
                                word1 = ""
                                count +=1
                                if count > int(flip_cent * len(news)):
                                    for x in range(y + 1, len(news)):
                                        new_news.append(news[x])
                                    return '.'.join(new_news)
                                break
                            #break
                    else:
                        word1 = w.text
                        tag1 = vocab2tag[w.text]

        new_news.append(line)
        #print(' '.join(line))
    if count < int((flip_cent*len(news))) or (tt == ('.'.join(new_news))):
        return ''
    return '.'.join(new_news)


def varyingSentiment(news_raw, pos, neg):
    news = news_raw.split('.')
    new_news = []
    ct = 0
    for y, line in enumerate(news):
        w = line.split()
        #temp = ner(line)
        new_line = ''
        for idx, l in enumerate(w):
            syn = list()
            ant = list()
            voidList = ['be', 'was', 'is', 'has', 'had','have','were', 'are', 'to', 'on']
            if l in voidList:
                continue
            for synset in wordnet.synsets(l):
                for lemma in synset.lemmas():
                    syn.append(lemma.name())  # add the synonyms
                    if lemma.antonyms():  # When antonyms are available, add them into the list
                        ant.append(lemma.antonyms()[0].name())
            if len(ant) > 0:
                #w[idx] = random.sample(ant, 1)[0]
                #w[idx] = ant[0]
                new_line = line.replace(l, ant[0])
                print(syn[0],ant[0], ct)
                new_news.append(new_line)
                ct +=1
                if ct > int(flip_cent*len(news)):
                    for x in range(y+1, len(news)):
                        new_news.append(news[x])
                    return '.'.join(new_news)
                break
            else:
                new_news.append(line)
                break
            '''
            if token.pos_ == 'ADJ' or token.pos_ == 'ADV' or token.pos_ == 'VERB' or token.pos_ == 'NOUN':
                print(token.text)
                if token.text.lower() in pos:
                    line = line.replace(token.text, neg[randint(0,len(neg)-1)])
                    ct +=1
                elif token.text.lower() in neg:
                    line = line.replace(token.text, pos[randint(0, len(pos)-1)])
                    ct+=1
                    '''
            #print(new_news)
            #print("---------------------")
        
    if (ct < int(0.8 * int(flip_cent * len(news)))) or (news_raw == ('.'.join(new_news))):
        return ''

    #print(news_raw)
    print("SENTIMENT TWEAKED!!!!!!!!!!!!!!!!!!!!!!!")
    print('.'.join(new_news))
    return '.'.join(new_news)+'.'
        #print(token.text, token.tag_, token.pos_)

def varyingSentiment_old(news_raw, pos, neg):
    news = news_raw.split('.')
    new_news = []
    for y, line in enumerate(news):
        ct = 0
        w = line.split()
        #temp = ner(line)
        for idx, l in enumerate(w):
            syn = list()
            ant = list()
            for synset in wordnet.synsets(l):
                for lemma in synset.lemmas():
                    syn.append(lemma.name())  # add the synonyms
                    if lemma.antonyms():  # When antonyms are available, add them into the list
                        ant.append(lemma.antonyms()[0].name())
            if len(ant) > 0:
                #w[idx] = random.sample(ant, 1)[0]
                w[idx] = ant[0]
                ct +=1
                break
            '''
            if token.pos_ == 'ADJ' or token.pos_ == 'ADV' or token.pos_ == 'VERB' or token.pos_ == 'NOUN':
                print(token.text)
                if token.text.lower() in pos:
                    line = line.replace(token.text, neg[randint(0,len(neg)-1)])
                    ct +=1
                elif token.text.lower() in neg:
                    line = line.replace(token.text, pos[randint(0, len(pos)-1)])
                    ct+=1
                    '''

        new_news.append(' '.join(w))
        if ct > int(flip_cent*len(news)):
            for x in range(y+1, len(news)):
                new_news.append(news[x])
            break
    if ct < int(0.8 * int(flip_cent * len(news))):
        return ''


    print("SENTIMENT TWEAKED!!!!!!!!!!!!!!!!!!!!!!!")
    print('.'.join(new_news))
    return '.'.join(new_news)
        #print(token.text, token.tag_, token.pos_)

if model == 'all':
    driver_gpt2 = webdriver.Firefox()
    driver_grover = webdriver.Firefox()
else:
    driver = webdriver.Firefox()
#trigger 2
nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#sentence_shuffle(tokenizer.tokenize(text))

print("Trigger 3!!!!!!!!!!!!!!!!!!!!!!!!")
#trigger 3
#Subject-Object exchange - no exchange on words like either, or, neither, nor, and, together
#subjectObject_excahnge(tokenizer.tokenize(text))

#trigger 4
pos_sent = []
neg_sent = []
print("trigger 4")
with open('./sentiWordNet/positive-words.txt', 'r') as pos:
    lines = pos.readlines()
    for l in lines:
        pos_sent.append(l.split('\n')[0])
pos.close()
with open('./sentiWordNet/negative-words.txt', 'r') as pos:
    lines = pos.readlines()
    for l in lines:
        neg_sent.append(l.split('\n')[0])
pos.close()
#varyingSentiment(tokenizer.tokenize(text), pos_sent, neg_sent)

#trigger 5 - grammatical perturbations
def removePunctuations(news):
    news_token = ner(news)
    new_news = []
    flag = False
    for token in news_token:
        # print(token.text, token.pos_, token.tag_)
        if ((token.text == "\'s") or (token.text == "’s")) and (token.tag_ == 'VBZ'):
            t = new_news.pop()
            new_news.append(t + " is")
        elif (token.tag_ == '.') or (token.tag_ == ',') or (
                (token.text == "'s") or (token.text == "’s") and (token.tag_ == 'POS')):
            new_news[-1] += token.text
        else:
            new_news.append(token.text)

    #print(' '.join(new_news))
    return ' '.join(new_news)


def removeBOWArticles(news, flip_size):
    news_token = ner(news)
    flag = False
    new_news = []
    temp = dict()
    split_news = news.split()

    for n in news_token:
        if n.text in temp.keys():
            temp[n.text] = temp.get(n.text) + 1
        else:
            temp[n.text] = 1

    sorted_vocab = sorted(temp.items(),
                          key=operator.itemgetter(1),
                          reverse=True)

    bow = [x for x in sorted_vocab[:20]]
    bow_punct = dict(bow)
    if flip_size == 1.0:
        for token in news_token:
            if token.text in bow_punct.keys() and (not token.text == '.'):
                if ((token.tag_ == 'DT') or (token.pos_ == 'PUNCT' and token.text == ',')):
                    continue
                elif (token.text == 'and') and (len(new_news)>0):
                    new_news[-1] += '.'
                    flag = True
                else:
                    if flag:
                        new_news.append(token.text.capitalize())
                        flag = False
                    else:
                        new_news.append(token.text)
            elif ((token.pos_ == 'PUNCT') or ((token.text == "\'s") or (token.text == "’s"))) and (len(new_news)>0):
                new_news[-1] += token.text
            else:
                if flag:
                    new_news.append(token.text.capitalize())
                    flag = False
                else:
                    new_news.append(token.text)

        #print(new_news)
        return ' '.join(new_news)
    else:
        for key in bow_punct.keys():
            if key in ['the', 'a', 'an', 'and', ',']:
                bow_punct[key] = int(flip_size * bow_punct[key])
            else:
                bow_punct[key] = 0

        print(bow_punct)
        for key in bow_punct.keys():
            temp = []
            rem = []
            definiteArticlesMap = ['the', 'a', 'an']
            if not key == '.':
                for idx, token in enumerate(split_news):
                    if key == token:
                        # if ((token in definiteArticlesMap) or (',' in token) or (token == 'and')):
                        #print(token, idx, key)
                        temp.append(idx)
                    elif (key == ',') and (key in token):
                        #print(token, idx, key)
                        temp.append(idx)
                # print(temp)
                if temp:
                    m = 0 
                    for l in range(0, bow_punct[key]):
                        val = random.choice(temp)
                        while (val in rem) and (m<1000):
                            val = random.choice(temp)
                            m+=1
                        if val not in rem:
                            rem.append(val)

                    ct = 0 
                    for clr in rem:
                        if (key == 'and') and (clr > 0):
                            if (clr - ct + 1) < len(split_news):
                                t = split_news.pop(clr - ct - 1)
                                split_news.insert(clr - ct - 1, t + '.')
                                #print("Key:and " + t)
                                n = split_news.pop(clr - ct + 1)
                                #print("Key:and " + )
                                split_news.insert(clr - ct + 1, n.capitalize())
                                split_news.pop(clr-ct)
                                ct += 1
                        elif key == ',':
                            t = split_news.pop(clr - ct)
                            #print(t[:-1])
                            split_news.insert(clr - ct, t[:-1])
                            ct += 1
                        else:
                            #print(clr, ct)
                            #print(split_news.pop(clr - ct))
                            ct += 1

        return ' '.join(split_news)

def AlterNumbers(news, flip_cent):
    doc = ner(news)
    ct = 0
    total_sent = len(news.split('.'))
    for ent in doc.ents:
        if (ent.label_ == 'MONEY') or (ent.label_ == 'CARDINAL'):
            if ent.text.isnumeric():
                if ent.end_char-ent.start_char > 3:
                    news = news.replace(ent.text, str(random.randint(0,999)),1)
                else:
                    num = random.randint(1000, 100000)
                    news = news.replace(ent.text, str(num),1)
                ct+=1
                if ct > int(flip_cent * total_sent):
                    break
            else:
                #write for Money and words
                numberWords = ['ten', 'hundred', 'thousand', 'million', 'billion', 'trillion']
                temp = ent.text.split()
                setFlag = False
                for i in temp:
                    if ct > int(flip_cent * total_sent):
                        break
                    if i.isnumeric():
                        if ent.end_char-ent.start_char > 3:
                            num = random.randint(1, 999)
                            news = news.replace(i, str(num),1)
                            ct+=1
                        else:
                            num = random.randint(1000, 100000)
                            news = news.replace(i, str(num),1)
                            ct+=1
                    else:
                        if re.search(r'\d', i):
                            print(i)
                            x = ''
                            ct = 0
                            for j in i:
                                if ct > int(flip_cent * total_sent):
                                    break
                                if j.isdigit():
                                    x =  x+str(random.randint(1,9))
                                    ct +=1
                                else:
                                    x = x+j
                            if ct > 3:
                                x = x+str(random.randint(1,999))
                            else:
                                x = x[0:2]
                            news = news.replace(i, x,1)
                            ct+=1
                            setFlag = True
                        elif i in numberWords:
                            news = news.replace(i, str(random.sample(numberWords,1)[0]+'s'),1)
                            ct+=1
                            setFlag = True
                            if ct > int(flip_cent * total_sent):
                                break
                    if setFlag:
                        break 
                       
        if ct > int(flip_cent * total_sent):
            break
    print(news)
    print("--------------------------------------")
    return news

def add_the(text, n):
    doc = nlp(text)
    ent_list = []
    sent_list = []
    for ent in doc.ents:
        #print(ent.text, ent.label_)
        if ent.label_ != "MONEY" or ent.label_ != "TIME" or ent.label!="QUANTITY":
            ent_list.append(ent.text+",")

    for ent in doc.sents:
        sent_list.append(ent.text)

    flip = int(n*len(ent_list))-1
    #print(flip, len(ent_list))
    if (len(ent_list) > flip) and (flip > 0):
        smple = random.sample(ent_list, flip)
    else:
        return ''
    text_l = []
    for i in doc:
        text_l.append(i.text)

    #smple.sort()
    #print(smple)
    for num in smple:
        for i,s in enumerate(sent_list):
            if num in s:
                idx = None
                temp = s.split()
                if not temp:
                    break
                if num.split()[0] in temp:
                    idx = temp.index(num.split()[0])
                else:
                    if num.split()[0] in text_l:
                        j = text_l.index(num.split()[0])
                        str_j = text_l[j]+text_l[j+1]
                        if str_j in temp:
                            idx = temp.index(str_j)
                if idx is None:
                    continue
                elif idx == 0:
                    temp.insert(0, "The")
                elif idx < len(temp) and temp[idx-1].lower() != "the":
                    temp.insert(idx, "the")
                sent_list[i] = ' '.join(temp)
    
    return ' '.join(sent_list)

def humanize(text1, n):
    idx = []
    mapVerb = ['are', 'is', 'has', 'have', 'did', 'can', 'would', 'could', 'may', 'shall'] 
    mapPro = ['that', 'he', 'she', 'it', 'It','where', 'which', 'we']
    #print("Replacing full forms with style!!!!!!!!!!!!!!!!!!!!!!", text1, n)
    #doc = nlp(text1)
    for i, t in enumerate(doc):
        if ((t.text == "is" and t.pos_ == 'VERB') and ((doc[i-1].pos_ == 'ADJ') or (doc[i-1].pos_=='PRON') or (doc[i-1].text.lower() in mapPro))) or ((t.text == "not" and t.pos_ == 'ADV') and ((doc[i-1].pos_ == 'VERB') or (doc[i-1].text in mapVerb))):
            idx.append(i)
    changed = []
    num= []
    flip = int(len(idx))-1
    if len(idx) < 2:
        return text1 
    smple = random.sample(range(0, len(idx)-1), flip)
    #print(smple)
    for t in smple:
        if idx[t] not in num:
            num.append(idx[t])
    num.sort()
    for i, t in enumerate(doc):
        if i in num:
            l = changed.pop()
            if "’" not in l:
                if doc[i].text == 'is':
                    l +="’s"
                elif doc[i].text == 'not':
                    l +="n’t"
            else:
                l = l + " " + t.text
            changed.append(l)
        elif t.pos_ == "PUNCT" or t.text =="’s":
            l = changed.pop()
            l+=t.text
            changed.append(l)
        else:
            changed.append(t.text)
    print(' '.join(changed))
    print("Huamnizing done!!!!!!!!!!!!!!________________________")
    return ' '.join(changed)


def join_sent(text2, n):
    doc = nlp(text2)
    text_list = []
    ent_list = []
    for sent in doc.sents:
        text_list.append(sent.text)

    for ent in doc.ents:
        if ent.text not in ent_list:
            ent_list.append(ent.text)

    flip = int(n * len(text_list)) - 2
    smple = random.sample(range(0, len(text_list) - 2), flip)
    smple.sort()
    print("Joining the sentences")
    for t in range(len(text_list) - 1):
        f= 0
        if t in smple:
            # print(text_list[t])
            break_word = text_list[t].split()
            if f==0:
                word = break_word[-1][:-1] + " and"
                f = 1
            else:
                word = break_word[-1][:-1] + ","
                f = 0
            break_word.pop()
            break_word.append(word)
            text_list[t] = ' '.join(break_word)
            next_sent = text_list[t + 1].split()
            temp = next_sent[0]
            if temp not in ent_list:
                next_sent[0] = temp.lower()
                text_list[t + 1] = ' '.join(next_sent)
    return ' '.join(text_list)


def detectGrover(news, driver, count, fooled):
    #for news in check_now:
    driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").clear()
    driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").send_keys(news)
    ans = driver.find_element_by_css_selector("button.ant-btn.sc-bdVaJa.sc-jbKcbu.iUrOzv").submit()
    result = dict()
#ant-btn sc-bdVaJa sc-jbKcbu iUrOzv
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dfVpRl.eIhhqn")))
        if element:
            result['id'] = count
            result['article'] = news
            if 'human' in element.text:
                result['label'] = 'human'
            else:
                result['label'] = 'machine'

            #store_result.append(result)
    except:
        ans = driver.find_element_by_css_selector("button.ant-btn.sc-bdVaJa.sc-jbKcbu.iUrOzv").submit()
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dfVpRl.eIhhqn")))
            if element:
                result['id'] = count
                result['article'] = news
                if 'human' in element.text:
                    result['label'] = 'human'
                    fooled +=1
                elif 'machine' in element.text:
                    result['label'] = 'machine'

                #store_result.append(result)
        except:
            print("Unresponsive!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #print(store_result)
    return result, fooled

def detectGPT2(news, driver, label, right):
    result = dict()
    driver.find_element_by_id("textbox").clear()
    driver.find_element_by_id("textbox").send_keys(news)
    temp = driver.find_element_by_id("real-percentage")
    time.sleep(5)
    temp = driver.find_element_by_id("real-percentage").text.split('%')
    time.sleep(10)
    try:
        if not temp[0]:
            time.sleep(30)
            temp = driver.find_element_by_id("real-percentage").text.split('%')
        if temp[0]:
            if float(temp[0]) > 50:
                result['label'] = 'human'
            else:
                result['label'] = 'machine'
        if result['label'] == 'human':
            right += 1
    except:
        print("Unresponsive.....................................")
    result['article'] = news
        #store_data.append(result)
    #driver.close()
    return result, right

def detectFakeBox(news, label, right):
    maxtry = 10
    res = 0
    label = ""
    result = dict()
    try:
        while maxtry > 0:
            res = req.sendRequest(news)
            maxtry = maxtry - 1
    except:
        print("Internet Error!Sleep 3 sec！", res, maxtry)
        time.sleep(3)
    print("******************************************")
    print(res['content_score'])
    if res:
        if res["content_decision"] == 'impartial' or ((res['content_score'] > 0.5)):
            result['label'] = 'human'
            right +=1
        else:
            result['label'] = 'machine'

    result['article'] = news
    print(right)
    print("-----------------------------------------------------")
    return result, right

#model load
if model == 'all':
    driver_grover.get("https://grover.allenai.org/detect")
    driver_gpt2.get("https://huggingface.co/openai-detector")
elif model == 'groverAI':
    driver_grover.get("https://grover.allenai.org/detect")
    #detectGrover(human_data, driver)
elif model == 'gpt2':
    driver_gpt2.get("https://huggingface.co/openai-detector")
    #detectGPT2(human_data, driver)
elif model == 'fakebox':
    req.init()
else:
    print("Not supported as yet! TODO:CTRL, FakeBox")

random.seed(99)
'''
if trigger == 'sentence_shuffle':
    random.seed(57)
elif trigger == 'entity_shuffle':
    random.seed(41)
elif trigger == 'so_exchange':
    random.seed(21)
elif trigger == 'sentiment':
    random.seed(56)
elif trigger == 'alter_numbers':
    random.seed(29)
elif trigger == 'syntactic_MH':
    random.seed(21)
'''
count = 0
store_result_gpt2 = []
store_result_grover = []
store_result = []
lines = []
fool = 0
ct = 0
m = 0
with open(file_name) as json_file:
    while m < 2000:
        line = json_file.readline()
        if len(line)!=0:
            lines.append(line)
            m +=1
        else:
            break
    ranselect = random.sample(lines, sample_size)
    print(ranselect[0])

machine = []
if trigger == 'sentence_shuffle' or trigger == 'syntactic_MH':
    with open('processed_machine.json') as json_file:
        while True:
            line = json_file.readline()
            if len(line)!=0:
                machine.append(line)
            else:
                break
'''
if trigger == 'syntactic_MH':
    ranselect = random.sample(machine, sample_size)
'''
for i in ranselect:
    copy = json.loads(i)
    if (trigger == 'entity_shuffle'):
        print(copy.get('article'))
        temp = entity_shuffle(copy.get('article'))
        #print(temp)
        if ((model == 'groverAI') or (model == 'all')) and temp:
            res, fool = detectGrover(temp, driver_grover, count, fool)
            store_result_grover.append(res)
            #json_file.write(str(json.dumps(res)) + '\n')
            count +=1
        if (model == 'gpt2') or (model == 'all') and temp:
            test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
            if label == 1:
                res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                store_result_gpt2.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
                print(fool)
            else:
                c = random.sample(lines, 1)
                ranselect.append(c[0])
            count += 1
        if (model == 'fakebox'): #or (model == 'all') and temp:
            test, label = detectFakeBox(copy.get('article'), count, 0)
            if label == 1:
                res, fool = detectFakeBox(temp, count, fool)
                store_result.append(res)
                print(fool)
                #json_file.write(str(json.dumps(res)) + '\n')
            else:
                c = random.sample(lines, 1)
                ranselect.append(c[0])
            count += 1
    elif trigger == 'sentence_shuffle':
        ranNext = random.sample(machine, 1)
        shuffler = (json.loads(ranNext[0])).get('article')
        temp = sentence_shuffle((copy.get('article')).split('.'), shuffler.split('.'))
        if (model == 'groverAI') or (model == 'all'):
            print(fool)
            res, fool = detectGrover(temp, driver_grover, count, fool)
            store_result_grover.append(res)
            #json_file.write(str(json.dumps(res)) + '\n')
            count +=1
        if (model == 'gpt2') or (model == 'all'):
            test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
            if label == 1:
                res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                print(fool)
                store_result_gpt2.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
            else:
                c = random.sample(lines, 1)
                ranselect.append(c[0])
            count += 1
        if (model == 'fakebox'): # or (model == 'all')) and temp:
            test, label = detectFakeBox(copy.get('article'), count, 0)
            if label == 1:
                res, fool = detectFakeBox(temp, count, fool)
                store_result.append(res)
                print(fool)
                #json_file.write(str(json.dumps(res)) + '\n')
            else:
                c = random.sample(lines, 1)
                ranselect.append(c[0])
            count += 1
    if trigger == 'so_exchange':
        print(copy.get('article'))
        temp = subjectObject_excahnge(copy.get('article'))
        if temp is None or (temp == ''):
            c = random.sample(lines, 1)
            ranselect.append(c[0])
        #print(temp)
        else:
            if(model=='groverAI') or (model == 'all'):
                res, fool = detectGrover(temp, driver_grover, count, fool)
                store_result_grover.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
            if  (model == 'gpt2') or (model == 'all'):
                res, label = detectGPT2(temp, driver_gpt2, count, 0)
                if label == 1:
                    res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                    print(fool)
                    store_result_gpt2.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
            if (model == 'fakebox'): # or (model == 'all'):
                test, label = detectFakeBox(copy.get('article'), count, 0)
                if label == 1:
                    res, fool = detectFakeBox(temp, count, fool)
                    store_result.append(res)
                    print(fool)
                    #json_file.write(str(json.dumps(res)) + '\n')
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
    if trigger == 'sentiment':
        print(copy.get('article'))
        temp = varyingSentiment(copy.get('article'), pos_sent, neg_sent)
        #print(temp)
        if temp is None or (temp == ''):
            c = random.sample(lines, 1)
            ranselect.append(c[0])
        else:
            if (model == 'groverAI') or (model == 'all'):
                res, fool = detectGrover(temp, driver_grover, count, fool)
                store_result_grover.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
            if (model == 'gpt2') or (model == 'all'):
                test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
                if label == 1:
                    res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                    print(fool)
                    store_result_gpt2.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
            if (model == 'fakebox'): # or (model == 'all'):
                test, label = detectFakeBox(copy.get('article'), count, 0)
                if label == 1:
                    res, fool = detectFakeBox(temp, count, fool)
                    store_result.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                    print(fool)
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
    if trigger == 'alter_numbers':
        temp = AlterNumbers(copy.get('article'), flip_cent)
        if ct < 400 :
            ct += 1
        if ('Endgame' in temp) or ('NHL' in temp):
            ct +=1
        else:
            if temp is None or (temp == ''):
                c = random.sample(lines, 1)
                ranselect.append(c[0])
            else:
                if (model == 'groverAI') or (model == 'all'):
                    res, fool = detectGrover(temp, driver_grover, count, fool)
                    store_result_grover.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                if (model == 'gpt2') or (model == 'all'):
                    test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
                    if label == 1:
                        res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                        print(fool)
                        store_result_gpt2.append(res)
                        #json_file.write(str(json.dumps(res)) + '\n')
                    else:
                        c = random.sample(lines, 1)
                        ranselect.append(c[0])
                if (model == 'fakebox'): # or (model == 'all'):
                    test, label = detectFakeBox(copy.get('article'), count, 0)
                    if label == 1:
                        res, fool = detectFakeBox(temp, count, fool)
                        store_result.append(res)
                        #json_file.write(str(json.dumps(res)) + '\n')
                        print(fool)
                    else:
                        c = random.sample(lines, 1)
                        ranselect.append(c[0])
    if trigger == 'syntactic_MH':
        print(copy.get('article'))
        temp_p = removePunctuations(copy.get('article'))
        if temp_p:
            temp = removeBOWArticles(temp_p, flip_cent)
        print(temp)
        print("****************************************************************************") 
        if (temp is None) or (temp == ''):
            c = random.sample(lines, 1)
            ranselect.append(c[0])
        else:
            if (model == 'groverAI') or (model == 'all'):
                res, fool = detectGrover(temp, driver_grover, count, fool)
                store_result_grover.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
            if (model == 'gpt2') or (model == 'all'):
                test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
                print("Test label:", label)
                if label == 0:
                    res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                    print(model + " " + str(fool))
                    store_result_gpt2.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
            if (model == 'fakebox'): # or (model == 'all'):
                test, label = detectFakeBox(copy.get('article'), count, 0)
                if label == 0:
                    res, fool = detectFakeBox(temp, count, fool)
                    #json_file.write(str(json.dumps(res)) + '\n')
                    store_result.append(res)
                    print(fool)
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
    if trigger == 'syntactic_HM':
        #print(copy.get('article'))
        temp = None 
        temp_2 = None 
        temp_p = add_the(copy.get('article'), flip_cent)
        if temp_p:
            temp_2 = humanize(temp_p, flip_cent)
            if temp_2 == -1:
               c = random.sample(lines, 1)
               ranselect.append(c[0])
               continue
        if temp_2:
            temp = join_sent(temp_2, flip_cent)
        #print(temp)
        if temp is None or (temp == ''):
            c = random.sample(lines, 1)
            ranselect.append(c[0])
        else:
            if (model == 'groverAI') or (model == 'all'):
                res, fool = detectGrover(temp, driver_grover, count, fool)
                store_result_grover.append(res)
                #json_file.write(str(json.dumps(res)) + '\n')
            if (model == 'gpt2') or (model == 'all'):
                test, label = detectGPT2(copy.get('article'), driver_gpt2, count, 0)
                if label == 1:
                    res, fool = detectGPT2(temp, driver_gpt2, count, fool)
                    print(model+" " +  str(fool))
                    store_result_gpt2.append(res)
                    #json_file.write(str(json.dumps(res)) + '\n')
                    print("----------------------------------------------------------")
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])
            if (model == 'fakebox'): # or (model == 'all'):
                test, label = detectFakeBox(copy.get('article'), count, 0)
                if label == 1:
                    res, fool = detectFakeBox(temp, count, fool)
                    #json_file.write(str(json.dumps(res)) + '\n')
                    store_result.append(res)
                    print(fool)
                else:
                    c = random.sample(lines, 1)
                    ranselect.append(c[0])

#print(vocab2tag)
if args.analyze:
    if model == 'groverAI':
        with open(str(trigger+'_'+model+str(flip_cent)+'_results'), 'w') as json_file:
            for each in store_result_grover:
                json_file.write(str(json.dumps(each)) + '\n')
        driver.close()
        json_file.close()
    if model == 'gpt2':
        with open(str(trigger + '_' + model + str(flip_cent) + '_results'), 'w') as json_file:
            for each in store_result_gpt2:
                json_file.write(str(json.dumps(each)) + '\n')
        driver.close()
        json_file.close()
    if model == 'all':
        with open(str(trigger + '_groverAI' + model + str(flip_cent) + '_results'), 'w') as json_file:
            for each in store_result_grover:
                json_file.write(str(json.dumps(each)) + '\n')
        json_file.close()
        with open(str(trigger + '_gpt2' + model + str(flip_cent) + '_results'), 'w') as json_file:
            for each in store_result_gpt2:
                json_file.write(str(json.dumps(each)) + '\n')
        driver_grover.close()
        driver_gpt2.close()
        json_file.close()

#print("Miss rate:", str(fool/sample_size))

