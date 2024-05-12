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
commands = ['show cdp neighbors detail', 'show ip interface brief', 'show vlan brief', 'show vtp status', 'show vrrp all', 'show ip route', 'show spanning-tree detail', 'show run aaa',
            'show version', 'show running-config', 'show ip ospf neighbor']


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
neighbors = net_connect.send_command("show cdp neighbors")
details = net_connect.send_command("show cdp neighbors detail", use_textfsm = True)
devices.append("192.168.193.191")

#loop through each device to get the ip address
for detail in details:
    if detail['management_ip'] and detail['management_ip'] not in devices and detail['management_ip'] != '10.40.1.1':
        devices.append(detail['management_ip'])
print(devices)


#for each command loop through each device and run that command in order to create a dataframe & use the commands name as the excell file
for command in commands:
    print(command)
    if command != 'show ip ospf neighbor': 
        for device in devices:
            try:
                net_connect = ConnectHandler(**device_dict(ip=device))
                net_connect.enable()

                
                output = net_connect.send_command(command, use_textfsm = True)
                output_type = type(output)
                # print(output)
                
                #if the output data type is a list that means its a list of dictionaries. Append each dictionary to the dataframe list
                if isinstance(output, list):
                    for item in output:
                        #add the source device to the dictionary
                        item['source_device'] = device
                        dataframe_list.append(item)
                # If output datatype isn't a list then its a string. add it to the output list for further parsing
                else:
                    output_list.append(output)
                
                #disconnect from the ssh session after each command is run on each device to avoid errors
                net_connect.disconnect()
            #catch any exceptions   
            except Exception as e:
                print(f'error {e} command: {command} \n')

    elif command == 'show ip ospf neighbor': 
        for device in devices:
            if device == '192.168.193.190' or device == '192.168.193.191':
                try:
                    net_connect = ConnectHandler(**device_dict(ip=device))
                    net_connect.enable()

                    
                    output = net_connect.send_command(command, use_textfsm = True)
                    output_type = type(output)
                    # print(output)
                    
                    #if the output data type is a list that means its a list of dictionaries. Append each dictionary to the dataframe list
                    if isinstance(output, list):
                        for item in output:
                            #add the source device to the dictionary
                            item['source_device'] = device
                            dataframe_list.append(item)
                    # If output datatype isn't a list then its a string. add it to the output list for further parsing
                    else:
                        output_list.append(output)
                    
                    #disconnect from the ssh session after each command is run on each device to avoid errors
                    net_connect.disconnect()
                #catch any exceptions   
                except Exception as e:
                    print(f'error {e} command: {command} \n')
        
    
    #if the output is a list use pandas to create a dataframe and write it as an excell file then clear the dataframe list for the next iteration
    if output and isinstance(output, list):
        #create excel file to write into
        file_path = f'{command}.xlsx'
        df = pd.DataFrame(dataframe_list)
        df.to_excel(file_path, index=False)
        print('hello')
        print(df)
        dataframe_list = []
    
    #if the output isnt a list Create a separate configuration text file
    elif output:
        file_path = f'{command}.txt'
        for item in output_list:
            f = open(file_path, 'a')
            f.write(f'Source Device: {device} \n')
            f.write(f'{item} \n')
            f.close()
        print(output_list)
        output_list = []
        
    
    
    



# print(jn)