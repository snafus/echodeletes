
import argparse
import json
import requests
import random
import string

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from queue import Queue, Empty

q = Queue()

def send_request(session, data):
    url = 'http://localhost:8000/deletes'
    r = session.post(url, json=data)  #, headers={'Content-Type':'application/json'})
    r.raise_for_status()
    # return r.json()


def prun():
    s = requests.Session()
    s.headers.update({'Content-Type':'application/json'})
    while True:
        try:
            data = q.get(block=False)
        except Empty:
            return 
        send_request(s, data)

def run():
    vos = ['atlas', 'cms', 'lhcb']
    letters = string.ascii_lowercase
    def gen_path():
        return '/'.join([''.join([random.choice(letters) for y in range(random.randint(5,20))]) for _ in range(3)])
        
    for _ in range(1_000):
        d = {'poolname':random.choice(vos), 
             'oid': gen_path(),
             'state':"Set"}
        q.put(d)
    print("prepared inputs")

    ftrs = []
    with ProcessPoolExecutor(max_workers=50) as executor:
        for i in range(10):
            ftrs.append(executor.submit(prun))

    for f in ftrs:
        f.result()

    #r = send_request()
    #print(r)


if __name__ == "__main__":
    run()


