import json
import spacy
import statistics
nlp = spacy.load("en_core_web_sm")
length = 0
length_h = 0
length_m = 0
length_mach = 0
length_hw = 0
length_mw = 0

ct = 0
total = 55555200
with open('processed_human.json') as f:
    while ct < total:
        line = f.readline()
        if len(line)!=0:
            art = json.loads(line) 
            array_list = art.get('article')
            array_article = nlp(array_list) 
            art_length =[] 
            count = 0
            for i in array_article.sents:
                j = i.text.split()
                art_length.append(len(j)  )
                count +=1
            #print("Human:", art_length, art_length/count)
            length +=statistics.median(art_length) 
            length_h += count
            length_hw += sum(art_length)
            ct += 1

ct = 0
with open('processed_machine.json') as f:
    while ct < total:
        line = f.readline()
        if len(line)!=0:
            art = json.loads(line) 
            array_list = art.get('article')
            array_article = nlp(array_list) 
            art_length = [] 
            count = 0
            for i in array_article.sents:
                j = i.text.split()
                art_length.append(len(j)  )
                count +=1
            length_mach +=statistics.median(art_length) 
            length_mw += sum(art_length)
            #print("Machine:",art_length, art_length/count)
            length_m += count 
            ct += 1

print("Toal length of human articles:", length_hw, length/total, length_h/total)
print("Total length of machine generated articles:", length_mw, length_mach/total, length_m/total) 
