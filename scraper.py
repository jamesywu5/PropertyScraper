from bs4 import BeautifulSoup
import requests

page_url = ''
page = requests.get(page_url)

soup = BeautifulSoup(page.content, 'html.parser')

