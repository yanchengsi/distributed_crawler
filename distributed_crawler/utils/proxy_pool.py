# distributed_crawler/utils/proxy_pool.py  
import requests  
import random  
import logging  
import re  
import time  
from typing import List, Optional, Dict  
from concurrent.futures import ThreadPoolExecutor, as_completed  

class Proxy:  
    def __init__(self, address: str, protocol: str = 'http'):  
        self.address = address  
        self.protocol = protocol  
        self.score = 100  # 初始分数  
        self.last_check_time = 0  
        self.response_time = float('inf')  

class ProxyPool:  
    def __init__(  
        self,   
        max_proxies: int = 100,   
        check_interval: int = 1800,  # 30分钟检查一次  
        validate_timeout: int = 5  
    ):  
        self.proxies: List[Proxy] = []  
        self.max_proxies = max_proxies  
        self.check_interval = check_interval  
        self.validate_timeout = validate_timeout  
        self.logger = logging.getLogger(__name__)  

    def fetch_free_proxies(self):  
        """  
        从多个代理源获取代理  
        """  
        proxy_sources = [  
            'https://free-proxy-list.net/',  
            'https://www.proxy-list.download/api/v1/get?type=http',  
            'https://www.proxyscan.io/download?type=http',  
            # 添加更多可靠的代理源  
        ]  

        with ThreadPoolExecutor(max_workers=5) as executor:  
            futures = [executor.submit(self._fetch_from_source, source) for source in proxy_sources]  
            
            for future in as_completed(futures):  
                try:  
                    proxies = future.result()  
                    self.add_proxies(proxies)  
                except Exception as e:  
                    self.logger.error(f"获取代理失败: {e}")  

    def _fetch_from_source(self, source: str) -> List[str]:  
        """  
        从单个源获取代理  
        """  
        try:  
            response = requests.get(source, timeout=10)  
            return self._parse_proxies(response.text)  
        except Exception as e:  
            self.logger.warning(f"获取代理源 {source} 失败: {e}")  
            return []  

    def _parse_proxies(self, content: str) -> List[str]:  
        """  
        解析代理  
        支持多种格式  
        """  
        proxy_patterns = [  
            r'\d+\.\d+\.\d+\.\d+:\d+',  # IP:PORT 格式  
            r'(\d+\.\d+\.\d+\.\d+)[\s:]+(\d+)'  # 空格分隔的 IP PORT  
        ]  
        
        proxies = []  
        for pattern in proxy_patterns:  
            proxies.extend(re.findall(pattern, content))  
        
        return [f"{p}" if isinstance(p, str) else ":".join(p) for p in proxies]  

    def add_proxies(self, proxies: List[str]):  
        """  
        添加代理到代理池  
        """  
        for proxy_str in proxies:  
            if len(self.proxies) >= self.max_proxies:  
                break  
            
            # 去重  
            if not any(p.address == proxy_str for p in self.proxies):  
                self.proxies.append(Proxy(proxy_str))  

    def validate_proxy(self, proxy: Proxy) -> bool:  
        """  
        验证代理可用性  
        """  
        try:  
            start_time = time.time()  
            response = requests.get(  
                'http://httpbin.org/ip',   
                proxies={proxy.protocol: f'{proxy.protocol}://{proxy.address}'},  
                timeout=self.validate_timeout  
            )  
            
            # 计算响应时间  
            proxy.response_time = time.time() - start_time  
            
            return response.status_code == 200  
        except Exception as e:  
            self.logger.debug(f"代理 {proxy.address} 验证失败: {e}")  
            return False  

    def get_proxy(self) -> Optional[Proxy]:  
        """  
        获取可用代理  
        优先选择高分数和响应快的代理  
        """  
        # 如果代理池为空，获取新代理  
        if not self.proxies:  
            self.fetch_free_proxies()  

        # 过滤和排序代理  
        valid_proxies = [  
            p for p in self.proxies   
            if time.time() - p.last_check_time > self.check_interval  
        ]  

        # 按分数和响应时间排序  
        valid_proxies.sort(key=lambda x: (x.score, x.response_time), reverse=True)  

        return valid_proxies[0] if valid_proxies else None  

    def update_proxy_score(self, proxy: Proxy, success: bool):  
        """  
        根据使用情况更新代理评分  
        """  
        if success:  
            proxy.score = min(100, proxy.score + 10)  
        else:  
            proxy.score = max(0, proxy.score - 20)  
        
        proxy.last_check_time = time.time()  

    def periodic_proxy_check(self):  
        """  
        定期检查代理可用性  
        """  
        with ThreadPoolExecutor(max_workers=10) as executor:  
            futures = {  
                executor.submit(self.validate_proxy, proxy): proxy   
                for proxy in self.proxies  
            }  

            for future in as_completed(futures):  
                proxy = futures[future]  
                try:  
                    is_valid = future.result()  
                    if not is_valid:  
                        self.remove_proxy(proxy)  
                except Exception as e:  
                    self.logger.error(f"代理检查错误: {e}")  

    def remove_proxy(self, proxy: Proxy):  
        """  
        移除无效代理  
        """  
        if proxy in self.proxies:  
            self.proxies.remove(proxy)