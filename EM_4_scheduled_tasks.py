#!/usr/bin/env python
# EM-4 Collect all scheduled tasks from the system and add them too the database

import win32com.client
import pandas as pd
import xml.etree.ElementTree as ET
import io

from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

import utils.common_functions as cf
from utils.database_class import DatabaseManager


def get_command(task):
    xml_data = task.Xml.replace('encoding="UTF-16"', 'encoding="UTF-8"')
    tree = ET.parse(io.StringIO(xml_data))
    root = tree.getroot()
    namespaces = {'ns': 'http://schemas.microsoft.com/windows/2004/02/mit/task'}
    command = root.find('.//ns:Exec/ns:Command', namespaces)
    
    if command is not None:
        Command = command.text
    else:
        Command = ""
    return(Command)


def get_scheduled_tasks():
    # Connect to the task scheduler service
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    
    tasks = []
    
    # Recursively traverse folders and subfolders to get all tasks
    def recurse_folder(folder):
        for task in folder.GetTasks(0):
            task_definition = task.Definition
            task_description = task_definition.RegistrationInfo.Description
            Enabled = task_definition.Settings.Enabled
            Command = get_command(task)
            #task_definition = task.Definition
            #triggers = task_definition.Triggers
            #triggers_list = []
            #for trigger in triggers:
            #    triggers_list.append(trigger.Type)
            
            task_info = {
                'Name': task.Name,
                'Path': task.Path,
                'Description': task_description,
                'Command': Command,
                'Enabled': Enabled,
                # 'Triggers': str(triggers_list),
                'LastRunTime': task.LastRunTime,
                'NextRunTime': task.NextRunTime
            }
            tasks.append(task_info)
        
        for subfolder in folder.GetFolders(0):
            recurse_folder(subfolder)
    
    recurse_folder(scheduler.GetFolder("\\"))
    
    return tasks

logger.info('Getting the Scheduled Tasks data')

scheduled_tasks = get_scheduled_tasks()

for task in scheduled_tasks:
    task['LastRunTime'] = task['LastRunTime'].timestamp()
    task['NextRunTime'] = task['NextRunTime'].timestamp()

df = pd.DataFrame(scheduled_tasks)

df['LastRunTime'] = pd.to_datetime(df['LastRunTime'], unit='s')
df['NextRunTime'] = pd.to_datetime(df['NextRunTime'], unit='s')
df['NextRunTime'] = pd.to_datetime(df['NextRunTime'], unit='s')

with DatabaseManager() as db:
    db.add_new_rows('em_4_scheduled_tasks', df, ['Name', 'Path', 'Description', 'Command', 'Enabled'])
    db.remove_old_rows('em_4_scheduled_tasks', df, ['Name', 'Path', 'Description', 'Command', 'Enabled'])

logger.info('Finished collecting the Scheduled Tasks data')