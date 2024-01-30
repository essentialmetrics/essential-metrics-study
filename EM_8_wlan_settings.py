#!/usr/bin/env python
# EM-8 - Track WLAN settings

import pandas as pd
import zxcvbn
import sys

import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the WLAN settings')

powershell_command = r'''
    $list = (netsh.exe wlan show profiles) -match '\s{2,}:\s' | ForEach-Object { $_ -replace '.*:\s', '' }
    $profileData = @()
    foreach ($profile in $list) {
        $data = netsh.exe wlan show profile name="$profile" key=clear | Select-String -Pattern "Authentication", "SSID name", "Cipher", "Network type", "Connection mode", "Key Content"
        $profileData += $data
    }
    $profileData
'''
output = cf.run_powershell_command(powershell_command)

try:
    lines = output['output'].split('\n')
except Exception as e:
    logger.error(f'Could not split output from powershell command: {e}')
    sys.exit(1)

try:
    structured_data = []
    current_data = {}
    for line in lines:
        if line.strip().startswith('Connection mode'):
            if current_data:
                structured_data.append(current_data)
                current_data = {}
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            current_data[key] = value
    if current_data:
        structured_data.append(current_data)
except Exception as e:
    logger.info(f'Could not parse the returned powershell WLAN settings: {e}')
    sys.exit(1)

try:
    df = pd.DataFrame(structured_data)
except Exception as e:
    logger.error(f'Could not load dataframe from returned controlled folders: {e}')
    sys.exit(1)

try:
    df['PasswordStrength'] = None
    df['Feedback'] = None
    df['Suggestions'] = None
    for index, row in df.iterrows():
        strength = zxcvbn.zxcvbn(row['Key Content'])
        if strength['score'] == 0:
            password_strength='Weakest'
        elif strength['score'] == 1:
            password_strength='Weak'
        elif strength['score'] == 2:
            password_strength='Medium'
        elif strength['score'] == 3:
            password_strength='Strong'
        elif strength['score'] == 4:
            password_strength='Strongest'
        df.at[index, 'Key Content'] = '********'
        df.at[index, 'PasswordStrength'] = password_strength
        df.at[index, 'Feedback'] = strength['feedback']['warning']
        df.at[index, 'Suggestions'] = strength['feedback']['suggestions']
    df.rename(columns={'Connection mode': 'ConnectionMode', 'SSID name': 'SSIDName', 'Network type': 'NetworkType', 'Key Content': 'KeyContent'}, inplace=True)
except Exception as e:
    logger.error(f'There was an error formatting the WIFI password settings: {e}')
    df['PasswordStrength'] = None
    df['Feedback'] = None
    df['Suggestions'] = None
    df['Key Content'] = '********'
    df.rename(columns={'Connection mode': 'ConnectionMode', 'SSID name': 'SSIDName', 'Network type': 'NetworkType', 'Key Content': 'KeyContent'}, inplace=True)

try:
    df = df.map(cf.convert_dataframe_list_to_string)
except Exception as e:
    logger.error(f'Could not convert the list to string format, exiting as we cannot add lists to the database: {e}')
    sys.exit(1)

with DatabaseManager() as db:
    db.add_new_rows('em_8_wlan_settings', df, list(df.keys()))
    logger.info('WLAN settings successfully written to database')