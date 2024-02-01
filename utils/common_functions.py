# These are common functions used by many different python scripts

import subprocess
import sys
import nmap
import time
import os
import wmi
from scapy.all import ARP, Ether, srp
from datetime import datetime

from .logger_config import configure_logger
from .database_class import DatabaseManager


logger = configure_logger(__name__)

# We need to add this as the SYSTEM user does not have this in their PATH
os.environ['PATH'] = f"{os.environ['PATH']};C:\\Program Files (x86)\\Nmap"


def run_subprocess_command(command: str) -> str:
    """
    Run a shell command and return the output as a string.

    :param command: The shell command to run.
    :return: The command's output as a string, or an empty string if an error occurs.
    """
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running subprocess command '{command}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error running subprocess command '{command}': {e}")
        sys.exit(1)


def popen_subprocess_command(command: str) -> None:
    """
    Run a shell command in a new process, typically used for launching applications.

    :param command: The shell command to run.
    :return: None. Outputs from the command are not captured or returned.
    """
    try:
        subprocess.Popen(command, shell=True)
        logger.info(f"Successfully ran command: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running subprocess command '{command}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error running subprocess command '{command}': {e}")
        sys.exit(1)
    

def run_powershell_command(powershell_command: str):
    """
    Runs a PowerShell command and returns the result.
    
    :param powershell_command: The command to run.
    :return: A dictionary with 'success', 'output' and 'error' keys.
    """
    logger.debug(f'Running the mpowershell command: {powershell_command}')
    result = {
        'success': False,
        'output': '',
        'error': ''
    }
    
    try:
        completed_process = subprocess.run(['powershell', '-Command', powershell_command], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE, 
                                           text=True)
        
        result['output'] = completed_process.stdout.strip()
        logger.debug(f'Return code is: {completed_process}')
        if completed_process.returncode != 0:
            result['error'] = completed_process.stderr.strip()
        else:
            result['success'] = True
    
    except Exception as e:
        logger.error(f'There was an issue with the powershell command: {powershell_command}, the error was: {e}')
        result['error'] = str(e)
    
    return result


def run_wmi_query(query):
    '''
    This will interact with the Windows Management Interface API and run queries against it.
    Inputs:
        query: This is the query used against the WMI
    Returns:
        wql_r: windows query launguage response from the WMI
    '''
    try:
        wmi_a = wmi.WMI('.')
        wql_r = wmi_a.query(query)
        return wql_r
    except Exception as e:
        logger.error(f"An error occurred while executing the WMI query: {str(e)}, the query was: {query}")
        sys.exit(1)


def convert_windows_timestamp(timestamp_str):
    '''
    This will convert the windows timestamp format of: '/Date(1703172658904)/'
    And convert it into a UTC human readable format: %Y-%m-%d %H:%M:%S
    '''
    if timestamp_str is None:
        return(timestamp_str)
    try:
        timestamp_ms = int(timestamp_str.strip('/Date()'))
        timestamp = timestamp_ms / 1000.0
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        logger.info(f'There was an error in the datetimestamp conversion, returning EPOC, error: {e} ')
        return '1970-01-01 00:00:00'
    except Exception as e:
        logger.info(f'There was an error in the datetimestamp conversion, returning EPOC, error: {e} ')
        return '1970-01-01 00:00:00'


def convert_dataframe_list_to_string(cell_value):
    try:
        if isinstance(cell_value, list):
            return ', '.join(map(str, cell_value))
        else:
            return cell_value
    except Exception as e:
        logger.error(f'Could not parse list to string, wrapping the entire cointents')
        return(f'{cell_value}')


def check_data_freshness(table, days=7):
    '''
    This function will check the database table to validate the freshness of the data.
    The function will cleanly exit if there is fresh data in the database.
    We can use this to only update tables when we pass the data freshness threshold.
    Inputs:
        table: This is the database table to validate against
        days: This is how many days previous we need to check for fresh data
        '''

    with DatabaseManager() as db:
        logger.info(f'Getting the latest event timestamp for: {table} from the database if it exists')
        db.execute_query(f'SELECT MAX(created_at) FROM {table};')
        result = db.cursor.fetchone()[0]

    if result:
        result_date = datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
        current_date = datetime.now()

        date_difference = current_date - result_date
        if date_difference.days <= days:
            logger.info(f'The data in {table} is still fresh: {result}, exiting cleanly and waiting for next run to update table.')
            sys.exit(0)
        else:
            logger.info(f'The data in {table} is not fresh: {result}, continuing with data collection.')
    else:
        logger.info(f'The data in {table} is not fresh: {result}, continuing with data collection.')


################# All below functions are used by and for nmap scanning and processing ###################

def nmap_scan(subnets, arguments='-sn'):
    '''
    This function will manage the nmap scan and control error handling
    '''
    try:
        logger.info(f'Scanning the IP or subnet with arguments: {arguments}')
        nm = nmap.PortScanner()
        scan = nm.scan(hosts=subnets, arguments=arguments)
        return scan['scan']
    except Exception as e:
        logger.error(f'The nmap scan failed with subnets and arguments: {arguments} with error: {e}')
        sys.exit(1)


def run_arp_sweep(ip_or_subnet, return_type='all'):
    '''
    This function will broadcast an arp request to the subnet and get the list of IP and MACs that are active and responding on the subnet.
    If a single IP address is given it will ask the subnet who has the associated MAC address and return a single MAC
    '''
    try:
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, pdst=ip_or_subnet)
        answered, unanswered = srp(arp_request, timeout=1, verbose=False)
    except Exception as e:
        logger.error(f'Could not run an ARP broadcast of the {ip_or_subnet} address')
    
    if return_type == 'all':
        arp_sweep = {}
        try:
            for sent, received in answered:
                logger.debug(f"IP: {received.psrc} - MAC: {received.hwsrc} received from the ARP broadcast")
                arp_sweep[received.psrc] = received.hwsrc
            return(arp_sweep)
        except Exception as e:
            logger.error('There was an error getting data from the ARP broadcast output: {e}')
            return(ip_or_subnet)
    if return_type == 'mac':
        for attempt in range(3):
            try:
                for sent, received in answered:
                    logger.debug(f"IP: {received.psrc} - MAC: {received.hwsrc} received from the ARP broadcast")
                    return(received.hwsrc)
                break
            except Exception as e:
                logger.info('There was an error getting data from the ARP request, retrying {e}')
                if attempt < 3:
                    time.sleep(1)
                    continue
                else:
                    logger.error('There was an error getting data from the ARP request, returning IP address: {ip_or_subnet}')
                    return(ip_or_subnet)


def get_os_matches(MAC, IP, osmatch):
    '''
    This function will get all the returned OS matches for the nmap scanned host
    It will return a list of all the potential OS matches that were found by nmap
    '''
    logger.debug(f'Getting the OS matches for: {MAC}')
    os_matches = []
    try:
        for os in range(0, len(osmatch)):
            NAME = osmatch[os]['name']
            ACCURACY = osmatch[os]['accuracy']
            if osmatch[os].get('osclass'):
                for osclass in range(0, len(osmatch[os]['osclass'])):
                    VENDOR = osmatch[os]['osclass'][osclass]['vendor']
                    OS_FAMILY = osmatch[os]['osclass'][osclass]['osfamily']
                    OS_GEN = osmatch[os]['osclass'][osclass]['osgen']
                    ACCURACY = osmatch[os]['osclass'][osclass]['accuracy']
                    CPE = " ".join(osmatch[os]['osclass'][osclass]['cpe'])
                    os_matches.append([MAC, IP, NAME, VENDOR, OS_FAMILY, OS_GEN, ACCURACY, CPE])
            else:
                VENDOR = ''
                OS_FAMILY = ''
                OS_GEN = ''
                ACCURACY = ''
                CPE = ''
            os_matches.append([MAC, IP, NAME, VENDOR, OS_FAMILY, OS_GEN, ACCURACY, CPE])
    except Exception as e:
        logger.debug(f'Failed to correctly get the OS matches for: {MAC}, returning empty list')
        return([])
    return(os_matches)


def sort_port_scan_data(port_scan_results):
    '''
    This will get the interesting data from the returned port scan so we can add it into the database
    '''
    assets_found = []
    all_os_matches = []
    
    try:
        for ip in port_scan_results.keys():
            if 'mac' in port_scan_results[ip]['addresses']:
                MAC = port_scan_results[ip]['addresses']['mac']
            else:
                logger.debug(f"MAC not found during nmap scan for: {port_scan_results[ip]['addresses']['ipv4']}, running ARP scan to get it")
                try:
                    MAC = run_arp_sweep(port_scan_results[ip]['addresses']['ipv4'], return_type='mac').upper()
                except Exception as e:
                    logger.debug(f'Could not get the MAC with an ARP sweep, this is usually because of a VM')
                    MAC = port_scan_results[ip]['addresses']['ipv4']
            if 'vendor' in port_scan_results[ip]:
                vendor_values = list(port_scan_results[ip]['vendor'].values())
                if vendor_values:
                    vendor_info = vendor_values[0]
                else:
                    vendor_info = ''
            else:
                vendor_info = ''
            if 'tcp' in port_scan_results[ip]:
                try:
                    open_ports = []
                    for port in port_scan_results[ip]['tcp'].keys():
                        ports = {'port': port, **port_scan_results[ip]['tcp'][port]}
                        open_ports.append(ports)
                except Exception as e:
                    logger.error(f'There was an issue getting the ports back from the scan: {e}')
            else:
                open_ports = []

            all_os_matches.extend(get_os_matches(MAC, port_scan_results[ip]['addresses']['ipv4'], port_scan_results[ip]['osmatch']))

            if 'osmatch' in port_scan_results[ip]:
                try:
                    if port_scan_results[ip].get('osmatch'):
                        OS = port_scan_results[ip]['osmatch'][0]['name']
                        ACCURACY = port_scan_results[ip]['osmatch'][0]['accuracy']
                        CPE = port_scan_results[ip]['osmatch'][0]['osclass'][0]['cpe'][0]
                    else:
                        OS = ''
                        ACCURACY = ''
                        CPE = ''
                except Exception as e:
                    logger.debug(f"Could not parse the OS information from the returned nmap scan: {e}\n\n{port_scan_results[ip]['osmatch']}")
            assets_found.append([MAC, port_scan_results[ip]['addresses']['ipv4'], vendor_info, OS, ACCURACY, CPE, open_ports])
    except Exception as e:
        logger.error(f'Could not successfully parse the nmap scanned data, we hit this error: {e}')
        logger.error(f'Passing back partial data from any that were successfully parsed')
    
    return(assets_found, all_os_matches)