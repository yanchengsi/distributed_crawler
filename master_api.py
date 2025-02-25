from flask import Flask, jsonify, request
from crawler.core.url_manager import URLManager
import logging

app = Flask(__name__)
url_manager = URLManager()
logging.basicConfig(level=logging.INFO)

@app.route('/get_task', methods=['GET'])
def get_task():
    url = url_manager.get_waiting_url()
    if url:
        return jsonify({'task': url})
    else:
        return jsonify({'task': None})

@app.route('/report_status', methods=['POST'])
def report_status():
    data = request.get_json()
    status = data.get('status')
    url = data.get('url')
    if status =='success':
        url_manager.mark_url_visited(url)
    elif status == 'failed':
        url_manager.mark_url_failed(url)
    logging.info(f'Received status report for {url}: {status}')
    return jsonify({'message': 'Status report received'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
