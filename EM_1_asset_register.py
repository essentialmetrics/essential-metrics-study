#!/usr/bin/env python
# EM-1 - Hardware asset register collection, this script will use nmap to scan the internal network for all assets on the default subnet that windows is connected too
# EM-16 - This automation will also collect internal open ports and add that to our database for tracking

import socket
import subprocess
import re
import ipaddress
import pandas as pd
from scapy.all import ARP, Ether, srp

import utils.common_functions as cf
from utils.logger_config import configure_logger

logger = configure_logger(__name__)
from utils.database_class import DatabaseManager

def get_default_gateway():
    '''
    This function will get the default gateway from the routing table
    '''
    try:        
        # Use the 'route print' command to retrieve the routing table
        result = subprocess.check_output(["route", "print"], shell=True).decode("utf-8")
        
        # Use regular expressions to find the IPv4 default gateway address
        pattern = r'0.0.0.0\s+0.0.0.0\s+(\d+\.\d+\.\d+\.\d+)\s+\d+'
        match = re.search(pattern, result)
        
        if match:
            gateway = match.group(1)
            return gateway
    except Exception as e:
        logger.error(f"Could not get default gateway from the route table: {e}")
        return None


def get_ip():
    '''
    This will get the primary IP of the windows desktop machine
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.168.1.1', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_all_subnets(ipconfig):
    '''
    This function will find all subnets that are currently attached to this target machine and return a list of the subnets
    '''
    ipv4 = [line for line in ipconfig if ("IPv4 Address" in line) or ("Subnet Mask" in line)]
    
    parsed_addresses = []
    
    for line in ipv4:
        processed_address = line.split(': ')[1].replace('\r', '')
        parsed_addresses.append(processed_address)
    
    ipv4_routes = {}
    
    # Iterate through the parsed addresses in pairs
    for i in range(0, len(parsed_addresses), 2):
        ip = parsed_addresses[i]
        subnet_mask = parsed_addresses[i + 1]
        
        # Create IPv4 objects from the IP address and subnet mask strings
        # ip_address = ipaddress.IPv4Address(ip)
        subnet = ipaddress.IPv4Network(f'{ip}/{subnet_mask}', strict=False)
        
        # Print the calculated subnet
        ipv4_routes[ip] = str(subnet)
        print(f'IP Address: {ip}, Subnet: {subnet}')
    
    all_subnets = ' '.join(list(ipv4_routes.values()))
    return(all_subnets)


def get_primary_subnet(ipconfig, default_gateway):
    '''
    This function will get the primary subnet connected to the computer and return the subnet as a string
    '''
    try:
        ipv4 = [line for line in ipconfig if ("IPv4 Address" in line) or ("Subnet Mask" in line) or ("Default Gateway" in line)]
    except Exception as e:
        logger.debug(f'There was an error generating the list of IP addresses and subnets from the ifconfig output')
    
    # Iterate through the list and find the target IP address then get its subnet mask
    logger.info(f'Getting the default subnet that is connected to this computer')
    try:
        for i in range(len(ipv4)):
            if default_gateway + '\r' in ipv4[i]:
                logger.debug(f'Found IP Address as the defaul gateway: {ipv4[i]}')
                if i <= len(ipv4):
                    default_subnet = ipv4[i - 1].split(': ')[1].replace('\r', '')
                    logger.debug(f'Found the preceding subnet for the default_gateway: {default_subnet}')
                else:
                    logger.error(f'The default route of: {default_gateway} was not found in the returned list.\n\n{ipv4}')
                break
    except Exception as e:
        logger.error(f'There was an error getting the {default_gateway} from the for loop: {e}')
    try:
        subnet = ipaddress.IPv4Network(f'{default_gateway}/{default_subnet}', strict=False)
        return (str(subnet))
    except Exception as e:
        logger.error(f'There was an error calculating the subnet: {e}')


def scan_for_new_assets():
    '''
    This function will scan the default subnet for new assets
    '''
    default_gateway = get_default_gateway()
    ipconfig = cf.run_subprocess_command('ipconfig').split('\n')
    subnet = get_primary_subnet(ipconfig, default_gateway)
    subnet_sweep = cf.nmap_scan(subnet, arguments='-sn')
    
    try:
        port_scan = ""
        for key in subnet_sweep.keys():
            port_scan += subnet_sweep[key]['addresses']['ipv4'] + ' '
    except Exception as e:
        logger.error(f'Could not parse the returned nmap scan to get the list of IP addresses: {e}')
    
    port_scan_results = cf.nmap_scan(port_scan, arguments='-T4 -sV -O')
    return(port_scan_results)


def add_named_assets_to_database(assets_found):
    '''
    This will add our windows machine and our default gateway to our named asset register
    The named asset register is what our users will see and add too, we are going to add two known hosts as a prompt for them too add more
    '''
    default_gateway = get_default_gateway()
    windows_ip = get_ip()
    
    asset_table = []
    
    for device in range(0, len(assets_found)):
        asset_table.append(assets_found[device][0:6])
    
    named_assets = []
    
    named_assets = [sublist for sublist in asset_table if windows_ip in sublist or default_gateway in sublist]
    column_names = ['asset_name', 'mac', 'ip', 'vendor', 'os', 'confidence', 'cpe', 'notes']
    
    for sublist in named_assets:
        if default_gateway in sublist:
            sublist.insert(0, "Home Gateway")
        if windows_ip in sublist:
            sublist.insert(0, "Windows Desktop")
        sublist.append('')
    
    df = pd.DataFrame(named_assets, columns=column_names)
    
    with DatabaseManager() as db:
        db.add_new_rows('em_1_named_asset_register', df, ['mac'])
    

def add_internal_ports_to_database(assets_found):
    ports_open = pd.DataFrame()
    try:
        for asset in range(0, len(assets_found)):
            df = pd.DataFrame()
            df = pd.DataFrame(assets_found[asset][6])
            df.insert(0, 'ip', assets_found[asset][1])
            df.insert(0, 'mac', assets_found[asset][0])
            ports_open = pd.concat([ports_open, df], ignore_index=True)
    
        ports_open['port'] = ports_open['port'].astype(int)
    except Exception as e:
        logger.error(f'Could not add internal scan data to port dataframe: {e}')
        return
    
    with DatabaseManager() as db:
        db.add_new_rows('em_16_internal_ports', ports_open, ['mac', 'ip', 'port', 'state'])
        db.remove_old_rows('em_16_internal_ports', ports_open, ['mac', 'ip', 'port', 'state'])
    
    with DatabaseManager() as db:
        ports_open.to_sql('em_16_internal_ports_heatmap', db.conn, if_exists='append', index=False)


def add_assets_to_database(assets_found):
    try:
        df = pd.DataFrame([sublist[:6] for sublist in assets_found], columns=['mac', 'ip', 'vendor', 'os', 'confidence', 'cpe'])
        df.insert(0, 'asset_name', '')
        df['notes'] = ''
    except Exception as e:
        logger.error(f'Could not convert nmap scan into assets dataframe: {e}')
        
    with DatabaseManager() as db:
        db.add_new_rows('em_1_asset_register', df, ['mac'])


def add_os_matches_to_database(all_os_matches):
    try:
        logger.info(f'Adding the OS information to its database table')
        column_names = ['mac', 'ip', 'name', 'vendor', 'os_family', 'os_gen', 'accuracy', 'cpe']
        os_matches = pd.DataFrame(all_os_matches, columns=column_names)
    
        with DatabaseManager() as db:
            os_matches.to_sql('em_1_os_matches', db.conn, if_exists='replace', index=False)
    except Exception as e:
        logger.error(f'Could not add the os guess information to the database, dropping')


def run_port_scan():
    port_scan_results = scan_for_new_assets()
    assets_found, all_os_matches = cf.sort_port_scan_data(port_scan_results)
    add_internal_ports_to_database(assets_found)
    add_assets_to_database(assets_found)
    add_named_assets_to_database(assets_found)
    add_os_matches_to_database(all_os_matches)
    

if __name__ == "__main__":
    logger.info(f'Gathering asset register data')
    cf.check_data_freshness('em_16_internal_ports_heatmap', days=3)
    run_port_scan()
    logger.info(f'Finished gathering asset register data')