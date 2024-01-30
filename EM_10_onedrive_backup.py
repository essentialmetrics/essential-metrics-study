#!/usr/bin/env python
# EM-10 - Backup Syncing
# For this automation we are tracking two of the most popular backup solutions:
# Microsoft Onedrive as it is inbuilt with the OS install
# Google Drive as many users already have a google email address

# https://winbuzzer.com/2020/07/24/how-to-onedrive-folder-sync-any-directory-via-mklink-xcxwbt/#:~:text=mklink%20is%20a%20Windows%20command%20that%20lets%20users,makes%20Windows%20think%20its%20contents%20are%20actually%20there.
# https://learn.microsoft.com/en-us/sharepoint/redirect-known-folders

'''
KfmFoldersProtectedNow:
0:      No folders configured
512:    Desktop only
1024:   Documents only
2048:   Pictures only

1536:   Desktop & Documents
2560:   Desktop & Pictures
3072:   Documents & Pictures
3584:   Documnets & Desktop & Pictures
'''

import json
import pandas as pd
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the backup data for microsoft OneDrive')

powershell_command = r'''
$registryPath = "HKLM:\SOFTWARE\Microsoft\Security Center\Provider\CBP"
$subkeys = Get-ChildItem -Path $registryPath

$results = foreach ($subkey in $subkeys) {
    $properties = Get-ItemProperty -Path $subkey.PSPath -ErrorAction SilentlyContinue

    if ($properties -ne $null -and $properties.DISPLAYNAME -like "OneDrive*") {
        [PSCustomObject]@{
            Namespace = $properties.NAMESPACE
            AccountName = $properties.ACCOUNTNAME
            UserSID = $properties.USERSID
            RestoreUrl = $properties.RESTOREURL
        }
    }
}

$results | ConvertTo-Json
'''
output = cf.run_powershell_command(powershell_command)

try:
    if output['output'] == '':
        microsoft_backup_settings = []
    else:
        microsoft_backup_settings = json.loads(output['output'])
except Exception as e:
    logger.error(f'Could not parse the user data from the Remote Desktop Users group command: {e}')

try:
    if isinstance(microsoft_backup_settings, list):
        pass
    else:
        microsoft_backup_settings = [microsoft_backup_settings]
except Exception as e:
    logger.error(f'Could not convert Admins to list format')

# Get the latest GUID from the backup settings, this changes with a new backup timestamp
if len(microsoft_backup_settings) > 1:
    microsoft_backup_settings = microsoft_backup_settings[-1]

if len(microsoft_backup_settings) == 0:
    logger.info(f'Microsoft OneDrive is not configured for Ransomeware protection, exiting automation')
    
    data = {
        'AccountName': ['NotConfigured'],
        'UserFolder': [''],
        'KfmFoldersProtectedNow': [''],
        'LastKnownFolderBackupTime': ['000000000'],
        'LastKnownSettingsChange': [''],
        'RestoreUrl': ['']
    }
    df = pd.DataFrame(data)
    with DatabaseManager() as db:
        db.add_new_rows('em_10_onedrive_enabled', df, list(df.keys()), single_row=True)
    sys.exit(0)
else:
    logger.info(f'Microsoft OneDrive is configured for Ransomeware protection, gathering backup metrics')


powershell_command = f'''
$properties = Get-ItemProperty -Path "Registry::HKEY_USERS\\{microsoft_backup_settings[0]['UserSID']}\\SOFTWARE\\Microsoft\\OneDrive\\Accounts\\"
$properties.LastUpdate
'''
last_settings_update = cf.run_powershell_command(powershell_command)

powershell_command = f'''
$registryPath = "Registry::HKEY_USERS\\{microsoft_backup_settings[0]["UserSID"]}\\SOFTWARE\\Microsoft\\OneDrive\\Accounts\\"
$subkeys = Get-ChildItem -Path $registryPath

$results = foreach ($subkey in $subkeys) {{
    $properties = Get-ItemProperty -Path $subkey.PSPath -ErrorAction SilentlyContinue

    [PSCustomObject]@{{
        SubkeyName = $subkey.PSChildName
        UserFolder = $properties.UserFolder
        KfmFoldersProtectedNow = $properties.KfmFoldersProtectedNow
        LastKnownFolderBackupTime = $properties.LastKnownFolderBackupTime
    }}
}}

$results | ConvertTo-Json
'''

backup_settings = cf.run_powershell_command(powershell_command)

try:
    # The output here is for both "Business1" and "Personal" accounts, as we are not targeting business users in our study we are just gathering the Personal data from this reg key
    # The SubkeyName was left in code here to easily convert this to track business users if necessary
    # The Business account would be returned in [0]
    backup_settings = json.loads(backup_settings['output'])[1]
except Exception as e:
    logger.error(f'Could not parse the OneDrive Backup data: {e}')
    sys.exit(1)

try:
    backup_settings.pop('SubkeyName', None)
    backup_settings = {'AccountName': f'{microsoft_backup_settings[0]["AccountName"]}', **backup_settings}
    backup_settings['LastKnownSettingsChange'] = last_settings_update['output']
    backup_settings['RestoreUrl'] = microsoft_backup_settings[0]['RestoreUrl']
except Exception as e:
    logger.error(f'Could not combine all elements of the backup metric data: {e}')
    sys.exit(1)

try:
    df = pd.DataFrame([backup_settings])
    with DatabaseManager() as db:
        db.add_new_rows('em_10_onedrive_enabled', df, list(df.keys()), single_row=True)
    logger.info(f'Microsoft OneDrive backup metrics collected, exiting')
except Exception as e:
    logger.error(f'Could not add data to dataframe and push to database: {e}')