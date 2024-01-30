#!/usr/bin/env python
# EM-12 - gather reboot analysis metrics from time of patch to time of reboot

'''
System Events:
Event ID: 1074      Source: User32              Reason: A system reboot/ shutdown has been requested or initiated
Event ID: 12        Source: Kernel-General      Reason: Kernel version parameters in boot message

Status codes for 1074:
0x80020002          Planned system reboot is necessary to complete application patching (system initiated)
0x80020003          Planned system reboot is necessary to complete OS upgrade patching (system initiated)
0x80020010          Planned system reboot is necessary to complete service pack patching (system, initiated)
0x500ff             Unknown shutdown 
0x0                 User initiated restart
'''

import pandas as pd
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the reboot data')

result = None

with DatabaseManager() as db:
    logger.info("Getting the latest event timestamp from the database if it exists")
    db.execute_query("SELECT MAX(TimeGenerated) AS TimeGenerated FROM ( SELECT TimeGenerated FROM em_12_kernel_versions UNION ALL SELECT TimeGenerated FROM em_12_reboot_analysis );")
    result = db.cursor.fetchone()[0]

if result is not None:
    logger.info(f'Using {result} timestamp that we got from the database as the latest timestamp for our events collected')
    query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile='System' AND ( EventCode=1074 OR EventCode=12 ) AND TimeGenerated >= '{result}'"
else:
    logger.info("No timestamp found in the database, getting all events")
    query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='System' AND ( EventCode=1074 OR EventCode=12 )"


wql_r = cf.run_wmi_query(query)
reboot_events = []
kernel_versions = []

try:
    for event in wql_r:
        if getattr(event, "EventCode") == 1074:
            Process = getattr(event, "InsertionStrings")[0]
            Reason = getattr(event, "InsertionStrings")[2]
            Status = getattr(event, "InsertionStrings")[3]
            Power = getattr(event, "InsertionStrings")[4]
            User = getattr(event, "InsertionStrings")[6]
            EventCode = getattr(event, "EventCode")
            TimeGenerated = getattr(event, "TimeGenerated")
            reboot_events.append([Process, Reason, Status, Power, User, EventCode, TimeGenerated])
        elif getattr(event, "EventCode") == 12:
            if getattr(event, "Category") != 1:
                continue
            MajorVersion = getattr(event, "InsertionStrings")[0]
            MinorVersion = getattr(event, "InsertionStrings")[1]
            BuildVersion = getattr(event, "InsertionStrings")[2]
            QfeVersion = getattr(event, "InsertionStrings")[3]
            ServiceVersion = getattr(event, "InsertionStrings")[4]
            BootMode = getattr(event, "InsertionStrings")[5]
            StartTime = getattr(event, "InsertionStrings")[6]
            EventCode = getattr(event, "EventCode")
            TimeGenerated = getattr(event, "TimeGenerated")
            kernel_versions.append([MajorVersion, MinorVersion, BuildVersion, QfeVersion, ServiceVersion, BootMode, StartTime, EventCode, TimeGenerated])
except Exception as e:
    logger.error(f'Failed to parse the WMI reboot data: {e}')
    sys.exit(1)


try:
    df = pd.DataFrame(reboot_events, columns=['Process', 'Reason', 'Status', 'Power', 'User', 'EventCode', 'TimeGenerated'])

    with DatabaseManager() as db:
        db.add_new_rows('em_12_reboot_analysis', df, ['Process', 'Reason', 'Status', 'Power', 'User', 'EventCode', 'TimeGenerated'])
except Exception as e:
    logger.error(f'Could not add the reboot times to the database: {e}')

try:
    df = pd.DataFrame(kernel_versions, columns=['MajorVersion', 'MinorVersion', 'BuildVersion', 'QfeVersion', 'ServiceVersion', 'BootMode', 'StartTime', 'EventCode', 'TimeGenerated'])
    with DatabaseManager() as db:
        db.add_new_rows('em_12_kernel_versions', df, ['MajorVersion', 'MinorVersion', 'BuildVersion', 'QfeVersion', 'ServiceVersion', 'BootMode', 'StartTime', 'EventCode', 'TimeGenerated'])
except Exception as e:
    logger.error(f'Could not add the reboot times to the database: {e}')


logger.info('Collection of the vulnerability patching data complete')