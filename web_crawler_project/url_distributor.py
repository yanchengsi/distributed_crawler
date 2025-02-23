import multiprocessing
from data_crawler import data_crawler

def url_distributor(url_manager, num_processes):
    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=data_crawler, args=(url_manager,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()