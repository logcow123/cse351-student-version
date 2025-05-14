"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from common import *
import queue

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0

def get_urls(film6, kind):
    global call_count

    urls = film6[kind]
    print(kind)
    for url in urls:
        call_count += 1
        item = get_data_from_server(url)
        print(f'  - {item['name']}')

def main():
    global call_count
    NUM_OF_WORKERS = 90

    q = queue.Queue()
    types = ['characters', 'planets', 'starships', 'vehicles', 'species']

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    url_workers = []
    name_workers = []
    for type in types:
        url_worker = threading.Thread(target=url_producer, args=(q, film6, [type], int(NUM_OF_WORKERS/5)))
        url_workers.append(url_worker)

    for w in range(NUM_OF_WORKERS):
        name_worker = threading.Thread(target=url_consumer, args=(q,))
        name_workers.append(name_worker)

    for u in url_workers:
        u.start()
    for n in name_workers:
        n.start()

    for u in url_workers:
        u.join()
    for n in name_workers:
        n.join()
   
    # Retrieve people
    # get_urls(film6, 'planets')
    # get_urls(film6, 'planets')
    # get_urls(film6, 'starships')
    # get_urls(film6, 'vehicles')
    # get_urls(film6, 'species')

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')


def url_producer(queue, dict, types, num_of_consumers):
    for type in types:
        for url in dict[type]:
            queue.put(url)
    for n in range(num_of_consumers):
        queue.put(None)

def url_consumer(queue):
    while True:
        url = queue.get()
        if url == None:
            break
        else:
            item = get_data_from_server(url)
            print(item['name'])

if __name__ == "__main__":
    main()
