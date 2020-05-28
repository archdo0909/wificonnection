from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler
import os, json, urllib, requests
from subprocess import Popen, PIPE, TimeoutExpired, SubprocessError
import subprocess
import pandas as pd

interface_name = 'wlan0'
sudo_password = 'raspberry'

class WifiHandler(IPythonHandler):
    
    # input system call parameter
    def select_cmd(self, x):

        # choose the commands want to call
        return {
            'iwconfig' : ['iwconfig'],
            'search_wifi_list' : ['sudo', 'iw', interface_name, 'scan'],
            'interface_down' : ['sudo', 'ifconfig', interface_name, 'down'],
            'interface_up' : ['sudo', 'ifconfig', interface_name, 'up'],
            'current_wifi' : ['wpa_cli', '-i', interface_name, 'list_networks']
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
            self.error_and_return('interface up error')
            return

    def interface_down(self):

        # kill the wireless interface
        cmd = self.select_cmd('interface_down')
        try:
            subprocess.run(cmd)
        except SubprocessError as e:
            print(e)
            self.error_and_return('interfae down error')
            return
    
class CurrentWifiHandler(WifiHandler):

    def get_current_wifi_info(self):
        
        wifi_info = {
            'wifi_status' : False,
            'wifi_SSID' : None
        }

        cmd = self.select_cmd('iwconfig')
        try:
            with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                output = proc.communicate()
                output = [x.decode('utf-8') for x in output]
        except SubprocessError as e:
            print(e)
            self.error_and_return('Improper Popen object opened')
            return

        try:
            inter_info = [x for x in output if x.find(interface_name) != -1]
            assert len(inter_info) != 0
        except AssertionError as e:
            print(e)
            self.error_and_return("Cannot find wlan0 device interface")
            return

        inter_info = inter_info[0].split(' ')
        
        for data in inter_info:
            if data.find('ESSID') != -1:
                wlan0_info = data.split(':')[1]

        if wlan0_info != 'off/any':
            wifi_info['wifi_status'] = True
            wifi_info['wifi_SSID'] = wlan0_info
        
        # wifi_info_json = json.dumps(wifi_info)

        return wifi_info
                

    def get(self):

        current_wifi_info = self.get_current_wifi_info()

        self.write({'status': 200, 
                    'statusText': 'current wifi information',
                    'data' : current_wifi_info
        }) 
        

class WifiListHandler(WifiHandler):

    # return the possible wifi list
    def get(self):        
        
        cmd = self.select_cmd('search_wifi_list')
        # scan wifi list
        try:
            with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                output = proc.communicate(input=(sudo_password+'\n').encode())

                # handling exception of commands execution
            assert output[1].decode() == ''
        except AssertionError as e:
            # self.error_and_return('Wifi scanning failed')
            return
        except SubprocessError as e:
            print(e)
            # self.error_and_return('Improper Popen object opened')
            return

        # parsing all ssid list
        ssid_cnt = 0
        tmp_scanned_wifi_info = dict()
        for each_line in output[0].decode('utf-8').split('\n'):
            tmp_each_info = []
            if each_line.find('BSS') != -1 and each_line.find('on wlan0') != -1:
                if ssid_cnt != 0 and len(tmp_scanned_wifi_info.get(ssid_cnt)) == 2:
                    tmp_scanned_wifi_info[ssid_cnt].append("FREE")
                ssid_cnt += 1
                tmp_scanned_wifi_info[ssid_cnt] = []
            elif each_line.find('signal') != -1:
                tmp_scanned_wifi_info[ssid_cnt].append(each_line.split(' ')[1])
            elif each_line.find('SSID:') != -1:
                tmp_ssid = each_line.split(' ')[1]
                if tmp_ssid != '' and tmp_ssid.find('x00') == -1:
                    tmp_scanned_wifi_info[ssid_cnt].append(tmp_ssid)
            elif each_line.find('RSN') != -1:
                tmp_scanned_wifi_info[ssid_cnt].append('PSK')

        # Sort out the duplicate value and generate json format 
        df_scanned_wifi_info = pd.DataFrame(data=tmp_scanned_wifi_info.values(),
                                                columns=['SIGNAL', 'SSID', 'PSK'])[['SSID', 'PSK', 'SIGNAL']]
        df_tmp_psk = df_scanned_wifi_info[['SSID', 'PSK']].drop_duplicates()
        df_tmp_signal = df_scanned_wifi_info.groupby('SSID').SIGNAL.min().reset_index(name = "SIGNAL")
        wifi_info = pd.merge(
            df_tmp_psk, df_tmp_signal, how="inner", on="SSID"
        ).sort_values(by=['SIGNAL']).set_index('SSID', drop=True).T.to_dict('list')

        self.write({'status': 200, 
                    'statusText': 'Wifi scanning success',
                    'data' : wifi_info
        }) 

def setup_handlers(nbapp):
    # Determine whether wifi connected
    route_pattern_current_wifi = ujoin(nbapp.settings['base_url'], '/wifi/current')
    nbapp.add_handlers('.*', [(route_pattern_current_wifi, CurrentWifiHandler)])

    # Scanning wifi list
    route_pattern_wifi_list = ujoin(nbapp.settings['base_url'], '/wifi/scan')
    nbapp.add_handlers('.*', [(route_pattern_wifi_list, WifiListHandler)])