from subprocess import call
from threading import Thread

from plane import Plane
from constants import APM_CONNECTION_STRING

def start_mavproxy():
    call(['sudo', 'mavproxy.py', '--master', '/dev/ttyAMA0,57600', '--out',
        '127.0.0.1:14550', '--out', '/dev/ttyUSB0'])

if __name__ == '__main__':
    #_start_mavproxy = Thread(target=start_mavproxy)
    #_start_mavproxy.start()

    print 'Starting....'
    
    Plane(APM_CONNECTION_STRING)
