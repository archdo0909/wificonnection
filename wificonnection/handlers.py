from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler
import os, json, git, urllib, requests
from subprocess import Popen, PIPE, TimeoutExpired, SubprocessError


class WifiHandler(IPythonHandler):

    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

    def get(self):
        interface_name = 'wlx88366cf69460'
        sudo_password = 'luxrobo'
        commands = ['sudo', 'iw', interface_name, 'scan']

        ssid_set = set()
        # scan wifi list
        try:
            with Popen(commands, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                output = proc.communicate(input=(sudo_password+'\n').encode())

                # handling exception of commands execution
            assert output[1].decode() == ''
        except AssertionError as e:
            self.error_and_return('Wifi scanning failed')
            return
        except SubprocessError as e:
            print(e)
            self.error_and_return('Improper Popen object opened')
            return

        # parsing all ssid list
        for each_line in output[0].decode('utf-8').split('\n'):
            if each_line.find('SSID:') != -1:
                each_line = each_line.split(' ')[1:]
                ssid_set.add(each_line[0])

        ssid_list = [x for x in ssid_set 
                        if x != "" and x.find('x00') == -1]

        self.write({'status': 200, 
                    'statusText': 'Wifi scanning success',
                    'data' : ssid_list
        }) 

def setup_handlers(nbapp):
    route_pattern = ujoin(nbapp.settings['base_url'], '/wifi/scan')
    nbapp.add_handlers('.*', [(route_pattern, WifiHandler)])

