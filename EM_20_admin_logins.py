#!/usr/bin/env python
# EM-20 - Admin Logins
# In this automation we are going to track elevated privilage logins to the system
# We are capturing all elevated logins here but we may only present a subset of the user elevated cretentials as SYSTEM makes a lot of elevated calls

# https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types
# This is useful for other recommended monitoring from Microsoft:
# https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624

'''
Event IDs captured by this automation (https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/basic-audit-logon-events)
4624 	A user successfully logged on to a computer. For information about the type of logon, see the Logon Types table below.
4625 	Logon failure. A logon attempt was made with an unknown user name or a known user name with a bad password.
4634 	The logoff process was completed for a user.
4647    A user has successfully logged off
4648 	A user successfully logged on to a computer using explicit credentials while already logged on as a different user.
4779 	A user disconnected a terminal server session without logging off.

Logon type captured
2 	Interactive 	A user logged on to this computer.
3 	Network 	A user or computer logged on to this computer from the network.
4 	Batch 	Batch logon type is used by batch servers, where processes may be executing on behalf of a user without their direct intervention.
5 	Service 	A service was started by the Service Control Manager.
7 	Unlock 	This workstation was unlocked.
8 	NetworkCleartext 	A user logged on to this computer from the network. The user's password was passed to the authentication package in its unhashed form. The built-in authentication packages all hash credentials before sending them across the network. The credentials do not traverse the network in plaintext (also called cleartext).
9 	NewCredentials 	A caller cloned its current token and specified new credentials for outbound connections. The new logon session has the same local identity, but uses different credentials for other network connections.
10 	RemoteInteractive 	A user logged on to this computer remotely using Terminal Services or Remote Desktop.
11 	CachedInteractive 	A user logged on to this computer with network credentials that were stored locally on the computer. The domain controller was not contacted to verify the credentials.
'''

import pandas as pd
import sys
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the user login session data')

# First we need to track if the audit policies are still configured because if they are not we will not get back any useful data
# Patching reverts the audit policies if the Microsoft version has been been purchased which you will see in VMWare when testing with vinalla installs of Microsoft Windows

powershell_command = '''
$Process = Auditpol /get /subcategory:"Logon"
if ($Process -like "*Success*") {$True} else {$False}
'''
output = cf.run_powershell_command(powershell_command)
data = {'LogonEnabled': f'{output["output"]}'}

powershell_command = '''
$Process = Auditpol /get /subcategory:"Logoff"
if ($Process -like "*Success*") {$True} else {$False}
'''

output = cf.run_powershell_command(powershell_command)
data['LogoffEnabled'] = f'{output["output"]}'

for key, value in data.items():
    if value == 'False':
        logger.error(f"{key} is set to False, enabling the audit policy again")
        powershell_command = '''
        Auditpol /set /subcategory:"Logon" /success:enable /failure:enable
        Auditpol /set /subcategory:"Logoff" /success:enable /failure:disable
        '''
        cf.run_powershell_command(powershell_command)

df = pd.DataFrame([data])
with DatabaseManager() as db:
    df.to_sql('em_20_logon_audit_tracking_enabled', db.conn, if_exists='append', index=False)

# Now we are getting the events and adding them to the database
result = None

with DatabaseManager() as db:
    logger.info("Getting the latest event timestamp from the database if it exists")
    db.execute_query("SELECT MAX(TimeGenerated) FROM em_20_admin_logins;")
    result = db.cursor.fetchone()[0]

if result is not None:
    logger.info(f'Using {result} timestamp that we got from the database as the latest timestamp for our events collected')
    query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4624 OR EventCode=4625 OR EventCode=4634 OR EventCode=4647 OR EventCode=4648 OR EventCode=4779) AND TimeGenerated >= '{result}'"
else:
    try:
        logger.info("No timestamp found in the database, using the last reboot time for our timestamp")
        wql = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='System' AND EventCode=12"
        result_set = cf.run_wmi_query(wql)
        # Sort the result set by TimeGenerated in descending order
        sorted_result_set = sorted(result_set, key=lambda event: event.TimeGenerated, reverse=True)
        if sorted_result_set:
            last_timestamp = sorted_result_set[0].TimeGenerated  # The first item in the sorted result set is the latest event
            logger.info(f'Using timestamp: {last_timestamp} for our login event query')
            query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4624 OR EventCode=4625 OR EventCode=4634 OR EventCode=4647 OR EventCode=4648 OR EventCode=4779) AND TimeGenerated >= '{last_timestamp}'"
        else:
            logger.debug("No matching events found, Getting all events from the event log")
            query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4624 OR EventCode=4625 OR EventCode=4634 OR EventCode=4647 OR EventCode=4648 OR EventCode=4779)"
    except Exception as e:
        logger.error(f'Could not use the reboot or database timestamp, getting all events in the event log: {e}')
        query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4624 OR EventCode=4625 OR EventCode=4634 OR EventCode=4647 OR EventCode=4648 OR EventCode=4779)"

logger.debug(f'Running a query for 4625 and 4624 and 4634 events from the security log')
wql_r = cf.run_wmi_query(query)

def get_process_name(event, string):
    message = getattr(event, 'Message')
    lines = message.split('\n')
    try:
        for line in lines:
            if string in line:
                return(line.split(f'{string}:')[-1].strip())
    except Exception as e:
        return('')

login_events = []

try:
    for event in wql_r:
        ElevatedToken=''
        if getattr(event, "EventIdentifier") == 4624:
            Uid = getattr(event, "InsertionStrings")[4]
            User = getattr(event, "InsertionStrings")[5]
            LogonType = getattr(event, "InsertionStrings")[8]
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[7]
            Process = getattr(event, "InsertionStrings")[17]
            ElevatedToken = get_process_name(event, 'Elevated Token')
            SourceAddress = getattr(event, "InsertionStrings")[18]
            SourcePort = getattr(event, "InsertionStrings")[19]
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4779:
            Uid = getattr(event, "InsertionStrings")[4]
            User = getattr(event, "InsertionStrings")[5]
            LogonType = getattr(event, "InsertionStrings")[8]
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[7]
            Process = getattr(event, "InsertionStrings")[17]
            ElevatedToken = get_process_name(event, 'Elevated Token')
            SourceAddress = getattr(event, "InsertionStrings")[18]
            SourcePort = getattr(event, "InsertionStrings")[19]
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4634:
            Uid = getattr(event, "InsertionStrings")[0]
            User = getattr(event, "InsertionStrings")[1]
            LogonType = getattr(event, "InsertionStrings")[4]
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[3]
            Process = ''
            SourceAddress = ''
            SourcePort = ''
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4625:
            Uid = getattr(event, "InsertionStrings")[4]
            User = getattr(event, "InsertionStrings")[5]
            LogonType = getattr(event, "InsertionStrings")[10]
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[7]
            Process = getattr(event, "InsertionStrings")[18]
            SourceAddress = getattr(event, "InsertionStrings")[19]
            SourcePort = getattr(event, "InsertionStrings")[20]
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4647:
            Uid = getattr(event, "InsertionStrings")[0]
            User = getattr(event, "InsertionStrings")[1]
            LogonType = 'Logoff'
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[3]
            Process = ''
            SourceAddress = ''
            SourcePort = ''
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4625:
            Uid = getattr(event, "InsertionStrings")[4]
            User = getattr(event, "InsertionStrings")[5]
            LogonType = 'Explicit password'
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[10]
            Process = getattr(event, "InsertionStrings")[11]
            SourceAddress = getattr(event, "InsertionStrings")[12]
            SourcePort = getattr(event, "InsertionStrings")[13]
            TimeGenerated = getattr(event, "TimeGenerated")
        elif getattr(event, "EventIdentifier") == 4648:
            Uid = getattr(event, "InsertionStrings")[6]
            User = getattr(event, "InsertionStrings")[5]
            LogonType = 'Explicit password'
            EventIdentifier = getattr(event, "EventIdentifier")
            RecordNumber = getattr(event, "RecordNumber")
            LogonID = getattr(event, "InsertionStrings")[3]
            Process = getattr(event, "InsertionStrings")[11]
            SourceAddress = getattr(event, "InsertionStrings")[12]
            SourcePort = getattr(event, "InsertionStrings")[13]
            TimeGenerated = getattr(event, "TimeGenerated")
        else:
            logger.error(f'Got event back that was not queried: {getattr(event, "EventIdentifier")}')
        login_events.append([RecordNumber, Uid, User, LogonType, EventIdentifier, LogonID, ElevatedToken, Process, SourceAddress, SourcePort, TimeGenerated])
except Exception as e:
    logger.error(f'There was an error processing the returned WMI data: {e}')

try:
    columns = ['RecordNumber', 'Uid', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'Process', 'SourceAddress', 'SourcePort', 'TimeGenerated']
    df = pd.DataFrame(login_events, columns=columns)
except Exception as e:
    logger.error(f'Could not convert list of events into pandas dataframe')
    sys.exit(1)

with DatabaseManager() as db:
    db.add_new_rows('em_20_admin_logins', df, columns)

logger.info(f'Finished processing user session login data')