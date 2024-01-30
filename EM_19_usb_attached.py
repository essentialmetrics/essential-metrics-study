#!/usr/bin/env python
# EM-19 - Find all attached USBs
# For this automation we are using the public USB ID database: http://www.linux-usb.org/usb.ids
# This has been downloaded as it is very small, we are using this as a lookup table to find the Vendor and Product associated with the attached USB devices

import pandas as pd
import json
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info(f'Getting the attached USB devices on the system')


def parse_document(document):
    data = {}
    current_vendor = None
    
    for line in document.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        
        if not line.startswith('\t'):
            # Vendor line
            vendor_key, vendor_name = line.split(maxsplit=1)
            current_vendor = vendor_key
            data[current_vendor] = {'name': vendor_name}
        
        else:
            # Device line
            if current_vendor is not None:
                device_key, device_name = line.strip().split(maxsplit=1)
                data[current_vendor][device_key] = device_name
    return data

try:
    with open('C:\\opt\\essential-metrics\\assets\\usb.ids', 'r', encoding='cp1252') as file:
        document = file.read()
        parsed_data = parse_document(document)
except Exception as e:
    logger.error(f'Could not open usb.ids database for further processing')

def lookup(data, vendor_key, device_key=None):
    if vendor_key in data:
        if device_key:
            return data[vendor_key].get(device_key)
        else:
            return data[vendor_key]['name']
    return None


powershell_command = r'''
$registryPath = 'HKLM:\SYSTEM\ControlSet001\Enum\USB'
$results = New-Object System.Collections.ArrayList 

Get-ChildItem -Path $registryPath | Where-Object { $_.Name -match '\\V' } | ForEach-Object {
    $subKeyPath = $_.Name
    # Extract VID
    $vidValue = if ($subKeyPath -match 'VID_([0-9A-Fa-f]{4})') {
        $matches[1]
    } else {
        "XXXX"
    }
    # Extract PID
    $pidValue = if ($subKeyPath -match 'PID_([0-9A-Fa-f]{4})') {
        $matches[1]
    } else {
        "XXXX"
    }

    $subkeys = Get-ChildItem -Path "Registry::$subKeyPath"
    foreach ($subkey in $subkeys) {
        $KeyPath = $subkey.Name
        $properties = Get-ItemProperty -Path "Registry::$KeyPath" -ErrorAction SilentlyContinue

        $result = [PSCustomObject]@{
            Vid = $vidValue
            Pid = $pidValue
            Service = $properties.Service
            #HardwareID = $properties.HardwareID
            #DeviceDesc = $properties.DeviceDesc
            LocationInformation = $properties.LocationInformation
        }

        [void]$results.Add($result)
    }
}
$results | ConvertTo-Json
'''

usb_attached = cf.run_powershell_command(powershell_command)
usb_devices = json.loads(usb_attached['output'])


unique_dict = {}

for item in usb_devices:
    vid_pid_key = (item['Vid'], item['Pid'])
    if vid_pid_key in unique_dict:
        if item['Service'] is not None:
            if unique_dict[vid_pid_key]['Service'] is None:
                unique_dict[vid_pid_key]['Service'] = item['Service']
            else:
                unique_dict[vid_pid_key]['Service'] += ", " + item['Service']
        if item['LocationInformation'] is not None:
            if unique_dict[vid_pid_key]['LocationInformation'] is None:
                unique_dict[vid_pid_key]['LocationInformation'] = item['LocationInformation']
            else:
                unique_dict[vid_pid_key]['LocationInformation'] += ", " + item['LocationInformation']
    else:
        # Add a new entry to the dictionary
        unique_dict[vid_pid_key] = item

usb_devices_processed = list(unique_dict.values())

for device in range(0, len(usb_devices_processed)):
    usb_devices_processed[device] = { 'Product': lookup(parsed_data, usb_devices_processed[device]['Vid'].lower(), usb_devices_processed[device]['Pid'].lower()), **usb_devices_processed[device] }
    usb_devices_processed[device] = { 'Vendor': lookup(parsed_data, usb_devices_processed[device]['Vid'].lower()), **usb_devices_processed[device] }

df = pd.DataFrame(usb_devices_processed)

with DatabaseManager() as db:
    db.add_new_rows('em_19_usb_devices', df, list(df.keys()))


# Find USB policy and add it to the database
powershell_command = r'''
function Get-RegistryValues {
    param (
        [string]$path
    )
    $result = @()
    $key = Get-Item -Path $path -ErrorAction SilentlyContinue
    if ($key -ne $null) {
        $keyInfo = [PSCustomObject]@{
            Path  = $path
            Values = @()
            Subkeys = @()
        }
        $key.GetValueNames() | ForEach-Object {
            $valueName = $_
            $valueData = $key.GetValue($_)
            $valueObject = [PSCustomObject]@{
                Name = $valueName
                Data = $valueData
            }
            $keyInfo.Values += $valueObject
        }
        $key.GetSubKeyNames() | ForEach-Object {
            $subkeyPath = "$path\$_"
            $subkeyResult = Get-RegistryValues -path $subkeyPath
            if ($subkeyResult) {
                $keyInfo.Subkeys += $subkeyResult
            }
        }

        $result += $keyInfo
    }

    return $result
}

Get-RegistryValues -path "HKLM:\Software\Policies\Microsoft\Windows\DeviceInstall\Restrictions" | ConvertTo-Json -Depth 100
'''

output = cf.run_powershell_command(powershell_command)

if output['output'] == '':
    logger.info(f'USB policy is not set, finished gathering metrics on USB devices')
    sys.exit(0)
usb_policy = json.loads(output['output'])

def flatten_policy(policy, result=None, parent_path=''):
    if result is None:
        result = []
        
    path = policy['Path']
    for value in policy['Values']:
        result.append({'Path': path, 'Name': value['Name'], 'Data': value['Data']})
        
    for subkey in policy['Subkeys']:
        flatten_policy(subkey, result, path)
        
    return result

flattened_data = flatten_policy(usb_policy)
df = pd.DataFrame(flattened_data)

with DatabaseManager() as db:
    db.add_new_rows('em_19_usb_policy', df, list(df.keys()))

logger.info(f'Finished gathering metrics on USB devices')