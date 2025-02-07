# distributed_crawler/core/data_storage.py  
import logging  
import json  
from typing import Dict, List, Optional  
from abc import ABC, abstractmethod  
import pymongo   # type: ignore
import mysql.connector   # type: ignore

class DataStorage(ABC):  
    """  
    数据存储抽象基类  
    """  
    @abstractmethod  
    def save(self, data: Dict):  
        """  
        保存数据  
        :param data: 要保存的数据  
        """  
        pass  

class FileStorage(DataStorage):  
    """  
    文件存储实现  
    """  
    def __init__(self, file_path: str = 'data.json'):  
        self.file_path = file_path  
        self.logger = logging.getLogger(__name__)  

    def save(self, data: Dict):  
        try:  
            with open(self.file_path, 'a', encoding='utf-8') as f:  
                json.dump(data, f, ensure_ascii=False)  
                f.write('\n')  
        except Exception as e:  
            self.logger.error(f"保存数据到文件时出错: {e}")  

class MongoDBStorage(DataStorage):  
    """  
    MongoDB 存储实现  
    """  
    def __init__(self, db_config: Dict):  
        self.db_config = db_config  
        self.logger = logging.getLogger(__name__)  
        self.client = pymongo.MongoClient(**self.db_config)  
        self.db = self.client[self.db_config.get('db_name', 'crawler_db')]  
        self.collection = self.db['pages']  

    def save(self, data: Dict):  
        try:  
            self.collection.insert_one(data)  
        except Exception as e:  
            self.logger.error(f"保存数据到 MongoDB 时出错: {e}")  

class MySQLStorage(DataStorage):  
    """  
    MySQL 存储实现  
    """  
    def __init__(self, db_config: Dict):  
        self.db_config = db_config  
        self.logger = logging.getLogger(__name__)  
        self.conn = mysql.connector.connect(**self.db_config)  
        self.cursor = self.conn.cursor()  

        # 初始化表结构  
        self.cursor.execute("""  
            CREATE TABLE IF NOT EXISTS pages (  
                id INT AUTO_INCREMENT PRIMARY KEY,  
                url VARCHAR(512) NOT NULL,  
                title TEXT,  
                body MEDIUMTEXT,  
                meta JSON,  
                images JSON,  
                links JSON,  
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
            )  
        """)  
        self.conn.commit()  

    def save(self, data: Dict):  
        try:  
            query = """  
                INSERT INTO pages (url, title, body, meta, images, links)  
                VALUES (%s, %s, %s, %s, %s, %s)  
            """  
            values = (  
                data.get('url'),  
                data.get('title'),  
                data.get('body'),  
                json.dumps(data.get('meta', {})),  
                json.dumps(data.get('images', [])),  
                json.dumps(data.get('links', []))  
            )  
            self.cursor.execute(query, values)  
            self.conn.commit()  
        except Exception as e:  
            self.logger.error(f"保存数据到 MySQL 时出错: {e}")  

    def close(self):  
        """  
        关闭数据库连接  
        """  
        self.cursor.close()  
        self.conn.close()  
