from netmiko import ConnectHandler
import pandas as pd
from commands import show_commands, access_layer_commands
import textfsm
import json
import pprint as p

# Set the display option to show all rows
pd.set_option("display.max_rows", None)

# set variables
devices = []
dataframe_list = []
output_list = []
router_id = 1



#set connection payload function
def device_dict(ip:str)->dict:
    device = {
        "device_type" : "cisco_ios",
        "ip" : ip,
        "username" : "derive",
        "password" : "@Derive123",
        "secret" : "@Derive123"
    }
    return device

def core_commands(id:int)->list:
    admin_switch_commands = ['router ospf 193', f'router-id 1.1.1.{str(id)}', 'auto-cost reference-bandwidth 10000', 'network 192.168.0.0 0.0.255.255 area 0.0.0.0', 'network 172.16.0.0 0.0.255.255 area 0.0.0.0', 'network 10.0.0.0 0.255.255.255 area 0.0.0.0']
    return admin_switch_commands

#initialize connection
dls1_connect = ConnectHandler(**device_dict(ip="192.168.193.191"))
dls1_connect.enable()
dls_details = dls1_connect.send_command("show cdp neighbors detail", use_textfsm = True)
#second connection to get info from dls1
cls_connect = ConnectHandler(**device_dict(ip="192.168.193.190"))
cls_connect.enable()
cls_details = cls_connect.send_command("show cdp neighbors detail", use_textfsm = True)

for detail in dls_details:
    dict_ = {'name': detail['destination_host'], 'ip': detail['management_ip']}

    if dict_ not in devices and dict_['ip'] and dict_['ip'] != '10.40.1.1':
        devices.append(dict_)

for detail in cls_details:
    dict_ = {'name': detail['destination_host'], 'ip': detail['management_ip']}

    if dict_ not in devices and dict_['ip'] and dict_['ip'] != '10.40.1.1' and dict_['ip'] != '10.40.1.2':
        devices.append(dict_)

cls_connect.disconnect()
dls1_connect.disconnect()

p.pprint(devices)


#configure switches
for device in devices:
    
    #establish connection
    net_connect = ConnectHandler(**device_dict(ip=device['ip']))
    net_connect.enable()
    net_connect.config_mode()

    if device['name'][0] == 'A':
        net_connect.send_config_set(access_layer_commands)
        net_connect.disconnect()
    elif device['name'][0] != 'A':
        print(core_commands(router_id))
        net_connect.send_config_set(core_commands(router_id))
        net_connect.disconnect()
        router_id += 1
        print(core_commands(router_id))
        



