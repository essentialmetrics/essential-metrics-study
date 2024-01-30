#!/usr/bin/env python

# This script will manage EM-3 and collect the firewall rules and save them in the essential-metrics database.
# We first need to validate the firewall is enabled or our application will not work.
# https://support.microsoft.com/en-us/windows/risks-of-allowing-apps-through-windows-defender-firewall-654559af-3f54-3dcf-349f-71ccd90bcc5c

# Check windows advanced firewall before completeing automation.

import pandas as pd
import json
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

powershell_command = 'Get-NetFirewallProfile | convertto-csv | ConvertFrom-Csv | ConvertTo-Json'
output = cf.run_powershell_command(powershell_command)

data_list = json.loads(output['output'])

firewall_profiles = {}
for d in data_list:
    firewall_profiles[d['Profile']] = d['Enabled']

df = pd.DataFrame(list(firewall_profiles.items()), columns=['Profile', 'Enabled'])
with DatabaseManager() as db:
    df.to_sql('em_3_firewall_enabled', db.conn, if_exists='append', index=False)

if any(df['Enabled'] == 'False'):
    logger.error("There is at least one firewall deactivated value under the 'Enabled' column, enabling it now.")
    try:
        cf.run_powershell_command('Set-NetFirewallProfile -Enabled True')
    except Exception as e:
        logger.error(f'Could not enable the firewall, Error: {e}')


logger.info(f'Getting all firewall rules on the system')
powershell_command = 'Get-NetFirewallRule | Select-Object Name, DisplayName, Description, DisplayGroup, Enabled, Profile, Direction, Action, EdgeTraversalPolicy, Owner | ConvertTo-Csv | ConvertFrom-Csv | ConvertTo-Json'
output = cf.run_powershell_command(powershell_command)

try:
    df = pd.DataFrame(json.loads(output['output']))
except Exception as e:
    logger.error(f'Could not load dataframe from returned enabled services: {e}')

with DatabaseManager() as db:
    db.add_new_rows('em_3_firewall_rules', df, ['Name', 'DisplayName', 'Description', 'DisplayGroup', 'Enabled', 'Profile', 'Direction', 'Action', 'EdgeTraversalPolicy', 'Owner'])
    db.remove_old_rows('em_3_firewall_rules', df, ['Name', 'DisplayName', 'Description', 'DisplayGroup', 'Enabled', 'Profile', 'Direction', 'Action', 'EdgeTraversalPolicy', 'Owner'])