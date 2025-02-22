# distributed_crawler/core/data_crawler.py  
import requests  
import logging  
import time  
import random  
from typing import Optional, Dict, List  
from urllib.parse import urlparse, urljoin  

from .data_storage import DataStorage
from distributed_crawler.utils.proxy_pool import ProxyPool   # type: ignore
from distributed_crawler.utils.robots_checker import RobotsChecker   # type: ignore
from .url_manager import URLManager  # 同一目录下的模块
from ..config.settings import CONFIG  # 上级目录的配置 # type: ignore
from .data_parser import DataParser   # type: ignore
# 确保有 Crawler 类的定义  
class Crawler:  
    def download(self, url):  
        # 实现基本下载逻辑  
        import requests  
        response = requests.get(url)  
        return response.text
class DataCrawler:  
    def __init__(  
        self,   
        url_manager: URLManager,   
        proxy_pool: ProxyPool,   
        robots_checker: RobotsChecker,  
        storage: DataStorage,  # 新增存储模块参数  
        data_parser: Optional[DataParser] = None,  
        max_depth: int = 3,  
        crawl_interval: float = 1.0  
    ):  
        self.url_manager = url_manager  
        self.proxy_pool = proxy_pool  
        self.robots_checker = robots_checker  
        self.storage = storage  # 初始化存储模块  
        self.data_parser = data_parser or DataParser()  
        self.logger = logging.getLogger(__name__)  
        self.max_depth = max_depth  
        self.crawl_interval = crawl_interval
        # 配置请求头  
        self.headers = {  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',  
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',  
        }  

    def crawl(self):  
        """  
        主爬取方法  
        """  
        while True:  
            url = self.url_manager.get_waiting_url()  
            
            if not url:  
                self.logger.info("没有更多待爬取的 URL。")  
                break  

            try:  
                self.handle_crawl(url)  
                
                # 控制爬取频率  
                time.sleep(self.crawl_interval + random.uniform(0, 1))  
                
            except Exception as e:
                self.logger.error(f"爬取 {url} 时发生错误: {e}")
    def handle_crawl(self, url: str, depth: int = 0):
        """
        处理单个 URL 的爬取
        
        :param url: 待爬取的 URL
        :param depth: 当前爬取深度
        """
        # 检查深度
        if depth > self.max_depth:
            self.logger.info(f"已达到最大爬取深度 {self.max_depth}")
            return

        # 检查 Robots 协议  
        if not self.robots_checker.can_fetch(url):  
            self.logger.warning(f"不允许爬取 {url}，根据 robots.txt 配置。")  
            self.url_manager.mark_url_failed(url)  
            return  

        # 获取代理  
        proxy = self._get_proxy()  
        
        try:  
            response = self._fetch_url(url, proxy)  
            
            # 处理响应  
            if response:  
                # 解析页面  
                parsed_data = self.data_parser.parse(response.text, url)  
                parsed_data['url'] = url  # 添加 URL 到解析数据中  
                
                # 保存数据到存储模块  
                self.storage.save(parsed_data)  
                
                # 提取新的链接  
                new_links = self._extract_links(response.text, url)  
                
                # 添加新链接到 URL 管理器  
                self.url_manager.add_urls(new_links)  
                
                # 标记 URL 为已访问  
                self.url_manager.mark_url_visited(url)  
                
        except Exception as e:  
            self.logger.error(f"爬取 {url} 时发生错误: {e}")  
            self.url_manager.mark_url_failed(url)

    def _get_proxy(self) -> Optional[Dict[str, str]]:  
        """  
        获取代理  
        
        :return: 代理配置字典  
        """  
        proxy = self.proxy_pool.get_proxy()  
        return {'http': proxy, 'https': proxy} if proxy else None  

    def _fetch_url(self, url: str, proxy: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:  
        """  
        获取 URL 内容  
        
        :param url: 待获取的 URL  
        :param proxy: 代理配置  
        :return: 响应对象  
        """  
        try:  
            # 获取 Robots 建议的延迟  
            crawl_delay = self.robots_checker.get_crawl_delay(url)  
            time.sleep(crawl_delay)  

            response = requests.get(  
                url,   
                headers=self.headers,  
                proxies=proxy,  
                timeout=10  
            )  
            
            response.raise_for_status()  
            return response  
        
        except requests.RequestException as e:  
            self.logger.warning(f"获取 {url} 失败: {e}")  
            return None  

    def _extract_links(self, html: str, base_url: str) -> List[str]:  
        """  
        提取页面中的链接  
        
        :param html: HTML 内容  
        :param base_url: 基础 URL  
        :return: 链接列表  
        """  
        try:  
            # 使用解析器提取链接  
            links = self.data_parser.extract_links(html)  
            
            # 转换为绝对 URL  
            absolute_links = [  
                urljoin(base_url, link)   
                for link in links   
                if self._is_valid_url(urljoin(base_url, link))  
            ]  
            
            return absolute_links  
        except Exception as e:  
            self.logger.error(f"提取链接时发生错误: {e}")  
            return []  

    def _is_valid_url(self, url: str) -> bool:  
        """  
        验证 URL 是否有效  
        
        :param url: 待验证的 URL  
        :return: 是否有效  
        """  
        try:  
            result = urlparse(url)  
            return all([result.scheme, result.netloc])  
        except Exception:  
            return False