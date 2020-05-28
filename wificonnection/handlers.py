from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler
import os, json, urllib, requests
from subprocess import Popen, PIPE, TimeoutExpired, SubprocessError

class WifiHandler(IPythonHandler):
    
    # input system call parameter
    interface_name = 'wlx88366cf69460'
    sudo_password = 'luxrobo'

    def select_cmd(self, x):

        # choose the commands want to call
        return {
            'search_wifi_list' : ['sudo', 'iw', interface_name, 'scan'],
            'interface_down' : ['sudo', 'ifconfig', interface_name, 'down'],
            'interface_up' : ['sudo', 'ifconfig', interface_name, 'up'],
            'current_wifi' : ['sudo', 'wpa_cli', interface_name, 'list_networks']
        }.get(x, None)

    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

    def interface_up(self):

        # raise the wireless interface 
        cmd = self.select_cmd('interface_up')
        try:
            subprocess.run(cmd)
        except SubprocessError as e:
            print(e)
            print('interface up error')
            return

    def interface_down(self):

        # kill the wireless interface
        cmd = self.select_cmd('interface_down')
        try:
            subprocess.run(cmd)
        except SubprocessError as e:
            print(e)
            print('interfae down error')
            return
    
class CurrentWifiHandler(WifiHandler):

    def error_and_return(self, reason):

        # send error
        self.send_error(500, reason=reason)

    def get(self):

        cmd = self.select_cmd('current_wifi')        
        # get current connected wifi
        try:
            with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
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
        
        cmd = self.select_cmd('search_wifi_list')
        ssid_set = set()
        # scan wifi list
        try:
            with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
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