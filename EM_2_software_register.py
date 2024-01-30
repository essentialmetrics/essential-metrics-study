#!/usr/bin/env python
# EM-2 - Software register
# In this automation if we cannot find an install date for the software we are creating an install date 5 years in the past

import pandas as pd
import json
from datetime import datetime, timedelta
import sys

import utils.common_functions as cf
from utils.logger_config  import configure_logger
from utils.database_class import DatabaseManager

logger = configure_logger(__name__)

logger.info(f'Gathering software register data')

with DatabaseManager() as db:
    logger.info("Getting the latest event timestamp from the database if it exists")
    db.execute_query('SELECT MAX(timestamp) FROM app_install_date;')
    app_install_date = db.cursor.fetchone()[0]

def update_install_date(cell_value):
    '''
    This function will update the cell value if it is None to a date 5 years in the past
    '''
    try:
        if cell_value is None:
            today = datetime.now().strftime("%Y%m%d")
            app_install_date_datetime = datetime.strptime(app_install_date, "%Y%m%d")
            today_datetime = datetime.strptime(today, "%Y%m%d")
            if today_datetime > app_install_date_datetime:
                return(today)
            else:
                five_years_ago = datetime.now() - timedelta(days=365*5)
                logger.debug(f'Returning 5 years ago as the install date as we are initalizing the database: {five_years_ago.strftime("%Y%m%d")}')
                return five_years_ago.strftime("%Y%m%d")
        else:
            return cell_value
    except Exception as e:
        logger.error(f'Could not update cell value with old date, exiting automation as bad data will break the dashboard: {e}')
        sys.exit(1)

powershell_command = (
    'Get-ChildItem "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall", '
    '"HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall", '
    '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall", '
    '"HKLM:\\SOFTWARE\\Classes\\Installer\\Products"'
    '-ErrorAction SilentlyContinue | '
    'Get-ItemProperty | '
    'Where-Object { $_.DisplayName -ne $null } | '
    'ForEach-Object { '
        '[PSCustomObject]@{'
            'Publisher = $_.Publisher; '
            'DisplayName = $_.DisplayName; '
            'DisplayVersion = $_.DisplayVersion; '
            'InstallDate = $_.InstallDate '
        '} '
    '}  | convertto-json'
)

output = cf.run_powershell_command(powershell_command)
if output['output'] != '':
    try:
        installed_software = json.loads(output['output'])
    except Exception as e:
        logger.error(f'Could not convert the returned software into json compliant format: {e}')
        sys.exit(1)

df = pd.DataFrame(installed_software)

try:
    df.sort_values(by=['Publisher', 'DisplayName', 'DisplayVersion', 'InstallDate'], ascending=[True, True, True, False], inplace=True, na_position='last')
    df = df.drop_duplicates(subset=['Publisher', 'DisplayName', 'DisplayVersion'], keep='first')
except Exception as e:
    logger.error(f'Could not drop duplicates from the software frame, continuing on: {e}')

# import pdb; pdb.set_trace()

df['InstallDate'] = df['InstallDate'].apply(update_install_date)


'''
for index, row in df.iterrows():
    if row.isna().any():
        logger.debug(f"Row {index}:")
        logger.debug(row)
'''
with DatabaseManager() as db:
    db.add_new_rows('em_2_software_register', df, ['Publisher', 'DisplayName', 'DisplayVersion'])
    db.remove_old_rows('em_2_software_register', df, ['Publisher', 'DisplayName', 'DisplayVersion'])

logger.info(f'Finished gathering software register data')