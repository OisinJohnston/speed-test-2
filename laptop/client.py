import serial
import logging
import sys
import requests
import json

from time import sleep, time
from datetime import datetime
from os import mkdir
from serial.tools import list_ports

PID_MICROBIT = 516
VID_MICROBIT = 3368
TIMEOUT = 0.1

BASE_URL = 'http://localhost:9000'
HEADERS = {'Content-type': 'application/json'}

# logging stuff
try:
    mkdir(".logs")
except FileExistsError:
    pass

fp = f'./.logs/{datetime.now()}.log'.replace(' ', '-')

if sys.platform.lower() == 'win32':
    fp = fp.replace(':', '.')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(fp)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s')

ch.setFormatter(fmt)
fh.setFormatter(fmt)

logger.addHandler(ch)
logger.addHandler(fh)

def register(username):
    requests.post(BASE_URL + '/api/users', data = json.dumps({'name': username}), headers = HEADERS)

def submitsingle(username, time_taken):
    requests.post(BASE_URL + '/api/singleentries', data = json.dumps({'name': username, 'timetaken': time_taken}), headers = HEADERS)

def submittwo(names, winner, winscore):
    requests.post(BASE_URL + '/api/twoentries', data = json.dumps({'names': names, 'winner': winner, 'timetaken': winscore}), headers = HEADERS)

def find_comport(pid, vid, baud):
    """returns a serial port"""
    ser_port = serial.Serial(timeout=TIMEOUT)
    ser_port.baudrate = baud
    ports = list(list_ports.comports())
    # scanning ports
    logger.info("Scanning Ports...")
    for p in ports:
        try:
            logger.info(f'Testing: \n\t port: {p!r} \n\t pid: {p.pid} \n\t vid: {p.vid}')
        except AttributeError:
            continue

        if p.pid == pid and p.vid == vid:
            logger.info(f'found target device: \n\t pid: {p.pid} \n\t vid: {p.vid} \n\t port: {p.device}')
            ser_port.port = str(p.device)
            return ser_port
    return None

def readline(ser):
    while True:
        line = ser.readline().decode('utf-8')
        if line:
            logger.info(f"microbit -> laptop : {line}")
            return line

def main():
    logger.info('looking for microbit')
    ser_micro = find_comport(PID_MICROBIT, VID_MICROBIT, 115200)
    if not ser_micro:
        logger.fatal('microbit not found')
        return

    logger.info('opening and monitoring microbit port')
    ser_micro.open()
    while 1:
        try:
            mode = int(input("How many players? (1/2): ")) -1
            assert mode in (0,1)
        except:
            continue
        if mode == 0:
            name = input("please enter your name: ")
            register(name)
        elif mode == 1:
            names = [input("please enter the first name: "), input("please enter the second name")]
            for name in names:
                register(name)

        ser_micro.write('ready\n'.encode('utf-8'))
        logger.info("laptop -> microbit : 'ready'")
        
        ser_micro.write(f'{mode}\n'.encode('utf-8'))
        logger.info(f"laptop -> microbit : '{mode}'")
        
        resp = readline(ser_micro)

        
        start_time = time()
        resp = readline(ser_micro)
 
        time_taken = time() - start_time

        if mode == 1:
            winnerindex = int(readline(ser_micro).strip())
            winnerscore = int(readline(ser_micro).strip())
            winner = names[winnerindex]
            submittwo(names, winner, winnerscore)
        else:
            submitsingle(name, time_taken)




if __name__ == '__main__':
    main()

