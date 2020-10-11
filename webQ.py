import requests
from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup as soup
import re
import sys
import time

from requests_html import HTMLSession

session = HTMLSession()
r = session.get("https://discriminate.grover.allenai.org")
r.html.render()
print(r.html.render())
agent = requests.utils.default_headers()
'''
agent={"Host": "grover.allenai.org", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0", 
"Accept": "text/html,application/xhtml+xml,application/xl;q=0.9,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate, br",
"Connection": "keep-alive",
"Cookie":"_ga=GA1.2.1157608657.1573011374; _gid=GA1.2.1453773074.1573011374",
"Upgrade-Insecure-Reques
'''
agent.update({'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'})
agent.update({'origin':'https://grover.allenai.org'})
agent.update({'referer': 'https://grover.allenai.org/detect'})
agent.update({'sec-fetch-mode':'cors'})
agent.update({'sec-fetch-site':'same-site'})
agent.update({'host':'discriminate.grover.allenai.org'})

endpoint="https://discriminate.grover.allenai.org/api/disc"
data={'article':'dddd', 'target':'discrimination'}
mainPage = requests.post(url=r.html.render(), data=data, headers=agent)
print(mainPage.text)
