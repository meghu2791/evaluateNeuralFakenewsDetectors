news = "Online disinformation, or fake news intended to deceive, has emerged as a major societal problem. Currently, fake news articles are written by humans, but recently-introduced AI technology based on Neural Networks might enable adversaries to generate fake news. Our goal is to reliably detect this “neural fake news” so that its harm can be minimized."
from selenium import webdriver
from seleniumrequests import Firefox 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import argparse
import req
driver = webdriver.Firefox()
driver.get("https://grover.allenai.org/detect")
driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").clear()
driver.find_element_by_css_selector("textarea.ant-input.sc-dxgOiQ.sc-kTUwUJ.gEHnFy").send_keys(news)
ans = driver.find_element_by_css_selector("button.ant-btn.sc-bdVaJa.sc-jbKcbu.iUrOzv").submit()
#ant-btn sc-bdVaJa sc-jbKcbu iUrOzv
element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dfVpRl.eIhhqn")))
if element:
    print(element.text.split())
print(element.text.split()[-1])
driver.close()
