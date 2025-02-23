from bs4 import BeautifulSoup
from data_storage import data_storage

def data_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 这里可以根据具体需求提取信息
    texts = soup.get_text()
    data_storage(texts)