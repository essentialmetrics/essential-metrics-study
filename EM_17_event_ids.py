#!/usr/bin/env python
# EM-17 - App to External IP mapping
# In this automation we are going to collect the start and stop time of system PIDs
# We are then going to use them in coolorabation with the firewall logs and track which of our applications are making external calls
# In this automation we will create a table full with process start and stop times

'''
system events:
12:       System startup
4688:     Process Creation
4689:     Process Termination
'''

import wmi
import re
import pandas as pd
import numpy as np
import psutil
import utils.common_functions as cf
from utils.logger_config  import configure_logger
import datetime
logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the process IDs and matching them up')

# We first need to check if the process audit policy is enabled as this will not work without that

powershell_command = '''
$Process = auditpol /get /subcategory:"Process Creation"
if ($Process -like "*Success*") {$True} else {$False}
'''
output = cf.run_powershell_command(powershell_command)
data = {'CreateEnabled': f'{output["output"]}'}

powershell_command = '''
$Process = auditpol /get /subcategory:"Process Termination"
if ($Process -like "*Success*") {$True} else {$False}
'''

output = cf.run_powershell_command(powershell_command)
data['TerminationEnabled'] = f'{output["output"]}'

for key, value in data.items():
    if value == 'False':
        logger.error(f"{key} is set to False, enabling the audit policy again")
        powershell_command = '''
        auditpol /set /subcategory:"Process Creation" /success:enable /failure:disable
        auditpol /set /subcategory:"Process Termination" /success:enable /failure:disable
        '''
        cf.run_powershell_command(powershell_command)

df = pd.DataFrame([data])
with DatabaseManager() as db:
    df.to_sql('em_17_pid_tracking_enabled', db.conn, if_exists='append', index=False)

# Get the PIDS and match them up

with DatabaseManager() as db:
    logger.info("Getting the latest event timestamp from the database if it exists")
    db.execute_query("SELECT * FROM em_17_last_event_timestamp ORDER BY timestamp DESC LIMIT 1")
    result = db.cursor.fetchone()

if result is not None:
    try:
        epoc_timestamp = result[0]
        timestamp_seconds = int(epoc_timestamp) / 1_000_000_000  # Convert nanoseconds to seconds
        timestamp_datetime = datetime.datetime.fromtimestamp(timestamp_seconds, tz=datetime.timezone.utc)
        last_timestamp = timestamp_datetime.strftime('%Y%m%d%H%M%S.%f') + '-000'
        logger.info(f"Using the timestamp returned from the database to query for new events: {last_timestamp}")
    except Exception as e:
       logger.error(f'Failed to get timestamp from the database and convert it for query')
else:
    logger.info("No timestamp found in the database, using the last reboot time for our timestamp")
    wmi_o = wmi.WMI('.')
    wql = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='System' AND EventCode=12"
    result_set = wmi_o.query(wql)
    
    # Sort the result set by TimeGenerated in descending order
    sorted_result_set = sorted(result_set, key=lambda event: event.TimeGenerated, reverse=True)
    
    if sorted_result_set:
        last_timestamp = sorted_result_set[0].TimeGenerated  # The first item in the sorted result set is the latest event
        logger.info(f'Using timestamp: {last_timestamp} for our event query')
    else:
        logger.debug("No matching events found, Getting all events from the event log")


if not last_timestamp:
   query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4688 OR EventCode=4689)"
else:
   query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile='Security' AND (EventCode=4688 OR EventCode=4689) AND TimeGenerated >= '{last_timestamp}'"


logger.debug(f'Running a query for 4688 and 4689 events from the security log')
wmi_a = wmi.WMI('.')
wql_r = wmi_a.query(query)

formatted_list = []

for l in wql_r:
  event_id = getattr(l, 'EventIdentifier')
  if event_id == 4688:
    pid = int(getattr(l, 'InsertionStrings')[4], 16)
    application = getattr(l, 'InsertionStrings')[5]
    process_cli = getattr(l,'Message')
    pattern = r'Process Command Line:(.*?)Token Elevation'
    match = re.search(pattern, process_cli, re.DOTALL)
    # Remove the wrapper characters from the CLI string lines
    process_cli = match.group(1)[1:-4]
    if process_cli == '\t\r\n\r\n':
       process_cli = ''
  else:
    pid = int(getattr(l, 'InsertionStrings')[5], 16)
    application = getattr(l, 'InsertionStrings')[6]
    process_cli = ''
  TimeGenerated = getattr(l, 'TimeGenerated')[:-4]
  event = [event_id, pid, application, process_cli,  TimeGenerated]
  formatted_list.append(event)


column_names = ['event', 'pid', 'application', 'process_cli', 'Timestamp']

df = pd.DataFrame(formatted_list, columns=column_names)

df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y%m%d%H%M%S.%f')
df = df.sort_values('Timestamp', ascending=True)

last_timestamp = df['Timestamp'].tail(1).values[0]
epoc_timestamp = np.datetime64(last_timestamp).astype(datetime.datetime)


with DatabaseManager() as db:
    query = "SELECT * FROM em_17_running_pids"
    database_running_pids = pd.read_sql_query(query, db.conn)

database_running_pids['Timestamp'] = pd.to_datetime(database_running_pids['Timestamp'], format='%Y%m%d%H%M%S.%f')

# Fix the formatting
# database_running_pids['Timestamp'] = pd.to_datetime(database_running_pids['Timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
# database_running_pids['Timestamp'] = database_running_pids['Timestamp'].dt.strftime('%Y%m%d%H%M%S.%f')

# database_running_pids['Timestamp'] = pd.to_datetime(database_running_pids['Timestamp'], format='%Y%m%d%H%M%S.%f')
# database_running_pids['Timestamp'] = pd.to_datetime(database_running_pids['Timestamp'], format='%Y%m%d%H%M%S.%f')

logger.debug(f'Merging past running pids and current running pids')
df = pd.concat([df, database_running_pids], ignore_index=True)

calculated_dataframe = []
completed_pid_list = []
running_pid_list = []

def completed_pid(df, completed_pid_list):
  '''
  This function will match up a start and end time of a PID that has completed and add it too the list completed_pid in this format
  [pid, application, process_cli, start_time, end_time, time_diff]
  '''
  # logger.debug(f"Found matching PID start and stop times for: {df['application'].unique()[0]} Adding to database")
  try:
    start_time = df.loc[df['event'] == 4688, 'Timestamp'].values[0]
    end_time = df.loc[df['event'] == 4689, 'Timestamp'].values[0]
    time_diff = df.loc[df['event'] == 4689, 'Timestamp'].values[0] - df.loc[df['event'] == 4688, 'Timestamp'].values[0]
    completed_pid_list.append([df['pid'].unique()[0], df['application'].unique()[0], df['process_cli'].unique()[0], start_time, end_time, time_diff])
  except Exception as e:
     logger.debug(f"The completed_pid function failed while processing {df['application'].unique()[0]} with error: {e}\n\nDataframe is: {df}")


def running_pid(df, running_pid_list):
  '''
  This function will add the running pids to our global list in this format:
  [event, pid, application, start_time, end_time, time_diff]
  '''
  #logger.info(f"Inside single running_pid function")
  try:
    if df['event'] != 4688:
      logger.info(f'Process orphaned, not adding to database')
      return
    else:
      running_pid_list.append([df['event'], df['pid'], df['application'], df['process_cli'],  df['Timestamp'].strftime('%Y%m%d%H%M%S.%f')])
      return
  except:
     logger.debug(f"The running_pid function failed while processing {df['application']}")

PIDS = df['pid'].unique()

# Add a try except block here

# This block is quiet complex but necessary, one of the issues we have is dealing with multiple PIDs of the same number 
# This happens after a reboot when all the old PIDs are shutdown and the new PIDs start with the same number
# To get around this issue we are querying the application column and if there are multiple application columns with the same PID we are sorting them and taking the closest two together to be a matching pair

logger.debug(f'Matching up the 4688 event ID with its associated closing 4689 event ID')
try:
  for pid in PIDS:
    # print(f'Running against PID {pid}')
    pid_df = df.loc[df['pid'] == pid]
    # print(f"The row number is: {len(pid_df)}")
    if len(pid_df) == 1:
      running_pid(pid_df.iloc[0], running_pid_list)
    if len(pid_df) >= 2:
      APPLICATIONS = pid_df.loc[pid_df['pid'] == pid]['application'].unique()
      for app in APPLICATIONS:
        # print(f"The number of apps with this pid is: {pid_df.loc[pid_df['application'] == app]}")
        if len(pid_df.loc[pid_df['application'] == app]) == 1:
          running_pid(pid_df.iloc[0], running_pid_list)
        if len(pid_df.loc[pid_df['application'] == app]) == 2:
          completed_pid(pid_df.loc[pid_df['application'] == app], completed_pid_list)
        if len(pid_df.loc[pid_df['application'] == app]) > 2:
          sorted_app = pid_df.loc[pid_df['application'] == app]
          while len(sorted_app) > 0:
            # logger.debug(sorted_app.iloc[:2])
            unique_pid_app = sorted_app.iloc[:2]
            if len(unique_pid_app) > 1:
              completed_pid(unique_pid_app, completed_pid_list)
            else:
              # logger.debug(f'Adding this pid to the still running pids: {unique_pid_app.iloc[0]}')
              running_pid(unique_pid_app.iloc[0], running_pid_list)
            sorted_app = sorted_app.iloc[2:]
except Exception as e:
   logger.debug(f'Matching pids function failed with error: {e}')

# Getting a current list of all running pids

def get_running_pids():
    # Get a list of all running processes and their information
    process_list = psutil.process_iter(attrs=['pid', 'name'])
    running_pids = []
    
    for process in process_list:
        try:
            pid = process.info['pid']
            running_pids.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return running_pids


# Remove the non running PIDs from the dataframe that does not have any currently running.

pids = get_running_pids()
still_running = [item[1] for item in running_pid_list]
matching_pids = [pid for pid in pids if pid in still_running]
active_pids = [sub_list for sub_list in running_pid_list if sub_list[1] in pids]

logger.debug(f'There were {len(running_pid_list)} pids in the database before the active pid process and {len(active_pids)} pids after')

column_names = ['event', 'pid', 'application', 'process_cli', 'Timestamp']
df_running_pids = pd.DataFrame(active_pids, columns=column_names)

with DatabaseManager() as db:
    df_running_pids.to_sql('em_17_running_pids', db.conn, if_exists='replace', index=False)

column_names = ['pid', 'application', 'process_cli', 'start_time', 'end_time', 'duration']
df_completed_pids = pd.DataFrame(completed_pid_list, columns=column_names)
logger.debug(f'Writing {len(df_completed_pids)} pids into the completed_pids table')

with DatabaseManager() as db:
    df_completed_pids.to_sql('em_17_completed_pids', db.conn, if_exists='append', index=False)

with DatabaseManager() as db:
    db.execute_write('em_17_last_event_timestamp', [epoc_timestamp])