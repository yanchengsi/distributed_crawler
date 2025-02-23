import queue

class URLManager:
    def __init__(self):
        self.new_urls = queue.Queue()
        self.old_urls = set()

    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.old_urls:
            self.new_urls.put(url)
            self.old_urls.add(url)

    def has_new_url(self):
        return not self.new_urls.empty()

    def get_new_url(self):
        return self.new_urls.get()