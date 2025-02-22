from typing import Dict, List, Optional  
import logging  
from bs4 import BeautifulSoup  
from urllib.parse import urljoin  

class Parser:  
    def __init__(self):  
        self.logger = logging.getLogger(__name__)  

    def parse(self, html: str, base_url: str = '') -> Dict:  
        """  
        简化的解析方法，兼容测试  
        
        :param html: HTML 内容  
        :param base_url: 基础 URL（可选）  
        :return: 解析后的数据字典  
        """  
        try:  
            soup = BeautifulSoup(html, 'html.parser')  
            
            return {  
                'title': self._extract_title(soup),  
                'text': soup.get_text(),  
                'links': [a.get('href') for a in soup.find_all('a', href=True)]  
            }  

        except Exception as e:  
            self.logger.error(f"解析 HTML 时发生错误: {e}")  
            return {}  

    def _extract_title(self, soup) -> Optional[str]:  
        """  
        提取页面标题  
        """  
        title_tag = soup.find('title')  
        return title_tag.text.strip() if title_tag else None  

class DataParser:  
    def __init__(self):  
        self.logger = logging.getLogger(__name__)  

    def parse(self, html: str, base_url: str) -> Dict:  
        """  
        详细的 HTML 解析方法  
        
        :param html: HTML 内容  
        :param base_url: 基础 URL  
        :return: 解析后的数据字典  
        """  
        try:  
            soup = BeautifulSoup(html, 'html.parser')  

            # 提取标题  
            title = self._extract_title(soup)  
            
            # 提取正文  
            body = self._extract_body(soup)  
            
            # 提取元数据  
            meta = self._extract_meta(soup)  
            
            # 提取图片链接  
            images = self._extract_images(soup, base_url)  

            return {  
                'title': title,  
                'body': body,  
                'meta': meta,  
                'images': images,  
                'links': self.extract_links(html, base_url)  
            }  

        except Exception as e:  
            self.logger.error(f"解析 HTML 时发生错误: {e}")  
            return {}  

    def _extract_title(self, soup) -> Optional[str]:  
        """  
        提取页面标题  
        """  
        title_tag = soup.find('title')  
        return title_tag.text.strip() if title_tag else None  

    def _extract_body(self, soup) -> Optional[str]:  
        """  
        提取页面正文  
        """  
        body = soup.find('body')  
        return body.text.strip() if body else None  

    def _extract_meta(self, soup) -> Dict[str, str]:  
        """  
        提取页面元数据  
        """  
        meta_tags = soup.find_all('meta')  
        meta_data = {}  
        for tag in meta_tags:  
            name = tag.get('name') or tag.get('property')  
            content = tag.get('content')  
            if name and content:  
                meta_data[name] = content  
        return meta_data  

    def _extract_images(self, soup, base_url: str) -> List[str]:  
        """  
        提取页面图片链接  
        """  
        images = []  
        for img in soup.find_all('img'):  
            src = img.get('src')  
            if src:  
                images.append(urljoin(base_url, src))  
        return images  

    def extract_links(self, html: str, base_url: str) -> List[str]:  
        """  
        提取页面链接  
        """  
        try:  
            soup = BeautifulSoup(html, 'html.parser')  
            links = []  
            for a in soup.find_all('a', href=True):  
                href = a['href']  
                links.append(urljoin(base_url, href))  
            return links  
        except Exception as e:  
            self.logger.error(f"提取链接时发生错误: {e}")  
            return []