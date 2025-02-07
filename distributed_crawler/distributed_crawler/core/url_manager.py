# distributed_crawler/core/url_manager.py  
import redis   # type: ignore
from typing import Set, List, Optional  
from ..config import REDIS_CONFIG   # type: ignore

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