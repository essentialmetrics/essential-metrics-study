#!/usr/bin/env python
# EM-20 - Admin Logins
# We need to track our users and who is in the Administrator group

# https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups
# https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/basic-audit-account-management
# https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/basic-audit-logon-events#configure-this-audit-setting
# https://learn.microsoft.com/en-us/windows/win32/api/lmaccess/nf-lmaccess-netusergetinfo

import sys
import win32net
import win32netcon
import pandas as pd
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

import datetime
from utils.database_class import DatabaseManager

logger.info(f'Getting the user and group data from the system')

all_users = {}
user_details = []

def get_user_info(user):
    global user_details
    try:
        user_info = win32net.NetUserGetInfo(None, user, 4)
        password_age_seconds = user_info['password_age']
        password_age_timedelta = datetime.timedelta(seconds=password_age_seconds)
        # Convert password_age to days
        password_age_days = password_age_timedelta.days
        user_info['password_days'] = password_age_days
        user_info['account_disabled'] = user_info['flags'] & win32netcon.UF_ACCOUNTDISABLE == win32netcon.UF_ACCOUNTDISABLE
        user_info['sid'] = str(user_info['user_sid']).split(':')[1]
        user_details.append(user_info)
    except Exception as e:
        logger.error(f'Could not get back user details from the system, error: {e}')

def construct_uri(group_name):
    group_name_cleaned = group_name.split('\\')[-1]
    uri = f"https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#{group_name_cleaned.replace(' ', '-').lower()}"
    return uri

groups = cf.run_wmi_query('SELECT * FROM Win32_Group')

try:
    for group in groups:
        group_name = group.Caption
        all_users[group_name] = []
        users = cf.run_wmi_query(f"ASSOCIATORS OF {{Win32_Group.Domain='{group.Domain}',Name='{group.Name}'}} WHERE AssocClass=Win32_GroupUser")
        for user in users:
            # the SIDType of 1 represents a user Security identifier so we will only pull the user accounts with this
            # This will get rid of the INTERACTIVE, ISS and Authenticated Users SIDs (5)
            if user.SIDType == 1:
                user_name = user.Caption
                all_users[group_name].append(user_name)
except Exception as e:
    logger.error(f'Could not get back group data from the system, exiting as we cannot continue without this data: {e}')
    sys.exit(1)

try:
    # Get a list of users in these groups
    all_values = list(set(value.split('\\')[-1] for values_list in all_users.values() for value in values_list))
except Exception as e:
    logger.error(f'Could not get users from group selections: {e}')
    sys.exit(1)

for user in all_values:
  get_user_info(user)

try:
    desired_data = ['sid', 'full_name', 'name', 'comment', 'priv', 'last_logon', 'password_days', 'account_disabled']
    filtered_data = [{key: d[key] for key in desired_data} for d in user_details]
    df = pd.DataFrame(filtered_data)
    df = df.astype(str)
except Exception as e:
    logger.error(f'Could not parse the returned user details from the system, exiting: {e}')
    sys.exit(1)

with DatabaseManager() as db:
    db.add_new_rows('em_20_users', df, list(df.keys()))
    db.remove_old_rows('em_20_users', df, list(df.keys()))

# Adding group data to database

try:
    data = []
    filtered_dict = {key: value for key, value in all_users.items() if value}

    for group, users in filtered_dict.items():
        uri = construct_uri(group)
        for user in users:
            data.append([group.split('\\')[-1], user.split('\\')[-1], uri])

    df = pd.DataFrame(data, columns=['local_group', 'members', 'uri'])
    df = df.astype(str)
except Exception as e:
    logger.error(f'Could not parse the returned group data from the system: {e}')
    sys.exit(1)

with DatabaseManager() as db:
    db.add_new_rows('em_20_groups', df, list(df.keys()))
    db.remove_old_rows('em_20_groups', df, list(df.keys()))

logger.info(f'Completed gathering the user and group data from the system successfully')