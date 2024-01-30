#!/usr/bin/env python
# EM-9 - Track all controlled folders and state of the setting
# https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/enable-controlled-folders?view=o365-worldwide
# https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/customize-controlled-folders?view=o365-worldwide

import pandas as pd
import json
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info(f'Getting the controlled folder access settings')
powershell_command = 'Get-MpPreference | Select-Object -Property EnableControlledFolderAccess, ControlledFolderAccessProtectedFolders | ConvertTo-Json'
output = cf.run_powershell_command(powershell_command)

try:
    df = pd.DataFrame(json.loads(output['output']), index=[0])
except Exception as e:
    logger.error(f'Could not load dataframe from returned controlled folders: {e}')

with DatabaseManager() as db:
    db.add_new_rows('em_9_controlled_folder_access', df, list(df.keys()), single_row=True)