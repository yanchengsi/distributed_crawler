import pika
import json
from crawler.core.data_crawler import DataCrawler
from crawler.core.url_manager import URLManager
from utils.proxy_pool import ProxyPool
from distributed_crawler.utils.robots_checker import RobotsChecker
from crawler.core.data_storage import FileStorage
import logging

logging.basicConfig(level=logging.INFO)

def send_task_to_queue(url):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq_server_ip'))
    channel = connection.channel()
    channel.queue_declare(queue='crawler_tasks')
    channel.basic_publish(exchange='', routing_key='crawler_tasks', body=json.dumps({'task': url}))
    connection.close()

def receive_task_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq_server_ip'))
    channel = connection.channel()
    channel.queue_declare(queue='crawler_tasks')

    def callback(ch, method, properties, body):
        task = json.loads(body)['task']
        url_manager = URLManager()
        proxy_pool = ProxyPool()
        robots_checker = RobotsChecker()
        storage = FileStorage(file_path='data.json')
        data_crawler = DataCrawler(
            url_manager=url_manager,
            proxy_pool=proxy_pool,
            robots_checker=robots_checker,
            storage=storage
        )
        try:
            data_crawler.handle_crawl(task)
            send_result_to_queue(task,'success')
        except Exception as e:
            logging.error(f'Error crawling {task}: {e}')
            send_result_to_queue(task, 'failed')

    channel.basic_consume(queue='crawler_tasks', on_message_callback=callback, auto_ack=True)
    logging.info('Waiting for tasks...')
    channel.start_consuming()

def send_result_to_queue(url, status):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq_server_ip'))
    channel = connection.channel()
    channel.queue_declare(queue='crawler_results')
    channel.basic_publish(exchange='', routing_key='crawler_results', body=json.dumps({'url': url,'status': status}))
    connection.close()
