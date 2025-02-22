def test_full_process():  
    """快速验证完整流程"""  
    from distributed_crawler.crawler.core.url_manager import SeedManager  
    from distributed_crawler.crawler.core.data_crawler import Crawler  
    from distributed_crawler.crawler.core.data_parser import Parser  
    import pytest  

    # 准备测试数据  
    test_url = "http://httpbin.org/html"  # 样例页面  
    SeedManager().add_seed(test_url)  

    # 执行爬取  
    crawler = Crawler()  
    html = crawler.download(test_url)  

    # 解析验证  
    parsed_data = Parser().parse(html)  # 修改为无需 base_url 的调用  
    assert parsed_data is not None  
    assert 'title' in parsed_data  
    assert 'text' in parsed_data