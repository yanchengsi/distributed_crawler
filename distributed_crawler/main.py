# distributed_crawler/main.py  
import logging  
from crawler.core.url_manager import URLManager  
from utils.proxy_pool import ProxyPool
from distributed_crawler.utils.robots_checker import RobotsChecker  # 修正路径  
from crawler.core.data_crawler import DataCrawler  
from crawler.core.data_storage import FileStorage
def main():  
    # 配置日志  
    logging.basicConfig(level=logging.INFO)  

    # 初始化组件  
    url_manager = URLManager()  
    proxy_pool = ProxyPool()  
    robots_checker = RobotsChecker()  

    # 添加种子 URL  
    seed_urls = [  
        'https://www.python.org',  
        'https://www.github.com',  
        'https://www.wikipedia.org'  
    ]  
    url_manager.add_seed_urls(seed_urls)  

    # 初始化存储模块（文件存储）  
    storage = FileStorage(file_path='data.json')  

    # 创建爬虫实例  
    data_crawler = DataCrawler(  
        url_manager=url_manager,   
        proxy_pool=proxy_pool,   
        robots_checker=robots_checker,  
        storage=storage  
    )  

    # 开始爬取  
    data_crawler.crawl()  

if __name__ == '__main__':  
    main()