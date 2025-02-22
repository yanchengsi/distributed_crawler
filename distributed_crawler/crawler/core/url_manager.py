# crawler/core/url_manager.py  
import redis  
from typing import Set, List, Optional  
from ..config.settings import REDIS_CONFIG  # 修正导入路径  

class URLManager:  
    def __init__(self):  
        self.redis_client = redis.Redis(**REDIS_CONFIG)  
        self.unvisited_key = 'unvisited_urls'  
        self.visited_key = 'visited_urls'  

    def add_seed_urls(self, urls: List[str]):  
        """  
        添加种子 URL  
        """  
        for url in urls:  
            self.redis_client.sadd(self.unvisited_key, url)  

    def get_url(self) -> Optional[str]:  
        """  
        获取一个待爬取的 URL  
        """  
        url = self.redis_client.spop(self.unvisited_key)  
        if url:  
            self.redis_client.sadd(self.visited_key, url)  
        return url.decode('utf-8') if url else None  

    def add_urls(self, urls: List[str]):  
        """  
        添加新的 URL  
        """  
        for url in urls:  
            # 避免重复和已访问的 URL  
            if not self.redis_client.sismember(self.visited_key, url):  
                self.redis_client.sadd(self.unvisited_key, url)  

    def get_visited_urls(self) -> Set[str]:  
        """  
        获取已访问的 URL  
        """  
        return {url.decode('utf-8') for url in self.redis_client.smembers(self.visited_key)}  

class SeedManager:  
    def __init__(self):  
        self.seeds = set()  # 使用 set 替代 list，自动去重  

    def add_seed(self, url):  
        """  
        添加单个种子 URL  
        :param url: 要添加的 URL  
        """  
        self.seeds.add(url)  

    def remove_seed(self, url):  
        """  
        移除指定的种子 URL  
        :param url: 要移除的 URL  
        """  
        self.seeds.discard(url)  # 安全移除，不存在不会报错  

    def get_seeds(self):  
        """  
        获取所有种子 URL  
        :return: 种子 URL 列表  
        """  
        return list(self.seeds)  

    def clear_seeds(self):  
        """  
        清空所有种子 URL  
        """  
        self.seeds.clear()  

    def seed_count(self):  
        """  
        获取种子 URL 的数量  
        :return: 种子数量  
        """  
        return len(self.seeds)  

    def is_empty(self):  
        """  
        检查是否没有种子 URL  
        :return: 是否为空  
        """  
        return len(self.seeds) == 0  

    def contains(self, url):  
        """  
        检查指定 URL 是否已存在  
        :param url: 要检查的 URL  
        :return: 是否存在  
        """  
        return url in self.seeds