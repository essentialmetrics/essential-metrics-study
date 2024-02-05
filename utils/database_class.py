# Database class to manage all the database connections

import sqlite3
import time
import pandas as pd

import sys
sys.path.append(r'C:\opt\essential-metrics\utils')

from logger_config import configure_logger

logger = configure_logger(__name__)

class DatabaseManager:
    def __init__(self, database_name='essential-metrics.db'):
        self.database_name = database_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.cursor.close()
            self.conn.close()

    def clean_dataframe(self, df):
        '''
        This function will clean the dataframe and convert all values to SQL compatable values
        '''
        try:
            df = df.map(self.convert_dataframe_list_to_string)
        except Exception as e:
            logger.error(f'Could not convert the list to string format, exiting as we cannot add lists to the database: {e}')
            sys.exit(1)
        try:
            df = df.drop_duplicates()
            df = df.astype(str)
        except Exception as e:
            logger.error(f'Could not convert boolean values to string values in the dataframe: {e}')
            sys.exit(1)
        return(df)


    def convert_dataframe_list_to_string(self, cell_value):
        try:
            if isinstance(cell_value, list):
                return ', '.join(map(str, cell_value))
            else:
                return cell_value
        except Exception as e:
            logger.error(f'Could not parse list to string, wrapping the entire contents')
            return(f'{cell_value}')


    def execute_query(self, query, parameters=None):
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f'An exception was caught when working with the database, query: {query}; Exception: {e}')
        except Exception as e:
            self.conn.rollback()
            logger.error(f'Could not return the data from the query: {query}, there was an error: {e}')


    def read_database_table(self, table, retry_count=3, delay=1):
        for attempt in range(retry_count):
            try:
                logger.debug(f"Reading all from the {table} SQL table")
                return pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
            except Exception as e:
                logger.error(f'Reading from the {table} table failed: {e}')
                if attempt < retry_count - 1:
                    logger.info(f'Retrying read of {table}, Attempt {attempt + 2}/{retry_count}')
                    time.sleep(delay) 
                else:
                    logger.error(f'All retry attempts failed, while trying to read: {table}')
                    return pd.DataFrame()


    def execute_write(self, table_name, values):
        '''
        This function needs a list entered as the values
        '''
        try:
            # Ensure the number of values matches the number of columns in the table
            num_columns = len(values)
            placeholders = ', '.join(['?'] * num_columns)

            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

            self.cursor.execute(query, values)
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f'An exception was caught when inserting data into {table_name}; Exception: {e}')
        

    def add_new_rows(self, current_table, new_table, comparison_columns, single_row=False):
        '''
        This is a function that will allow you to add new rows into the backend database
        It will take table and rows that you do not want to add data to and find all new rows in the current dataset
        Inputs:
            current_table:          This is the database table name that we want to add records too
            new_table:              This is the new dataframe we are using for comparrason
            comparison_columns:     This is the columns of the dataframe we want to check, this is necessary to drop the database generated created_at column
            single_row:             This is used to compare only the last row of the database against our current dataframe
        '''
        try:
            new_table = self.clean_dataframe(new_table)
            query = f"SELECT * FROM {current_table}"
            df_current_table = pd.read_sql_query(query, self.conn)
            df_subset = new_table[comparison_columns]
            current_table_subset = df_current_table[comparison_columns]
            if single_row:
                current_table_subset = current_table_subset.tail(1)
            unique_rows = df_subset.merge(current_table_subset, on=comparison_columns, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
            full_unique_rows = unique_rows.merge(new_table, on=comparison_columns)
            if not full_unique_rows.empty:
                full_unique_rows.to_sql(current_table, self.conn, if_exists='append', index=False)
                logger.info(f"{len(full_unique_rows)} new rows added to {current_table} successfully")
            else:
                logger.info(f"No new rows for {current_table}")
                
        except pd.io.sql.DatabaseError as e:
            logger.error(f"Database error occurred writing rows to {current_table}: {e}")
        except KeyError as e:
            logger.error(f"Key error adding new rows to {current_table}: {e}. Check your column names and comparison_columns")
        except Exception as e:
            logger.error(f"An error occurred writing to table: {current_table}: {e}")


    def remove_old_rows(self, current_table, new_table, comparison_columns):
        try:
            new_table = self.clean_dataframe(new_table)
            query = f"SELECT * FROM {current_table}"
            df_current_table = pd.read_sql_query(query, self.conn)
            df_subset = new_table[comparison_columns]
            current_table_subset = df_current_table[comparison_columns]
            old_rows = current_table_subset.merge(df_subset, on=comparison_columns, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
            old_rows = old_rows.merge(df_current_table, on=comparison_columns)

            if not old_rows.empty:
                try:
                    for index, row in old_rows.iterrows():
                        conditions = []
                        for col in old_rows.columns:
                            if row[col] is None:
                                conditions.append(f"({col} IS NULL OR {col} is 'None')")
                            else:
                                conditions.append(f"{col} = '{row[col]}'")
                        where_clause = " AND ".join(conditions)
                        delete_query = f"DELETE FROM {current_table} WHERE {where_clause}"
                        logger.debug(f'Running delete with query: {delete_query}')
                        self.conn.execute(delete_query)
                    logger.info(f"{len(old_rows)} old rows removed successfully from {current_table}.")
                except Exception as e:
                    logger.info(f"{len(old_rows)} old rows could not be removed from {current_table}: {e}")
                
                old_rows.to_sql(f'{current_table}_decommissioned', self.conn, if_exists='append', index=False)
                
            else:
                logger.info(f"No old rows to remove from {current_table}")

        except pd.io.sql.DatabaseError as e:
            logger.info(f"Database error occurred removing from {current_table}: {e}")
        except KeyError as e:
            logger.info(f"Key error occurred removing from {current_table}: {e}. Check your column names and comparison_columns.")
        except Exception as e:
            logger.info(f"An error occurred removing from {current_table}: {e}")


def create_table(database_name, table_name, create_table_sql):
    try:
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
        logger.info(f"Table '{table_name}' created successfully in {database_name}.")
    except sqlite3.Error as e:
        logger.error("SQLite error: %s", str(e))
    except Exception as e:
        logger.error("Error: %s", str(e))


def app_install_date():
    try:
        from datetime import datetime
        install_date = datetime.now().strftime("%Y%m%d")
        with sqlite3.connect('essential-metrics.db') as conn:
            cursor = conn.cursor()
            query = f"INSERT INTO app_install_date VALUES ({install_date})"
            cursor.execute(query)
    except sqlite3.Error as e:
        logger.error("SQLite error: %s", str(e))
    except Exception as e:
       logger.error("Error: %s", str(e))


# These are all the essential metrics database tables.
# There are other that are created dynamically with pandas to_sql function
# We created ones here that we needed more control over, the created_at datetime SQL function was used extensively to track when items were added to the database
app_install_date_sql = '''
    CREATE TABLE IF NOT EXISTS app_install_date
    (timestamp TEXT)
    '''

em_1_asset_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_1_asset_register (
        asset_name TEXT,
        mac TEXT PRIMARY KEY,
        ip TEXT,
        vendor TEXT,
        os TEXT,
        confidence TEXT,
        cpe TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_1_named_asset_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_1_named_asset_register (
        id INTEGER PRIMARY KEY,
        asset_name TEXT,
        mac TEXT,
        ip TEXT,
        vendor TEXT,
        os TEXT,
        confidence TEXT,
        cpe TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_2_software_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_2_software_register (
        Publisher TEXT,
        DisplayName TEXT,
        DisplayVersion TEXT,
        InstallDate TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_2_software_register_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_2_software_register_decommissioned (
        Publisher TEXT,
        DisplayName TEXT,
        DisplayVersion TEXT,
        InstallDate TEXT,
        created_at TEXT,
        removed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_3_firewall_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_3_firewall_enabled (
        Profile TEXT,
        Enabled TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_3_firewall_rules_sql = '''
    CREATE TABLE IF NOT EXISTS em_3_firewall_rules (
         Name TEXT,
         DisplayName TEXT,
         Description TEXT,
         DisplayGroup TEXT,
         Enabled TEXT,
         Profile TEXT,
         Direction TEXT,
         Action TEXT,
         EdgeTraversalPolicy TEXT,
         Owner TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_3_firewall_rules_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_3_firewall_rules_decommissioned (
         Name TEXT,
         DisplayName TEXT,
         Description TEXT,
         DisplayGroup TEXT,
         Enabled TEXT,
         Profile TEXT,
         Direction TEXT,
         Action TEXT,
         EdgeTraversalPolicy TEXT,
         Owner TEXT,
        created_at TEXT,
        removed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_4_scheduled_tasks_sql = '''
    CREATE TABLE IF NOT EXISTS em_4_scheduled_tasks (
        Name TEXT,
        Path TEXT,
        Description TEXT,
        Command TEXT,
        Enabled TEXT,
        LastRunTime TEXT,
        NextRunTime,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_4_scheduled_tasks_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_4_scheduled_tasks_decommissioned (
        Name TEXT,
        Path TEXT,
        Description TEXT,
        Command TEXT,
        Enabled TEXT,
        LastRunTime TEXT,
        NextRunTime,
        created_at TEXT,
        removed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_5_enabled_services_sql = '''
    CREATE TABLE IF NOT EXISTS em_5_enabled_services (
         DisplayName TEXT,
         ServiceName TEXT,
         StartType TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_5_enabled_services_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_5_enabled_services_decommissioned (
         DisplayName TEXT,
         ServiceName TEXT,
         StartType TEXT,
        created_at TEXT,
        removed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_6_defender_updates_sql = '''
    CREATE TABLE IF NOT EXISTS em_6_defender_updates (
         AMServiceEnabled TEXT,
         AMRunningMode TEXT,
         AntispywareEnabled TEXT,
         AntispywareSignatureAge TEXT,
         AntispywareSignatureLastUpdated TEXT,
         AntivirusEnabled TEXT,
         AntivirusSignatureAge TEXT,
         AntivirusSignatureLastUpdated TEXT,
         BehaviorMonitorEnabled TEXT,
         DefenderSignaturesOutOfDate TEXT,
         FullScanAge TEXT,
         FullScanRequired TEXT,
         IoavProtectionEnabled TEXT,
         IsTamperProtected TEXT,
         NISEnabled TEXT,
         NISSignatureAge TEXT,
         NISSignatureLastUpdated TEXT,
         OnAccessProtectionEnabled TEXT,
         QuickScanEndTime TEXT,
         QuickScanOverdue TEXT,
         RealTimeProtectionEnabled TEXT,
         RebootRequired TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_7_password_policy_sql = '''
    CREATE TABLE IF NOT EXISTS em_7_password_policy (
        MinimumPasswordAge TEXT,
        MaximumPasswordAge TEXT,
        MinimumPasswordLength TEXT,
        PasswordComplexity TEXT,
        PasswordHistorySize TEXT,
        LockoutBadCount TEXT,
        RequireLogonToChangePassword TEXT,
        ForceLogoffWhenHourExpire TEXT,
        NewAdministratorName TEXT,
        NewGuestName TEXT,
        ClearTextPassword TEXT,
        LSAAnonymousNameLookup TEXT,
        EnableAdminAccount TEXT,
        EnableGuestAccount TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_8_wlan_settings_sql = '''
    CREATE TABLE IF NOT EXISTS em_8_wlan_settings (
         ConnectionMode TEXT,
         SSIDName TEXT,
         NetworkType TEXT,
         Authentication TEXT,
         Cipher TEXT,
         KeyContent TEXT,
         PasswordStrength TEXT,
         Feedback TEXT,
         Suggestions TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_9_controlled_folder_access_sql = '''
    CREATE TABLE IF NOT EXISTS em_9_controlled_folder_access (
         EnableControlledFolderAccess TEXT,
         ControlledFolderAccessProtectedFolders TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_10_onedrive_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_10_onedrive_enabled (
        AccountName TEXT,
        UserFolder TEXT,
        KfmFoldersProtectedNow TEXT,
        LastKnownFolderBackupTime TEXT,
        LastKnownSettingsChange TEXT,
        RestoreUrl TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_11_vulnerability_patching_sql = '''
    CREATE TABLE IF NOT EXISTS em_11_vulnerability_patching (
        UpdateGUID TEXT,
        Software TEXT,
        EventIdentifier TEXT,
        TimeGenerated TEXT
    )
'''

em_12_reboot_analysis_sql = '''
    CREATE TABLE IF NOT EXISTS em_12_reboot_analysis (
        Process TEXT,
        Reason TEXT,
        Status TEXT,
        Power TEXT,
        User TEXT,
        EventCode TEXT,
        TimeGenerated TEXT
    )
'''

em_12_kernel_versions_sql = '''
    CREATE TABLE IF NOT EXISTS em_12_kernel_versions (
        MajorVersion TEXT,
        MinorVersion TEXT,
        BuildVersion TEXT,
        QfeVersion TEXT,
        ServiceVersion TEXT,
        BootMode TEXT,
        StartTime TEXT,
        EventCode TEXT,
        TimeGenerated TEXT
    )
'''

em_13_eicar_removed_sql = '''
    CREATE TABLE IF NOT EXISTS em_13_eicar_removed (
         File TEXT,
         Removed TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_14_threat_scanning_sql = '''
    CREATE TABLE IF NOT EXISTS em_14_threat_scanning (
         DetectionID TEXT,
         ActionSuccess TEXT,
         DomainUser TEXT,
         InitialDetectionTime TEXT,
         LastThreatStatusChangeTime TEXT,
         ProcessName TEXT,
         RemediationTime TEXT,
         Resources TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_15_external_ports_sql = '''
    CREATE TABLE IF NOT EXISTS em_15_external_ports (
         mac TEXT,
         ip TEXT,
         port TEXT,
         state TEXT,
         reason TEXT,
         name TEXT,
         product TEXT,
         version TEXT,
         extrainfo TEXT,
         conf TEXT,
         cpe TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_16_internal_ports_heatmap_sql = '''
    CREATE TABLE IF NOT EXISTS em_16_internal_ports_heatmap (
         mac TEXT,
         ip TEXT,
         port TEXT,
         state TEXT,
         reason TEXT,
         name TEXT,
         product TEXT,
         version TEXT,
         extrainfo TEXT,
         conf TEXT,
         cpe TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_16_internal_ports_sql = '''
    CREATE TABLE IF NOT EXISTS em_16_internal_ports (
         mac TEXT,
         ip TEXT,
         port TEXT,
         state TEXT,
         reason TEXT,
         name TEXT,
         product TEXT,
         version TEXT,
         extrainfo TEXT,
         conf TEXT,
         cpe TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_16_internal_ports_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_16_internal_ports_decommissioned (
         mac TEXT,
         ip TEXT,
         port TEXT,
         state TEXT,
         reason TEXT,
         name TEXT,
         product TEXT,
         version TEXT,
         extrainfo TEXT,
         conf TEXT,
         cpe TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_17_last_event_timestamp_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_last_event_timestamp
    (timestamp INT)
    '''

em_17_firewall_logs_timestamp_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_firewall_logs_timestamp
    (timestamp INT)
    '''

em_17_firewall_logs_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_firewall_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    protocol TEXT,
    src_ip TEXT,
    dst_ip TEXT,
    src_port TEXT,
    dst_port TEXT,
    size TEXT,
    path TEXT,
    datetime TEXT,
    pid TEXT,
    application TEXT,
    process_cli TEXT
    )
    '''

em_17_running_pids_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_running_pids
    (event INT,
    pid INT,
    application TEXT,
    process_cli TEXT,
    Timestamp TEXT
    )
    '''

em_17_completed_pids_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_completed_pids
    (pid INT, 
    application TEXT,
    process_cli TEXT,
    start_time TEXT,
    end_time TEXT,
    duration TEXT
    )
    '''

em_17_pid_tracking_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_17_pid_tracking_enabled (
         CreateEnabled TEXT,
         TerminationEnabled TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_18_rdp_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_18_rdp_enabled (
         Name TEXT,
         RDPUsers TEXT,
         RDPEnabled TEXT,
         NLAEnabled TEXT,
         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_19_usb_devices_sql = '''
    CREATE TABLE IF NOT EXISTS em_19_usb_devices (
        Vendor TEXT,
        Product TEXT,
        Vid TEXT,
        Pid TEXT,
        Service TEXT,
        LocationInformation TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_19_usb_policy_sql = '''
    CREATE TABLE IF NOT EXISTS em_19_usb_policy (
        Path TEXT,
        Name TEXT,
        Data TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_admin_logins_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_admin_logins (
         RecordNumber TEXT,
         Uid TEXT,
         User TEXT,
         LogonType TEXT,
         EventIdentifier TEXT,
         LogonID TEXT,
         ElevatedToken TEXT,
         Process TEXT,
         SourceAddress TEXT,
         SourcePort TEXT,
         TimeGenerated TEXT
    )
'''

em_20_users_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_users (
        sid TEXT,
        full_name TEXT,
        name TEXT,
        comment TEXT,
        priv TEXT,
        last_logon TEXT,
        password_days TEXT,
        account_disabled TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_users_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_users_decommissioned (
        sid TEXT,
        full_name TEXT,
        name TEXT,
        comment TEXT,
        priv TEXT,
        last_logon TEXT,
        password_days TEXT,
        account_disabled TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_groups_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_groups (
        local_group TEXT,
        members TEXT,
        uri TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_groups_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_groups_decommissioned (
        local_group TEXT,
        members TEXT,
        uri TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_groups_decommissioned_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_groups_decommissioned (
        local_group TEXT,
        members TEXT,
        uri TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

em_20_logon_audit_tracking_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_logon_audit_tracking_enabled (
        LogonEnabled TEXT,
        LogoffEnabled TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

# These are the study tables that are in the study-metrics.db database
# These are entirely separated from the essential-metrics database so our subject can see exactly what data we are retrieving from the study
# We did not want to leave any ambiguity in what we were collecting here so we separated these out into different databases so we could present 
# the data to the subjects on a continuing basis so their informed concent was as explicit and informed as possible when they chose to share the data at the end of the study period.

s_em_1_asset_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_1_asset_register (
        created_at TEXT,
        count TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_1_named_asset_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_1_named_asset_register (
        created_at TEXT,
        count TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_2_software_register_sql = '''
    CREATE TABLE IF NOT EXISTS em_2_software_register (
        installed TEXT,
        decommissioned TEXT,
        updated TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_3_firewall_rules = '''
    CREATE TABLE IF NOT EXISTS em_3_firewall_rules (
        enabled TEXT,
        disabled TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_3_firewall_enabled = '''
    CREATE TABLE IF NOT EXISTS em_3_firewall_enabled (
        Profile TEXT,
        Enabled TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_4_scheduled_tasks = '''
    CREATE TABLE IF NOT EXISTS em_4_scheduled_tasks (
        enabled TEXT,
        disabled TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_5_enabled_services = '''
    CREATE TABLE IF NOT EXISTS em_5_enabled_services (
        Manual TEXT,
        Automatic TEXT,
        Disabled TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_6_defender_updates = '''
    CREATE TABLE IF NOT EXISTS em_6_defender_updates (
        AMServiceEnabled TEXT,
        AntispywareEnabled TEXT,
        AntivirusEnabled TEXT,
        BehaviorMonitorEnabled TEXT,
        DefenderSignaturesOutOfDate TEXT,
        FullScanAge TEXT,
        FullScanRequired TEXT,
        IoavProtectionEnabled TEXT,
        IsTamperProtected TEXT,
        NISEnabled TEXT,
        OnAccessProtectionEnabled TEXT,
        QuickScanOverdue TEXT,
        RealTimeProtectionEnabled TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_7_password_policy = '''
    CREATE TABLE IF NOT EXISTS em_7_password_policy (
        MinimumPasswordAge TEXT,
        MaximumPasswordAge TEXT,
        MinimumPasswordLength TEXT,
        PasswordComplexity TEXT,
        PasswordHistorySize TEXT,
        LockoutBadCount TEXT,
        RequireLogonToChangePassword TEXT,
        ForceLogoffWhenHourExpire TEXT,
        EnableAdminAccount TEXT,
        EnableGuestAccount TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_8_wlan_settings = '''
    CREATE TABLE IF NOT EXISTS em_8_wlan_settings (
        SSIDHash TEXT,
        Authentication TEXT,
        Cipher TEXT,
        PasswordStrength TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_9_controlled_folder_access = '''
    CREATE TABLE IF NOT EXISTS em_9_controlled_folder_access (
        EnableControlledFolderAccess TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_10_onedrive_enabled = '''
    CREATE TABLE IF NOT EXISTS em_10_onedrive_enabled (
        AccountName TEXT,
        KfmFoldersProtectedNow TEXT,
        LastKnownFolderBackupTime TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_11_vulnerability_patching = '''
    CREATE TABLE IF NOT EXISTS em_11_vulnerability_patching (
        UpdateGUID TEXT,
        Software TEXT,
        EventIdentifier TEXT,
        TimeGenerated TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_12_kernel_versions = '''
    CREATE TABLE IF NOT EXISTS em_12_kernel_versions (
        MajorVersion TEXT,
        MinorVersion TEXT,
        BuildVersion TEXT,
        QfeVersion TEXT,
        ServiceVersion TEXT,
        BootMode TEXT,
        StartTime TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_13_eicar_removed_sql = '''
    CREATE TABLE IF NOT EXISTS em_13_eicar_removed (
         File TEXT,
         Removed TEXT,
         created_at,
         added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_14_threat_scanning_sql = '''
    CREATE TABLE IF NOT EXISTS em_14_threat_scanning (
        created_at TEXT,
        count TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_15_external_ports_sql = '''
    CREATE TABLE IF NOT EXISTS em_15_external_ports (
        mac TEXT,
        ip TEXT,
        port TEXT,
        state TEXT,
        reason TEXT,
        name TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_16_internal_ports_sql = '''
    CREATE TABLE IF NOT EXISTS em_16_internal_ports (
        mac TEXT,
        count TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_18_rdp_enabled_sql = '''
    CREATE TABLE IF NOT EXISTS em_18_rdp_enabled (
        Name TEXT,
        RDPUsers TEXT,
        RDPEnabled TEXT,
        NLAEnabled TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_19_usb_devices_sql = '''
    CREATE TABLE IF NOT EXISTS em_19_usb_devices (
        Id TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_19_usb_policy_sql = '''
    CREATE TABLE IF NOT EXISTS em_19_usb_policy (
        Path TEXT,
        Name TEXT,
        Data TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

s_em_20_users_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_users (
        sid TEXT,
        priv TEXT,
        last_logon TEXT,
        password_days TEXT,
        account_disabled TEXT,
        created_at TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''


s_em_20_admin_logins_sql = '''
    CREATE TABLE IF NOT EXISTS em_20_admin_logins (
        Sid TEXT,
        LogonType TEXT,
        EventIdentifier TEXT,
        LogonID TEXT,
        ElevatedToken TEXT,
        TimeGenerated TEXT,
        added_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

if __name__ == "__main__":
    logger.debug("Creating tables in the database")
    create_table('essential-metrics.db', 'app_install_date', app_install_date_sql)
    create_table('essential-metrics.db', 'em_1_asset_register', em_1_asset_register_sql)
    create_table('essential-metrics.db', 'em_1_named_asset_register', em_1_named_asset_register_sql)
    create_table('essential-metrics.db', 'em_2_software_register', em_2_software_register_sql)
    create_table('essential-metrics.db', 'em_2_software_register_decommissioned', em_2_software_register_decommissioned_sql)
    create_table('essential-metrics.db', 'em_3_firewall_enabled', em_3_firewall_enabled_sql)
    create_table('essential-metrics.db', 'em_3_firewall_rules', em_3_firewall_rules_sql)
    create_table('essential-metrics.db', 'em_3_firewall_rules_decommission', em_3_firewall_rules_decommissioned_sql)
    create_table('essential-metrics.db', 'em_4_scheduled_tasks', em_4_scheduled_tasks_sql)
    create_table('essential-metrics.db', 'em_4_scheduled_tasks_decommissioned', em_4_scheduled_tasks_decommissioned_sql)
    create_table('essential-metrics.db', 'em_5_enabled_services', em_5_enabled_services_sql)
    create_table('essential-metrics.db', 'em_5_enabled_services_decommission', em_5_enabled_services_decommissioned_sql)
    create_table('essential-metrics.db', 'em_6_defender_updates', em_6_defender_updates_sql)
    create_table('essential-metrics.db', 'em_7_password_policy', em_7_password_policy_sql)
    create_table('essential-metrics.db', 'em_8_wlan_settings', em_8_wlan_settings_sql)
    create_table('essential-metrics.db', 'em_9_controlled_folder_access', em_9_controlled_folder_access_sql)
    create_table('essential-metrics.db', 'em_10_onedrive_enabled', em_10_onedrive_enabled_sql)
    create_table('essential-metrics.db', 'em_11_vulnerability_patching', em_11_vulnerability_patching_sql)
    create_table('essential-metrics.db', 'em_12_reboot_analysis', em_12_reboot_analysis_sql)
    create_table('essential-metrics.db', 'em_12_kernel_versions', em_12_kernel_versions_sql)
    create_table('essential-metrics.db', 'em_13_eicar_removed', em_13_eicar_removed_sql)
    create_table('essential-metrics.db', 'em_14_threat_scanning', em_14_threat_scanning_sql)
    create_table('essential-metrics.db', 'em_15_external_ports', em_15_external_ports_sql)
    create_table('essential-metrics.db', 'em_16_internal_ports', em_16_internal_ports_sql)
    create_table('essential-metrics.db', 'em_16_internal_ports_decommissioned', em_16_internal_ports_decommissioned_sql)
    create_table('essential-metrics.db', 'em_16_internal_ports_heatmap', em_16_internal_ports_heatmap_sql)
    create_table('essential-metrics.db', 'em_17_last_event_timestamp', em_17_last_event_timestamp_sql)
    create_table('essential-metrics.db', 'em_17_firewall_logs_timestamp', em_17_firewall_logs_timestamp_sql)
    create_table('essential-metrics.db', 'em_17_firewall_logs', em_17_firewall_logs_sql)
    create_table('essential-metrics.db', 'em_17_running_pids', em_17_running_pids_sql)
    create_table('essential-metrics.db', 'em_17_completed_pids', em_17_completed_pids_sql)
    create_table('essential-metrics.db', 'em_17_pid_tracking_enabled', em_17_pid_tracking_enabled_sql)
    create_table('essential-metrics.db', 'em_18_rdp_enabled', em_18_rdp_enabled_sql)
    create_table('essential-metrics.db', 'em_19_usb_devices', em_19_usb_devices_sql)
    create_table('essential-metrics.db', 'em_19_usb_policy', em_19_usb_policy_sql)
    create_table('essential-metrics.db', 'em_20_users', em_20_users_sql)
    create_table('essential-metrics.db', 'em_20_users_decommissioned', em_20_users_decommissioned_sql)
    create_table('essential-metrics.db', 'em_20_groups', em_20_groups_sql)
    create_table('essential-metrics.db', 'em_20_groups_decommissioned', em_20_groups_decommissioned_sql)
    create_table('essential-metrics.db', 'em_20_admin_logins', em_20_admin_logins_sql)
    create_table('essential-metrics.db', 'em_20_logon_audit_tracking_enabled', em_20_logon_audit_tracking_enabled_sql)
    
    create_table('study-metrics.db', 'em_1_asset_register', s_em_1_asset_register_sql)
    create_table('study-metrics.db', 'em_1_named_asset_register', s_em_1_named_asset_register_sql)
    create_table('study-metrics.db', 'em_2_software_register', s_em_2_software_register_sql)
    create_table('study-metrics.db', 'em_3_firewall_rules', s_em_3_firewall_rules)
    create_table('study-metrics.db', 'em_3_firewall_enabled', s_em_3_firewall_enabled)
    create_table('study-metrics.db', 'em_4_scheduled_tasks', s_em_4_scheduled_tasks)
    create_table('study-metrics.db', 'em_5_enabled_services', s_em_5_enabled_services)
    create_table('study-metrics.db', 'em_6_defender_updates', s_em_6_defender_updates)
    create_table('study-metrics.db', 'em_7_password_policy', s_em_7_password_policy)
    create_table('study-metrics.db', 'em_8_wlan_settings', s_em_8_wlan_settings)
    create_table('study-metrics.db', 'em_9_controlled_folder_access', s_em_9_controlled_folder_access)
    create_table('study-metrics.db', 'em_10_onedrive_enabled', s_em_10_onedrive_enabled)
    create_table('study-metrics.db', 'em_11_vulnerability_patching', s_em_11_vulnerability_patching)
    create_table('study-metrics.db', 'em_12_kernel_versions', s_em_12_kernel_versions)
    create_table('study-metrics.db', 'em_13_eicar_removed', s_em_13_eicar_removed_sql)
    create_table('study-metrics.db', 'em_14_threat_scanning', s_em_14_threat_scanning_sql)
    create_table('study-metrics.db', 'em_15_external_ports', s_em_15_external_ports_sql)
    create_table('study-metrics.db', 'em_16_internal_ports', s_em_16_internal_ports_sql)
    create_table('study-metrics.db', 'em_18_rdp_enabled', s_em_18_rdp_enabled_sql)
    create_table('study-metrics.db', 'em_19_usb_devices', s_em_19_usb_devices_sql)
    create_table('study-metrics.db', 'em_19_usb_policy', s_em_19_usb_policy_sql)
    create_table('study-metrics.db', 'em_20_users', s_em_20_users_sql)
    create_table('study-metrics.db', 'em_20_admin_logins', s_em_20_admin_logins_sql)
    
    app_install_date()