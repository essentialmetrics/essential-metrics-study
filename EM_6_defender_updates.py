#!/usr/bin/env python
# EM-6 - Ensure Automatic defender updates are enabled and working as expected
# https://learn.microsoft.com/en-us/mem/intune/user-help/turn-on-defender-windows
# https://learn.microsoft.com/en-us/previous-versions/windows/desktop/defender/msft-mpcomputerstatus#properties

# # https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus?view=o365-worldwide#windows-defender-antivirus-client-error-codes

import pandas as pd
import json

import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info(f'Getting the defender settings and scan times')
powershell_command = 'Get-MpComputerStatus | Select-Object -Property AMServiceEnabled, AMRunningMode, AntispywareEnabled, AntispywareSignatureAge, AntispywareSignatureLastUpdated, AntivirusEnabled, AntivirusSignatureAge, AntivirusSignatureLastUpdated, BehaviorMonitorEnabled, DefenderSignaturesOutOfDate, FullScanAge, FullScanRequired, IoavProtectionEnabled, IsTamperProtected, NISEnabled, NISSignatureAge, NISSignatureLastUpdated, OnAccessProtectionEnabled, QuickScanEndTime, QuickScanOverdue, RealTimeProtectionEnabled, RebootRequired | convertto-json'
output = cf.run_powershell_command(powershell_command)

try:
    df = pd.DataFrame([json.loads(output['output'])])
except Exception as e:
    logger.error(f'Could not load dataframe from returned controlled folders: {e}')
    
try:
    df['AntispywareSignatureLastUpdated'] = df['AntispywareSignatureLastUpdated'].apply(cf.convert_windows_timestamp)
    df['AntivirusSignatureLastUpdated'] = df['AntivirusSignatureLastUpdated'].apply(cf.convert_windows_timestamp)
    df['NISSignatureLastUpdated'] = df['NISSignatureLastUpdated'].apply(cf.convert_windows_timestamp)
    df['QuickScanEndTime'] = df['QuickScanEndTime'].apply(cf.convert_windows_timestamp)
except Exception as e:
    logger.info(f'There was an error in the time conversion, returning EPOC: {e}')
    df['AntispywareSignatureLastUpdated'] = '1970-01-01 00:00:00'
    df['AntivirusSignatureLastUpdated'] = '1970-01-01 00:00:00'
    df['NISSignatureLastUpdated'] = '1970-01-01 00:00:00'
    df['QuickScanEndTime'] = '1970-01-01 00:00:00'

with DatabaseManager() as db:
    df.to_sql('em_6_defender_updates', db.conn, if_exists='append', index=False)

logger.info(f'Finished processing defender settings')