from netmiko import ConnectHandler
import pandas as pd
import pprint as p

# Set the display option to show all rows
pd.set_option("display.max_rows", None)

# set variables
devices = []
dataframe_list = []
output_list = []

#set commands variable
commands = ['vlan 2', 'name george']


#set connection payload function
def device_dict(ip:str):
    device = {
        "device_type" : "cisco_ios",
        "ip" : ip,
        "username" : "derive",
        "password" : "@Derive123",
        "secret" : "@Derive123"
    }
    return device

#initialize connection
net_connect = ConnectHandler(**device_dict(ip="192.168.193.191"))
net_connect.enable()
details = net_connect.send_command("show cdp neighbors detail", use_textfsm = True)


#loop through each device to get the ip address
for detail in details:
    if detail['management_ip'] and detail['management_ip'] not in devices and detail['management_ip'] != '10.40.1.1':
        devices.append(detail['management_ip'])
print(devices)
net_connect.disconnect()

for device in devices:
    net_connect = ConnectHandler(**device_dict(ip=device))
    net_connect.check_config_mode()
    net_connect.send_config_set(commands)
    net_connect.disconnect()
    print('done')
    # break



