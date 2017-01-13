from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from Queue import Queue
from threading import Thread
from time import sleep


class BaseClient(object):

    def __init__(self, ip, port, tcp=True, sending=False):

        self.socket = socket(AF_INET, SOCK_STREAM if tcp else SOCK_DGRAM)
        self.socket.connect((ip, port))

        self.closed = False

        def sending_thread():

            while not self.closed:

                message_list = self.queue.get()

                for message in message_list:

                    self.send('%4.f' % len(message))
                    self.send(message)

                self.queue.task_done()

        if sending:

            self.queue = Queue()

            _sending_thread = Thread(target=sending_thread)
            _sending_thread.start()

    def receive(self, length):

        message = None

        while not message:

            try:

                message = self.socket.recv(length)

            except Exception, e:

                print str(e)
                self.close()

                break

        return message

    def send(self, message):

        try:

            self.socket.send(message.encode('utf-8'))

        except Exception, e:

            print str(e)
            self.close()

    def send_messages(self, *args):

        self.queue.put(args)

    def close(self):

        self.closed = True

        sleep(1)

        self.socket.close()
