#!/usr/bin/env python
# EM-14 - Ensure Threat scanning is working as expected

import pandas as pd
import json
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the thread scan data from the system')
powershell_command = 'Get-MpThreatDetection | Select-Object -Property DetectionID, ActionSuccess,DomainUser,InitialDetectionTime,LastThreatStatusChangeTime,ProcessName,RemediationTime,Resources | convertto-json'
output = cf.run_powershell_command(powershell_command)

try:
    df = pd.DataFrame(json.loads(output['output']))
except Exception as e:
    logger.error(f'Could not load dataframe from returned threat detection: {e}')

try:
    df['InitialDetectionTime'] = df['InitialDetectionTime'].apply(cf.convert_windows_timestamp)
    df['LastThreatStatusChangeTime'] = df['LastThreatStatusChangeTime'].apply(cf.convert_windows_timestamp)
    df['RemediationTime'] = df['RemediationTime'].apply(cf.convert_windows_timestamp)
except Exception as e:
    logger.info(f'There was an error in the time conversion, returning EPOC: {e}')
    df['InitialDetectionTime'] = '1970-01-01 00:00:00'
    df['LastThreatStatusChangeTime'] = '1970-01-01 00:00:00'
    df['RemediationTime'] = '1970-01-01 00:00:00'


try:
    df = df.map(cf.convert_dataframe_list_to_string)
except Exception as e:
    logger.error(f'Could not convert the list to string format, exiting as we cannot add lists to the database: {e}')
    sys.exit(1)

df = df.drop_duplicates()
df = df.astype(str)

with DatabaseManager() as db:
    db.add_new_rows('em_14_threat_scanning', df, list(df.keys()))
    
logger.info(f'Finished processing threat detection')