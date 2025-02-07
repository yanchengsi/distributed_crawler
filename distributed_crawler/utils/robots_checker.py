# distributed_crawler/utils/robots_checker.py  
import urllib.robotparser  
from urllib.parse import urlparse  
import requests  
import logging  
import time  
from typing import Optional, Dict, Any  

class RobotsChecker:  
    def __init__(  
        self,   
        user_agent: str = 'DistributedCrawler/1.0',   
        cache_expire: int = 3600  # 缓存过期时间，默认1小时  
    ):  
        self.user_agent = user_agent  
        self.robots_cache: Dict[str, Dict[str, Any]] = {}  
        self.logger = logging.getLogger(__name__)  
        self.cache_expire = cache_expire  

    def _is_cache_valid(self, domain: str) -> bool:  
        """  
        检查缓存是否有效  
        """  
        if domain not in self.robots_cache:  
            return False  
        
        current_time = time.time()  
        cache_time = self.robots_cache[domain].get('timestamp', 0)  
        return current_time - cache_time < self.cache_expire  

    def can_fetch(self, url: str) -> bool:  
        """  
        检查是否可以抓取指定 URL，增加了缓存和日志机制  
        """  
        try:  
            parsed_url = urlparse(url)  
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"  

            # 检查缓存  
            if not self._is_cache_valid(domain):  
                robots_url = f"{domain}/robots.txt"  
                
                try:  
                    response = requests.get(robots_url, timeout=5)  
                    
                    if response.status_code == 200:  
                        rp = urllib.robotparser.RobotFileParser()  
                        rp.parse(response.text.splitlines())  
                        
                        self.robots_cache[domain] = {  
                            'parser': rp,  
                            'timestamp': time.time()  
                        }  
                    else:  
                        # 如果无法获取 robots.txt，默认允许  
                        self.logger.warning(f"无法获取 {robots_url}，状态码：{response.status_code}")  
                        return True  

                except requests.RequestException as e:  
                    self.logger.warning(f"获取 robots.txt 失败: {e}")  
                    return True  

            # 检查是否允许爬取  
            rp = self.robots_cache[domain]['parser']  
            is_allowed = rp.can_fetch(self.user_agent, url)  
            
            self.logger.info(f"URL: {url}, 是否允许爬取: {is_allowed}")  
            return is_allowed  

        except Exception as e:  
            self.logger.error(f"检查 robots 协议时发生错误: {e}")  
            return False  

    def get_crawl_delay(self, url: str) -> float:  
        """  
        获取网站建议的爬行延迟，增加了缓存和异常处理  
        """  
        try:  
            parsed_url = urlparse(url)  
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"  

            # 确保已解析 robots.txt  
            if not self._is_cache_valid(domain):  
                self.can_fetch(url)  

            rp = self.robots_cache[domain]['parser']  
            delay = rp.crawl_delay(self.user_agent) or 1.0  
            
            self.logger.info(f"URL: {url}, 建议延迟: {delay} 秒")  
            return delay  

        except Exception as e:  
            self.logger.error(f"获取爬行延迟时发生错误: {e}")  
            return 1.0