from flask import Flask, request
import requests
from time import sleep
import os
import json
from threading import Thread, Lock

BASE_URL = '/api/v1/'
MIGRATIONS_FOLDER = os.path.abspath('db_migrations')
open_ports = []
curr_port_index = 0
requests_count = 0
port_lock = Lock()
requests_count_lock = Lock()

app = Flask(__name__)

# Load Balancer
def log_requests(url, method):
    print('URL called: {}, Method: {}'.format(url, method))

def make_request(api_url, method, payload = None, log_requests = False):
    global port_lock, curr_port_index

    port_lock.acquire()
    if curr_port_index >= len(open_ports):
        curr_port_index = 0
    port_lock.release()

    port = open_ports[curr_port_index]
    url = 'http://localhost:' + str(port) + BASE_URL + api_url

    if method == 'GET':
        resp = requests.get(url)
        if log_requests:
            log_requests(url, method)
    
    elif method == 'POST':
        resp = requests.post(url = url, json = payload)
        if log_requests:
            log_requests(url, method)
    
    else:
        resp = requests.delete(url)
        if log_requests:
            log_requests(url, method)

    if resp.status_code == 204:
        json_resp = {}
    else:
        if resp.status_code >= 400:
            json_resp = {}
        else:
            json_resp = resp.json()

    port_lock.acquire()
    curr_port_index = (curr_port_index + 1) % len(open_ports)
    port_lock.release()

    return json_resp, resp.status_code


@app.route(BASE_URL + '<path:api>', methods = ["GET", "POST", "DELETE"])
def load_balancer(api):
    global requests_count

    requests_count_lock.acquire()
    requests_count += 1
    requests_count_lock.release()

    payload = None
    if request.method == 'POST':
        payload = request.get_json(force = True)
    
    resp, status = make_request(api, request.method, payload)
    return json.dumps(resp), status

# Fault Tolerance
def fault_tolerance():
    global open_ports
    sleep(5)

    try:
        while True:
            port_lock.acquire()
            len_ports = len(open_ports)
            port_lock.release()
            
            i = 0
            while i < len_ports:
                port = open_ports[i]
                url = 'http://localhost:' + str(port) + BASE_URL + '_health'
                resp = requests.get(url)

                # Restart Container if it is crashed
                if resp.status_code == 500:
                    print("Container crashed on port : ", port)
                    
                    port_lock.acquire()
                    del open_ports[i]
                    port_lock.release()

                    delete_command = 'docker rm -f acts-' + str(port)
                    print(delete_command)
                    os.system(delete_command)

                    run_command = 'docker run -d --name acts-{} -p {}:5000 -v {}:/db_migrations acts'.format(port, port, MIGRATIONS_FOLDER)
                    print(run_command)
                    os.system(run_command)

                    port_lock.acquire()
                    open_ports.append(port)
                    open_ports.sort()
                    port_lock.release()
                else:
                    print("Health Check: Container {} fine".format(port))

                port_lock.acquire()
                len_ports = len(open_ports)
                port_lock.release()

                i += 1
                if i>= len_ports:
                    break
            
            print()
            i = 0
            sleep(5)
    except Exception as e:
        print(e)

# Scaling
def auto_scaling():
    global requests_count
    while requests_count == 0:
        pass

    while True:
        sleep(15)
        curr_count = requests_count
        print("Count in last 15 secs: ", curr_count)
        num_diff = (curr_count // 20) - len(open_ports) + 1
        print("Difference: ", num_diff)
        if num_diff < 0:
            num_diff = abs(num_diff)
            for i in range(num_diff):
                port_lock.acquire()
                port_to_delete = open_ports.pop()
                port_lock.release()
                
                command = 'docker rm -f acts-' + str(port_to_delete)
                print("Deleting: ", command)
                os.system(command)
                print()
        else:
            for i in range(num_diff):
                port_lock.acquire()
                new_port = open_ports[-1] + 1

                run_command = 'docker run -d --name acts-{} -p {}:5000 -v {}:/db_migrations acts'.format(new_port, new_port, MIGRATIONS_FOLDER)
                print("Creating: ", run_command)
                os.system(run_command)

                open_ports.append(new_port)
                port_lock.release()
                print()
        
        requests_count_lock.acquire()
        requests_count = 0
        requests_count_lock.release()


def init():
    command = 'docker run -d -p 8000:5000 --name {} -v {}:/db_migrations acts'.format('acts-8000', MIGRATIONS_FOLDER)
    os.system(command)
    command = 'docker run -d -p 8001:5000 --name {} -v {}:/db_migrations acts'.format('acts-8001', MIGRATIONS_FOLDER)
    os.system(command)
    open_ports.append(8000)
    open_ports.append(8001)


def run_app():
    app.run(host = '0.0.0.0', port = 5000)

if __name__ == '__main__':
    init()

    load_balancer_th = Thread(target = run_app)
    load_balancer_th.start()

    fault_tolerance_th = Thread(target = fault_tolerance)
    fault_tolerance_th.start()

    auto_scaling_th = Thread(target = auto_scaling)
    auto_scaling_th.start()
