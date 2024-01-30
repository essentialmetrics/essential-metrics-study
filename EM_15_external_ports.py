#!/usr/bin/env python
# EM-15 - External port scanning for open ports
# The script makes an external API call to https://api64.ipify.org to get the externally facing IP address for the network

import pandas as pd
import requests
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the external port scan data from the system')

try:
    # ipify is an open source public IP address API, see https://www.ipify.org/ for full details
    response = requests.get('https://api64.ipify.org?format=json')
    if response.status_code == 200:
        EXTERNAL_IP = response.json()['ip']
    else:
        logger.error(f"Could not get external IP address of system: {response.status_code}")
        sys.exit(1)
except Exception as e:
    logger.error(f"There was an error in the external API call to return the IP address: {e}")
    sys.exit(1)

logger.info(f'Validating the external IP is a single hop away')
powershell_command = f'Test-Connection -ComputerName {EXTERNAL_IP} -Count 1 -TimeToLive 1 -Quiet'
output = cf.run_powershell_command(powershell_command)

try:
    if output['output'] == "True":
        logger.info(f'The external IP address is a single hop away running scan against it')
        scan=True
    else:
        logger.info(f'The external IP address is NOT a single hop away exiting')
        sys.exit(1)
except Exception as e:
    logger.error(f'Could not determine if external IP was a single hop away, exiting script: {e}')
    sys.exit(1)

external_scan = cf.nmap_scan(EXTERNAL_IP, arguments='-T4 -sV -O')
assets_found, all_os_matches = cf.sort_port_scan_data(external_scan)

try:
    df = pd.DataFrame(assets_found[0][6])
    if df.empty:
        df = pd.DataFrame(columns=['mac', 'ip', 'port', 'state', 'reason', 'name', 'product', 'version', 'extrainfo', 'conf', 'cpe'])
        df.loc[0] = [assets_found[0][0], assets_found[0][1], '', '', '', '', '', '', '', '', '']
    else:
        df.insert(0, 'ip', assets_found[0][1])
        df.insert(0, 'mac', assets_found[0][0])
        df['port'] = df['port'].astype(int)
except Exception as e:
    logger.error(f'Could not convert the nmap scan of the external IP to usable dataframe: {e}')
    sys.exit(1)

with DatabaseManager() as db:
    df.to_sql('em_15_external_ports', db.conn, if_exists='append', index=False)
    logger.info(f'Successfully updated the em_15_external_ports table')