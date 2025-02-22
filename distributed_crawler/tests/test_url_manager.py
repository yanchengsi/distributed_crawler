# tests/test_url_manager.py  
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  
from ..crawler.core.url_manager import SeedManager  

def test_seed_manager():  
    # 初始化  
    seed_manager = SeedManager()  
    assert seed_manager.is_empty() == True  
    assert seed_manager.seed_count() == 0  

    # 添加种子  
    seed_manager.add_seed("https://example.com")  
    assert seed_manager.seed_count() == 1  
    assert seed_manager.contains("https://example.com") == True  

    # 重复添加  
    seed_manager.add_seed("https://example.com")  
    assert seed_manager.seed_count() == 1  # 不应重复添加  

    # 移除种子  
    seed_manager.remove_seed("https://example.com")  
    assert seed_manager.is_empty() == True  

    # 清空种子  
    seed_manager.add_seed("https://test1.com")  
    seed_manager.add_seed("https://test2.com")  
    seed_manager.clear_seeds()  
    assert seed_manager.is_empty() == True