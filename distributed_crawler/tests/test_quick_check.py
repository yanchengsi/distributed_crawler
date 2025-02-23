
import pytest  
from ..crawler.core.data_crawler import Crawler
from ..crawler.core.data_parser import Parser
from requests.exceptions import RequestException

def test_crawler_download():
    """测试基础网页下载（使用测试网站）"""
    crawler = Crawler()
    
    # 测试正常情况
    test_url = "http://httpbin.org/get"  # 测试专用网站
    html = crawler.download(test_url)
    assert "headers" in html, "下载内容异常"
    
    # 测试异常处理
    bad_url = "http://invalid.website12345abcdef"
    try:
        crawler.download(bad_url)
    except RequestException:
        assert True  # 期望抛出异常
    else:
        assert False, "未正确处理无效URL"
