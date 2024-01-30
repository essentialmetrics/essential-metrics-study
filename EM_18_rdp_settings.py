#!/usr/bin/env python
# EM-18 - High Vaule applications
# In this automation we will check weither RDP (3389) is enabled on the system
# We are gathering RDP session login data in the EM_20_admin_logins script as this was collected in the same eventID 4624

import pandas as pd
import json
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the RDP settings')
powershell_command = r'(Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections").fDenyTSConnections'
output = cf.run_powershell_command(powershell_command)


if output['output'] == '0':
    rdp_enabled = 'True'
else:
    rdp_enabled = 'False'

powershell_command = r'(Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "UserAuthentication").UserAuthentication'
output = cf.run_powershell_command(powershell_command)

# Network Level Authentication
if output['output'] == '1':
    nla_enabled = 'True'
else:
    nla_enabled = 'False'

powershell_command = 'Get-LocalGroupMember -Group "Remote Desktop Users" | convertto-json'
output = cf.run_powershell_command(powershell_command)

try:
    if output['output'] == '':
        users = []
    else:
        users = json.loads(output['output'])
except Exception as e:
    logger.error(f'Could not parse the user data from the Remote Desktop Users group command: {e}')

try:
    if isinstance(users, list):
        pass
    else:
        users = [users]
except Exception as e:
    logger.error(f'Could not convert Remote Desktop Users to list format')

for user in users:
  user['RDPUsers'] = 'Explicit'

powershell_command = 'Get-LocalGroupMember -Group "Administrators" | convertto-json'
output = cf.run_powershell_command(powershell_command)

try:
    if output['output'] == '':
        admins = []
    else:
        admins = json.loads(output['output'])
except Exception as e:
    logger.error(f'Could not parse the user data from the Remote Desktop Users group command: {e}')

try:
    if isinstance(admins, list):
        pass
    else:
        admins = [admins]
except Exception as e:
    logger.error(f'Could not convert Admins to list format')

for user in admins:
  user['RDPUsers'] = 'Administrator'

all_rdp_users = users + admins
data = [{'Name': user['Name'].split('\\')[-1], 'RDPUsers': user['RDPUsers']} for user in all_rdp_users]
df = pd.DataFrame(data)

df['RDPEnabled'] = rdp_enabled
df['NLAEnabled'] = nla_enabled

with DatabaseManager() as db:
    df.to_sql('em_18_rdp_enabled', db.conn, if_exists='append', index=False)

logger.info('Completed collecting the RDP settings')