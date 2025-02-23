import requests
from urllib.robotparser import RobotFileParser
from data_parser import data_parser

def check_robots(url):
    rp = RobotFileParser()
    base_url = '/'.join(url.split('/')[:3])
    robots_url = f'{base_url}/robots.txt'
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch('*', url)
    except Exception as e:
        return False

def data_crawler(url_manager):
    while url_manager.has_new_url():
        url = url_manager.get_new_url()
        if check_robots(url):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data_parser(response.text)
            except Exception as e:
                print(f"Error crawling {url}: {e}")