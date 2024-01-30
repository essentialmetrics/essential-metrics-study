#!/usr/bin/env python
# EM-17 - App to External IP mapping
# In this automation we use the tabled created by the EM_17_event_ids automation and match them up to the firewall logs so we can see what applications are making external calls

import pandas as pd
import numpy as np
import datetime
import pandas as pd
import pytz
from tzlocal import get_localzone

from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

df_completed_pids = []
df_running_pids = []
combined_df = []

# Read all the completed pids
with DatabaseManager() as db:
    # Execute a query to list all tables
    query = "SELECT * FROM em_17_completed_pids"
    df_completed_pids = pd.read_sql_query(query, db.conn)

# Read all the running pids
with DatabaseManager() as db:
    # Execute a query to list all tables
    query = "SELECT * FROM em_17_running_pids"
    df_running_pids = pd.read_sql_query(query, db.conn)

# Normalize the dataframes so they can be merged
df_running_pids['Timestamp'] = pd.to_datetime(df_running_pids['Timestamp'], format='%Y%m%d%H%M%S.%f')
df_running_pids.rename(columns={'Timestamp': 'start_time'}, inplace=True)

# Combine the two tables
combined_df = pd.concat([df_completed_pids, df_running_pids], ignore_index=True)
combined_df.reset_index(drop=True, inplace=True)


# Normalize the timeformat and sort in ascending order
combined_df['start_time'] = pd.to_datetime(combined_df['start_time'])
combined_df['end_time'] = pd.to_datetime(combined_df['end_time'])
event_pids = combined_df.sort_values('start_time', ascending=True)


log_file_path = r'C:\Windows\System32\LogFiles\Firewall\pfirewall.log'
column_names = ['date', 'time', 'action', 'protocol', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'size', 'tcp_flags', 'tcp_syn', 'tcp_ack', 'tcp_win', 'icmp_type', 'icmp_code', 'info', 'path', 'pid']

try:
  with open(log_file_path, 'r') as file:
    logger.info(f'Reading the firewall logs to check what applications are reaching out externally')
    lines = file.readlines()[5:]
except Exception as e:
    logger.debug(f'There was an issue reading the firewall logs: {e}')

try:
  data = [string.split() for string in lines]
  df_network = pd.DataFrame(data, columns=column_names)
except Exception as e:
   logger.error(f'Failed to create a dataframe from the returned firewall log file')


df_network['datetime'] = pd.to_datetime(df_network['date'] + ' ' + df_network['time'])
df_network.drop(columns=['date', 'time'], inplace=True)
df_network['pid'] = pd.to_numeric(df_network['pid'], errors='coerce', downcast='integer')



# Convert the 'datetime' column from CST to UTC
local_timezone = get_localzone()
utc = pytz.timezone('UTC') 
df_network['datetime'] = df_network['datetime'].dt.tz_localize(local_timezone).dt.tz_convert(utc)


# df_network['pid'] = pd.to_numeric(df_network['pid'], errors='coerce', downcast='integer')

PIDS = df_network['pid'].unique()

event_pids['start_time'] = event_pids['start_time'].dt.tz_localize(utc).dt.tz_convert(utc)
event_pids['end_time'] = event_pids['end_time'].dt.tz_localize(utc).dt.tz_convert(utc)


# Get the latest timestamp from the firewall log table

with DatabaseManager() as db:
    logger.info("Getting the latest event timestamp from the database if it exists")
    db.execute_query("SELECT * FROM em_17_firewall_logs_timestamp ORDER BY timestamp DESC LIMIT 1")
    result = db.cursor.fetchone()

logger.debug(f'The dataframe is {len(df_network)}')


if result is not None:
    # Assuming there is only one column in the result
    try:
        epoc_timestamp = result[0]
        timestamp_datetime = datetime.datetime.fromtimestamp(epoc_timestamp, tz=datetime.timezone.utc)
        logger.info(f"Using the timestamp returned from the database to query for new events: {timestamp_datetime}")
    except Exception as e:
        logger.debug(f'There was an error setting the timestamp in the firewall log files')
    try:
        logger.debug(f'Removing the log lines from the firewall dataframe')
        df_network = df_network[df_network["datetime"] > timestamp_datetime]
    except Exception as e:
        logger.debug(f'There was an error removing the log lines from the firewall dataframe')
else:
    logger.info('There was no timestamp found so processing all firewall log lines')


logger.debug(f'The dataframe is {len(df_network)}')

firewall_applications = []

# This function needs changed so that the end time PIDS are also covered this only currently catches completed PIDs
for index, row in df_network.iterrows():
    # print(f"The event is: {row['src-ip']}")
    # It was this before below
    # event_pids[(event_pids['pid'] == row['pid']) & (event_pids['start_time'] <= row['datetime']) & (event_pids['end_time'] >= row['datetime'])]
    df = event_pids[(event_pids['pid'] == row['pid']) & (event_pids['start_time'] <= row['datetime'])]
    
    if len(df) !=0:
        if (event_pids['end_time'] >= row['datetime']).any() or (event_pids['event'] == 4688).any():
            # print(f'Match found: {df}')
            firewall_applications.append([row['action'], row['protocol'], row['src_ip'], row['dst_ip'], row['src_port'], row['dst_port'], row['size'], row['path'], row['datetime'], df['pid'].values[0], df['application'].values[0], df['process_cli'].values[0]])
        # print(f'df is: {df["pid"]}')
        #break
        
column_names = ['action', 'protocol', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'size', 'path', 'datetime', 'pid', 'application', 'process_cli']
firewall_logs = pd.DataFrame(firewall_applications, columns=column_names)

with DatabaseManager() as db:
    firewall_logs.to_sql('em_17_firewall_logs', db.conn, if_exists='append', index=False)

with DatabaseManager() as db:
    db.execute_write('em_17_firewall_logs_timestamp', [df_network["datetime"].max().timestamp()])