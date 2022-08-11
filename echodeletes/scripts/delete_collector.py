import argparse 
import configparser
import json
import logging
import sys
import socketserver
import requests
import threading

from pathlib import Path
from threading import Lock

class MyTCPRequestHandler(socketserver.BaseRequestHandler):
    allow_reuse_address = True
    # Override the handle() method
    def handle(self):
        # Receive and print the datagram received from client
        # Print the name of the thread
        logging.debug("Thread Name:{}; Recieved one request from {}"\
                     .format(threading.current_thread().name,
                             self.client_address[0]))
        # self.request is the TCP socket connected to the client
        try:
            self.data = self.request.recv(1024)
            self.data = self.data.strip().decode('utf8').split(":")
            logging.debug("{} wrote: {}".format(self.client_address[0], self.data))
            data  = {'poolname': self.data[0], 
                    'oid': self.data[1],
                    'state':"Set"}
        except Exception as e:
            logging.error(f"Proceesing: {500} Unable to parse input")
            response = json.dumps({'status': 500, 'reason':"Could not not parse input"}).encode('ascii')
            self.request.sendall(response)
            raise e
        
        try:
            resp = requests.post(f'{MyTCPRequestHandler.xrdhost}/deletes', json=data, 
                                                headers={'Content-Type':'application/json'}, timeout=2)
        except requests.exceptions.ReadTimeout as e:
            logging.warning(f"Response: Timeout")
            response = json.dumps({'status': 500, 'reason':"Timeout on request"}).encode('ascii')
            self.request.sendall(response)
            raise e


        if resp.ok:
            logging.debug(f"Response: {resp.raw}; {resp.json()}")
            response = json.dumps({'status': resp.status_code, 
                               'signature':resp.json()['signature'],
                               'id': resp.json()['id']}).encode('ascii')
        else:
            logging.error(f"Response: {resp.status_code} {resp.reason}")
            response = json.dumps({'status': resp.status_code, 'reason':{resp.reason}}).encode('ascii')

        logging.info(f"Delete registered for {resp.json()}")
        self.request.sendall(response)

def run(args, config):
    logging.info("Starting Server")

    MyTCPRequestHandler.xrdhost = 'http://localhost:8000/api/v1'
    # check the host is up
    try:
        r = requests.get(f'{MyTCPRequestHandler.xrdhost}/metrics/ping', timeout=5)
    except requests.exceptions.ReadTimeout as e:
        logging.error(f"PingTest: Timeout in connecting to host {MyTCPRequestHandler.xrdhost}")
        raise e
    except requests.exceptions.ConnectionError as e:
        logging.error(f"PingTest: Could not connect to server {MyTCPRequestHandler.xrdhost}")
        # raise e
        sys.exit(1)

    r.raise_for_status()
    logging.info(r.json())

    # MyTCPRequestHandler.xrdsession = requests.session()

    # prepare and start the loop 
    if args.config:
        ServerAddress = (config['SERVER'].get('address'), config['SERVER'].getint('port'))
    else:
        ServerAddress = ('0.0.0.0', 9931)
    # Create a Server Instance using context manager
    # Each request is processed through a different thread
    with socketserver.ThreadingTCPServer(ServerAddress, MyTCPRequestHandler) as TCPServerObject:
        # Make the server wait forever serving connections
        TCPServerObject.serve_forever()
    logging.info("Server terminating")




if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', '--socketname', dest = 'sockname', type=str)
    parser.add_argument('-w', '--workers', dest = 'n_workers', type=int, default=2)
    parser.add_argument('-d','--debug',help='Enable additional logging',action='store_true')
    parser.add_argument('-l','--log',help='Send all logging to a dedicated file',dest='logfile',default=None)
    parser.add_argument('-c','--config', type=Path, default=None, nargs='*', 
                                         help='ini config file for Observer connection params, etc.')

    args = parser.parse_args()

    logging.basicConfig(level= logging.DEBUG if args.debug else logging.INFO,
                    filename=None if args.logfile is None else args.logfile,
                    format='XRDREPORT-%(asctime)s-%(process)d-%(levelname)s-%(message)s',                  
                    )

    config = None
    if args.config is not None:
        logging.debug("Config files: {}".format(args.config))
        config = configparser.ConfigParser()
        config.read(args.config)

        logging.debug("Sections: {}".format(','.join(config.sections())))

    run(args, config)