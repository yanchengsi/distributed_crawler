from url_manager import URLManager
from url_distributor import url_distributor
from data_indexer import data_indexing
from data_query import data_query

if __name__ == '__main__':
    url_manager = URLManager()
    # 添加初始 URL
    url_manager.add_new_url('https://example.com')
    num_processes = 4
    url_distributor(url_manager, num_processes)
    data_indexing()
    data_query('example')