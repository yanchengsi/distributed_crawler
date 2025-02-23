# config/settings.py  

CONFIG = {  
    'key1': 'value1',  
    'key2': 'value2'  
}
# 基本配置  
REDIS_CONFIG = {  
    'host': 'localhost',  
    'port': 6379,  
    'db': 0  
}  

# 爬虫基本配置  
CRAWLER_CONFIG = {  
    'user_agent': 'DistributedCrawler/1.0',  
    'max_depth': 3,  
    'workers': 10,  
    'robots_enabled': True,  
    'proxy_enabled': True,  
    'max_retry': 3  
}