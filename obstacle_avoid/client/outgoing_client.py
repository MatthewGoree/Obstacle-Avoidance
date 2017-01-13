from threading import Thread
from time import sleep

from base_client import BaseClient
from ..constants import IP_GROUND, OUT_PORT_1, AVOID_DIST_STAT, AVOID_DIST_MOV
from ..util import feet


class OutgoingClient(BaseClient):
    
    def __init__(self, plane):

        super(OutgoingClient, self).__init__(
            IP_GROUND, OUT_PORT_1, sending=True
        )

        self.plane = plane
        self.has_started = False

        def commands_thread():

            while not self.closed:

                mode = self.plane.mode

                self.send_messages('m' + mode)

                self.plane.update_commands()

                commands = ''
                command_seq = self.plane.commands

                for i in xrange(0, command_seq.count):

                    commands += str(command_seq[i].command) + ' '
                    commands += str(command_seq[i].x) + ' '
                    commands += str(command_seq[i].y) + ' '
                    commands += str(command_seq[i].z) + ' '
        
                self.send_messages('c' + commands[:-1])

                sleep(5)

        def pinging_thread():
    
            while not self.closed:

                if self.plane.in_client.pinged:

                    self.send_messages('ping')
                    self.plane.in_client.pinged = False

                sleep(0.05)

        def send_avoid_radii():

            radii_string = '%0.f %0.f' % (feet(AVOID_DIST_STAT), feet(AVOID_DIST_MOV))

            self.send_messages('r' + radii_string)

        def starting_thread():

            send_avoid_radii()

            _pinging_thread = Thread(target=pinging_thread)
            _pinging_thread.start()

            while not self.has_started:

                sleep(0.1)

            _commands_thread = Thread(target=commands_thread)
            _commands_thread.start()

            @self.plane.vehicle.on_attribute('mode')
            def send_mode(self_, name, value):

                if not self.closed:

                    mode = self.plane.mode

                    self.send_messages('m' + mode)

        _starting_thread = Thread(target=starting_thread)
        _starting_thread.start()

    def start(self):

        self.has_started = True
