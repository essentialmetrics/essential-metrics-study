#!/usr/bin/env python
# EM-7 - Track users password policy
# https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/how-to-configure-security-policy-settings


import pandas as pd
import os
import sys
import tempfile
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

sec_policy = tempfile.NamedTemporaryFile(dir=r'C:\opt\essential-metrics', delete=False)
sec_policy_path = sec_policy.name
sec_policy.close()

try:
    with open(sec_policy_path, 'w') as f:
        logger.info('Getting the security policy settings')
        powershell_command = f'secedit /export /cfg {sec_policy_path}'
        output = cf.run_powershell_command(powershell_command)
except Exception as e:
    logger.error(f"Error: {e}")


def parse_inf_file(file_path):
    data = {}
    current_section = None
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                data[current_section] = {}
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                data[current_section][key.strip()] = value.strip()
    return data


try:
    parsed_data = parse_inf_file(sec_policy_path)
except Exception as e:
    logger.info(f'Reading the ini security policy file has failed with error: {e}')
    sys.exit(1)

try:
    df = pd.DataFrame([parsed_data['System Access']])
    df = df.filter(['MaximumPasswordAge', 'MinimumPasswordLength', 'PasswordComplexity', 'PasswordHistorySize', 'LockoutBadCount', 'RequireLogonToChangePassword', 'ForceLogoffWhenHourExpire', 'NewAdministratorName', 'NewGuestName', 'ClearTextPassword', 'LSAAnonymousNameLookup', 'EnableAdminAccount', 'EnableGuestAccount'])
except Exception as e:
    logger.error(f'Could not load dataframe from sec policy ini file: {e}')
    sys.exit(1)

os.remove(sec_policy_path)

with DatabaseManager() as db:
    db.add_new_rows('em_7_password_policy', df, list(df.keys()), single_row=True)

logger.info('Security policy settings successfully written to database')