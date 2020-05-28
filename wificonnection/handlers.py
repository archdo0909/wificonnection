from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler
import os, json, git, urllib, requests
from subprocess import Popen, PIPE, TimeoutExpired, SubprocessError

class WifiHandler(IPythonHandler):

    # input system call parameter
    interface_name = 'wlx88366cf69460'
    sudo_password = 'luxrobo'
    commands_wifi_list = ['sudo', 'iw', interface_name, 'scan']
    commands_current_wifi = ['sudo', 'wpa_cli', '-i', interface_name, 'list_networks']

    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

class CurrentWifiHandler(WifiHandler):

    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

    def get(self):
        
        # get current connected wifi
        try:
            with Popen(commands_current_wifi, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                output = proc.communicate(input=(sudo_password+'\n').encode())
        except:
            print('error')
        
        print(type(output))
        

class WifiListHandler(WifiHandler):
    
    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

    # return the possible wifi list
    def get(self):        
        
        ssid_set = set()
        # scan wifi list
        try:
            with Popen(commands_wifi_list, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
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
    # Determine whether wifi connected
    route_pattern_current_wifi = ujoin(nbapp.settings['base_url'], '/wifi/current')
    nbapp.add_handlers('.*', [(route_pattern_current_wifi, CurrentWifiHandler)])

    # Scanning wifi list
    route_pattern_wifi_list = ujoin(nbapp.settings['base_url'], '/wifi/scan')
    nbapp.add_handlers('.*', [(route_pattern_wifi_list, WifiListHandler)])