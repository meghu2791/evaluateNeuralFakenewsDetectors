news = "Online disinformation, or fake news intended to deceive, has emerged as a major societal problem. Currently, fake news articles are written by humans, but recently-introduced AI technology based on Neural Networks might enable adversaries to generate fake news. Our goal is to reliably detect this “neural fake news” so that its harm can be minimized."
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import argparse
import req

#initialization
human_data = []
machine_data = []
driver = webdriver.Firefox()

#command-line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str)
parser.add_argument('--file_name', type=str)

parser.add_argument('--save_human_file', type=str)
parser.add_argument('--save_machine_file', type=str)

args = parser.parse_args()
model = args.model
file_name = args.file_name

save_human_file = args.save_human_file
save_machine_file = args.save_machine_file

store_human_data = []
store_machine_data = []

#check_now = human_data

#driver.find_element_by_class_name("ant-input.sc-htpNat.sc-ksYbfQ.iuRnVj").clear()
#driver.find_element_by_class_name("ant-input.sc-htpNat.sc-ksYbfQ.iuRnVj").send_keys("Online disinformation, or fake news intended to deceive, has emerged as a major societal problem. Currently, fake news articles are written by humans, but recently-introduced AI technology based on Neural Networks might enable adversaries to generate fake news. Our goal is to reliably detect this “neural fake news” so that its harm can be minimized.")
#ans = driver.find_element_by_css_selector("button.ant-btn.sc-bwzfXH.sc-jDwBTQ.kNoRcT.ant-btn-default").submit()
#element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sc-kvZOFW.bpFYHv")))

def detectGrover(news, driver, store_human_data, store_machine_data):
    #for news in check_now:
    driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").clear()
    driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").send_keys(news.get('article'))
    ans = driver.find_element_by_css_selector("button.ant-btn.sc-bdVaJa.sc-jbKcbu.iUrOzv").submit()
#ant-btn sc-bdVaJa sc-jbKcbu iUrOzv
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dfVpRl.eIhhqn")))
        if element:
            print(element.text.split())
            if (news['label'] not in element.text.split()) and ((news['label'] + ".") not in element.text.split()[-1]):
                print(news['article'], element.text.split(), news['label'])
            else:
                if news['label'] == 'human':
                    store_human_data.append(news)
                else:
                    store_machine_data.append(news)
    except:
        ans = driver.find_element_by_css_selector("button.ant-btn.sc-bdVaJa.sc-jbKcbu.iUrOzv").submit()
        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dfVpRl.eIhhqn")))
            if element:
                if (news['label'] not in element.text.split()) and (
                        (news['label'] + ".") not in element.text.split()[-1]):
                    print(news['article'], element.text.split(), news['label'])
                else:
                    if news['label'] == 'human':
                        store_human_data.append(news)
                    else:
                        store_machine_data.append(news)
        except:
            print("Unresponsive!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")



def detectGPT2(news, driver, store_human_data, store_machine_data):
    if 'article' in news.keys():
        #print(news.keys())
        driver.find_element_by_id("textbox").clear()
        driver.find_element_by_id("textbox").send_keys(news['article'])
        temp = driver.find_element_by_id("real-percentage")
        time.sleep(5)
        temp = driver.find_element_by_id("real-percentage").text.split('%')
        if float(temp[0]) > 50:
            label = 'human'
        else:
            label = 'machine'
        #if label not in news['label']:
        #    print(news['article'], label, news['label'])
        #else:
        if label == 'human':
            store_human_data.append(news)
        else:
            store_machine_data.append(news)
    #driver.close()

def detectFakeBox(news, store_human_data, store_machine_data):
    maxtry = 10
    res = 0
    label = ""
    try:
        while maxtry > 0:
            res = req.sendRequest(news.get('article'))
            maxtry = maxtry - 1
    except:
        print("Internet Error!Sleep 3 sec！", res, maxtry)
        time.sleep(3)

    if res:
        if res["content_decision"] == 'impartial' or ((res['content_decision'] == 'bias') and (res['content_score'] < 0.5)):
            label = 'human'
        else:
            label = 'machine'

        if label == news['label']:
            if label == 'human':
                store_human_data.append(news)
            else:
                store_machine_data.append(news)


#model load
if model == 'groverAI':
    driver.get("https://grover.allenai.org/detect")
    #detectGrover(human_data, driver)
elif model == 'gpt2':
    driver.get("https://huggingface.co/openai-detector")
    #detectGPT2(human_data, driver)
elif model == 'fakebox':
    req.init()
else:
    print("Not supported as yet! TODO:CTRL, FakeBox")

#temporary
i = 0
count = 0
#input read

human_file = open(save_human_file, "a+")
machine_file = open(save_machine_file, "a+")
with open(file_name) as json_file:
    while True:
        line = json_file.readline()
        if len(line)!=0 and (model == 'groverAI'):
            #print(line)
            detectGrover(json.loads(line), driver, store_human_data, store_machine_data)
            count +=1
        elif len(line)!=0 and (model == 'gpt2'):
            len_human = len(store_human_data)
            len_machine = len(store_machine_data)
            detectGPT2(json.loads(line), driver, store_human_data, store_machine_data)
            if len_human < len(store_human_data):
                human_file.write(str(json.dumps(store_human_data[-1]))+'\n')
            elif len_machine < len(store_machine_data):
                machine_file.write(str(json.dumps(store_machine_data[-1]))+'\n')
        elif len(line)!=0 and (model == 'fakebox'):
            len_human = len(store_human_data)
            len_machine = len(store_machine_data)
            detectFakeBox(json.loads(line), store_human_data, store_machine_data)
            if len_human < len(store_human_data):
                human_file.write(str(json.dumps(store_human_data[-1]))+'\n')
            elif len_machine < len(store_machine_data):
                machine_file.write(str(json.dumps(store_machine_data[-1]))+'\n')
        else:
            break

json_file.close()
driver.close()
human_file.close()
machine_file.close()
'''
with open(save_human_file, "w") as json_file:
    for each in store_human_data:
        json_file.write(str(json.dumps(each))+'\n')

with open(save_machine_file, "w") as json_file:
    for each in store_machine_data:
        json_file.write(str(json.dumps(each))+'\n')
json_file.close()

'''