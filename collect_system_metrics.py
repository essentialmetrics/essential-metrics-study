#!/usr/bin/env python
# This automation is used to collect metrics for our study.
# This is the metrics that will be passed back and used for the study.

import hashlib
import pandas as pd
import winreg
import os
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Collecting study data from database')


def get_machine_guid():
    '''
    I need this function to salt values during our information Pseudonymization
    This will get the machine GUID which will not change for the machine, will be unique per subject and can be used to ensure there is no way to reverse the Pseudonymization
    '''
    registry_path = r"SOFTWARE\Microsoft\Cryptography"
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(registry_key, "MachineGuid")
    winreg.CloseKey(registry_key)
    return value

try:
    machine_guid = get_machine_guid()
except Exception as e:
    logger.error(f'The salt function has failed using backup salt')
    machine_guid = os.environ.get('COMPUTERNAME') + os.environ.get('USERNAME')


def hash_ssid(ssid):
    '''
    This function is used to hash PI string values so they are kept anonymous
    It will use the machine GUID as a salt value as this will not change and increases entropy for things than can be reversed such as MAC and IP addresses with hash tables
    '''
    pi = ssid + machine_guid
    return hashlib.sha256(pi.encode()).hexdigest()


def collect_aggregate_count(table, column='created_at'):
    '''
    This function will get the count of some resource in the table based on the date it was created or removed at
    Inputs:
        table: This is the metric table we wish to collect data from and push data into
    '''
    try:
        logger.info(f'Collecting {table} study metrics')
        with DatabaseManager() as db:
            df = db.read_database_table(table)
        df[column] = pd.to_datetime(df[column])
        df = df[column].dt.date.value_counts()
        df = df.reset_index()
        df.columns = ['created_at', 'count']
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows(table, df, list(df.keys()))
        
        logger.info(f'Finished collecting {table} study metrics')
    except Exception as e:
        logger.error(f'Could not collect {table} metrics: {e}')


def collect_table_subset(table, columns, tail=True):
    '''
    This will collect a subset of the columns and add the last record to the study-metrics database
    '''
    try:
        with DatabaseManager() as db:
            df = db.read_database_table(table)
            
        df = df[columns]
        
        if tail:
            with DatabaseManager(database_name='study-metrics.db') as db:
                df.tail(1).to_sql(table, db.conn, if_exists='append', index=False)
        else:
            with DatabaseManager(database_name='study-metrics.db') as db:
                df.to_sql(table, db.conn, if_exists='append', index=False)
        
    except Exception as e:
        logger.error(f'Could not collect table subset of metrics: {e}')


def collect_em_2_metrics():
    logger.info('Collecting EM 2 study metrics')
    try:
        with DatabaseManager() as db:
            installed_software = db.read_database_table('em_2_software_register')
            
        query = '''
            SELECT em_2_software_register_decommissioned.*
            FROM em_2_software_register_decommissioned
            LEFT JOIN em_2_software_register ON em_2_software_register_decommissioned.Publisher = em_2_software_register.Publisher AND em_2_software_register_decommissioned.DisplayName = em_2_software_register.DisplayName
            WHERE em_2_software_register.Publisher IS NULL AND em_2_software_register.DisplayName IS NULL;
        '''
        
        with DatabaseManager() as db:
            removed_software = pd.read_sql_query(query, db.conn)
        
        query = '''
            SELECT em_2_software_register_decommissioned.*
            FROM em_2_software_register_decommissioned
            INNER JOIN em_2_software_register 
            ON em_2_software_register_decommissioned.Publisher = em_2_software_register.Publisher AND em_2_software_register_decommissioned.DisplayName = em_2_software_register.DisplayName;
        '''
        with DatabaseManager() as db:
            updated_software = pd.read_sql_query(query, db.conn)
        
        data = {'installed': len(installed_software), 'decommissioned': len(removed_software), 'updated': len(updated_software)}
        df = pd.DataFrame(data, index=[0])
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            df.to_sql('em_2_software_register', db.conn, if_exists='append', index=False)
        
        logger.info('Finished collecting EM 2 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 2 metrics: {e}')


def collect_em_3_metrics():
    logger.info('Collecting EM 3 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_3_firewall_rules')
            
        data = {'enabled': df['Enabled'].value_counts()['True'], 'disabled': df['Enabled'].value_counts()['False']}
        df = pd.DataFrame(data, index=[0])
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            df.to_sql('em_3_firewall_rules', db.conn, if_exists='append', index=False)
        
        logger.info('Finished collecting EM 3 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 3 metrics: {e}')


def collect_em_3_firewall_enabled():
    logger.info('Collecting EM 3 firewall enabled study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_3_firewall_enabled')
            
        unique_changes = pd.DataFrame(columns=df.columns)
        rows_to_add = []
        
        for profile in df['Profile'].unique():
            profile_df = df[df['Profile'] == profile].copy()
            profile_df.sort_values(by='created_at', inplace=True)
            last_status = None
            
            for index, row in profile_df.iterrows():
                if row['Enabled'] != last_status:
                    rows_to_add.append(row)
                    last_status = row['Enabled']
        
        unique_changes = pd.concat([unique_changes, pd.DataFrame(rows_to_add)], ignore_index=True)
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_3_firewall_enabled', unique_changes, list(df.keys()))
        
        logger.info('Finished collecting EM 3 firewall enabled study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 3 firewall enabled metrics: {e}')


def collect_em_4_metrics():
    logger.info('Collecting EM 4 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_4_scheduled_tasks')
            
        data = {'enabled': df['Enabled'].value_counts()['True'], 'disabled': df['Enabled'].value_counts()['False']}
        df = pd.DataFrame(data, index=[0])
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            df.to_sql('em_4_scheduled_tasks', db.conn, if_exists='append', index=False)
        
        logger.info('Finished collecting EM 4 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 4 metrics: {e}')


def collect_em_5_metrics():
    logger.info('Collecting EM 5 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_5_enabled_services')
            
        df = pd.DataFrame([df['StartType'].value_counts()])
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            df.to_sql('em_5_enabled_services', db.conn, if_exists='append', index=False)
        
        logger.info('Finished collecting EM 5 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 5 metrics: {e}')


def collect_em_8_metrics():
    logger.info('Collecting EM 8 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_8_wlan_settings')
        
        df['SSIDHash'] = df['SSIDName'].apply(hash_ssid)
        
        df = df[['SSIDHash', 'Authentication', 'Cipher', 'PasswordStrength', 'created_at']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_8_wlan_settings', df, list(df.keys()))
        
        logger.info('Finished collecting EM 8 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 8 metrics: {e}')


def collect_em_10_metrics():
    logger.info('Collecting EM 10 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_10_onedrive_enabled')
            
        df['AccountName'] = df['AccountName'].apply(hash_ssid)
        df = df[['AccountName', 'KfmFoldersProtectedNow', 'LastKnownFolderBackupTime', 'created_at']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_10_onedrive_enabled', df, list(df.keys()))
        
        logger.info('Finished collecting EM 10 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 10 metrics: {e}')


def collect_em_11_metrics():
    logger.info('Collecting EM 11 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_11_vulnerability_patching')
        
        df = df[(df['Software'].str.contains('Update for Windows 11', na=False))]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_11_vulnerability_patching', df, list(df.keys()))
            
        logger.info('Finished collecting EM 11 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 11 metrics: {e}')


def collect_em_12_metrics():
    logger.info('Collecting EM 12 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_12_kernel_versions')
            
        df = df[['MajorVersion', 'MinorVersion', 'BuildVersion', 'QfeVersion', 'ServiceVersion', 'BootMode', 'StartTime']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_12_kernel_versions', df, list(df.keys()))
        
        logger.info('Finished collecting EM 12 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 12 metrics: {e}')


def collect_em_13_metrics():
    logger.info('Collecting EM 13 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_13_eicar_removed')
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_13_eicar_removed', df, list(df.keys()))
        
        logger.info('Finished collecting EM 13 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 13 metrics: {e}')


def collect_em_15_metrics():
    logger.info('Collecting EM 15 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_15_external_ports')
            
        df['mac'] = df['mac'].apply(hash_ssid)
        df['ip'] = df['ip'].apply(hash_ssid)
        df = df[['mac', 'ip', 'port', 'state', 'reason', 'name', 'created_at']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_15_external_ports', df, list(df.keys()))
        
        logger.info('Finished collecting EM 15 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 15 metrics: {e}')


def collect_em_16_metrics():
    logger.info('Collecting EM 16 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_16_internal_ports')
            
        df['mac'] = df['mac'].apply(hash_ssid)
        df = df.groupby('mac')['port'].count()
        df = df.reset_index()
        df.columns = ['mac', 'count']
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            df.to_sql('em_16_internal_ports', db.conn, if_exists='append', index=False)
        
        logger.info('Finished collecting EM 16 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 16 metrics: {e}')


def collect_em_18_metrics():
    logger.info('Collecting EM 18 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_18_rdp_enabled')
            
        df['Name'] = df['Name'].apply(hash_ssid)
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_18_rdp_enabled', df, list(df.keys()))
        
        logger.info('Finished collecting EM 18 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 18 metrics: {e}')


def collect_em_19_metrics():
    logger.info('Collecting EM 19 study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_19_usb_devices')
            
        df['Id'] = df['Vid'] + df['Pid']
        df['Id'] = df['Id'].apply(hash_ssid)
        df = df[['Id', 'created_at']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_19_usb_devices', df, list(df.keys()))
        
        logger.info('Finished collecting EM 19 study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 19 metrics: {e}')


def collect_em_19_policy_metrics():
    logger.info('Collecting EM 19 policy study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_19_usb_policy')
            
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_19_usb_policy', df, list(df.keys()))
            
        logger.info('Finished collecting EM 19 policy study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 19 policy metrics: {e}')


def collect_em_20_user_metrics():
    logger.info('Collecting EM 20 user study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_20_users')
            
        df['sid'] = df['sid'].apply(hash_ssid)
        df = df[['sid', 'priv', 'last_logon', 'password_days', 'account_disabled' ,'created_at']]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_20_users', df, ['sid', 'priv', 'account_disabled'])
        
        logger.info('Finished collecting EM 20 user study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 20 user metrics: {e}')


def collect_em_20_login_metrics():
    logger.info('Collecting EM 20 login study metrics')
    try:
        with DatabaseManager() as db:
            df = db.read_database_table('em_20_admin_logins')
            
        df = df[df['LogonID'] != '0x3e7']
        df['Sid'] = df['Uid'].apply(hash_ssid)
        df = df[[ 'Sid', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'TimeGenerated' ]]
        
        with DatabaseManager(database_name='study-metrics.db') as db:
            db.add_new_rows('em_20_admin_logins', df, list(df.keys()))
        
        logger.info('Finished collecting EM 20 login study metrics')
    except Exception as e:
        logger.error(f'Could not collect EM 20 login metrics: {e}')


collect_aggregate_count('em_1_asset_register')
collect_aggregate_count('em_1_named_asset_register')
collect_em_2_metrics()
collect_em_3_metrics()
collect_em_3_firewall_enabled()
collect_em_4_metrics()
collect_em_5_metrics()

logger.info('Collecting EM 6 study metrics')
collect_table_subset('em_6_defender_updates', ['AMServiceEnabled', 'AntispywareEnabled', 'AntivirusEnabled', 'BehaviorMonitorEnabled', 'DefenderSignaturesOutOfDate', 'FullScanAge', 'FullScanRequired', 'IoavProtectionEnabled', 'IsTamperProtected', 'NISEnabled', 'OnAccessProtectionEnabled', 'QuickScanOverdue', 'RealTimeProtectionEnabled', 'created_at'])
logger.info('Finished collecting EM 6 study metrics')

logger.info('Collecting EM 7 study metrics')
collect_table_subset('em_7_password_policy', ['MinimumPasswordAge', 'MaximumPasswordAge', 'MinimumPasswordLength', 'PasswordComplexity', 'PasswordHistorySize', 'LockoutBadCount', 'RequireLogonToChangePassword', 'ForceLogoffWhenHourExpire', 'EnableAdminAccount', 'EnableGuestAccount', 'created_at'])
logger.info('Finished collecting EM 7 study metrics')

collect_em_8_metrics()

logger.info('Collecting EM 9 study metrics')
collect_table_subset('em_9_controlled_folder_access', ['EnableControlledFolderAccess', 'created_at'])
logger.info('Finished collecting EM 9 study metrics')

collect_em_10_metrics()
collect_em_11_metrics()
collect_em_12_metrics()
collect_em_13_metrics()
collect_aggregate_count('em_14_threat_scanning', column='InitialDetectionTime')
collect_em_15_metrics()
collect_em_16_metrics()
collect_em_18_metrics()
collect_em_19_metrics()
collect_em_19_policy_metrics()
collect_em_20_user_metrics()
collect_em_20_login_metrics()

logger.info('Finished collecting study data from database')