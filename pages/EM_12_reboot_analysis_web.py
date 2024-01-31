#!/usr/bin/env python
# EM-12 - Reboot analysis, with this we can check how quickly our users are rebooting their systems after patching

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

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_12_kernel_versions = db.read_database_table('em_12_kernel_versions')

with DatabaseManager() as db:
    em_12_reboot_analysis = db.read_database_table('em_12_reboot_analysis')

with DatabaseManager() as db:
    em_11_vulnerability_patching = db.read_database_table('em_11_vulnerability_patching')

def generate_reboot_graph(df):
    try:
        df['SoftwareVersion'] = (
            df['MajorVersion'].astype(str) + '.' +
            df['MinorVersion'].astype(str) + '.' +
            df['BuildVersion'].astype(str) + ' Build ' +
            df['QfeVersion'].astype(str)
        )

        df['StartTime'] = pd.to_datetime(df['StartTime'])
        # This will sort the start times based on the software version and take the lowest start time
        # This will give us the first time the system logged in on this version
        earliest_versions = df.groupby('SoftwareVersion')['StartTime'].min().reset_index()
        fig = px.scatter(earliest_versions, x='SoftwareVersion', y='StartTime',
                        labels={'StartTime': 'Start Time', 'SoftwareVersion': 'Software Version'},
                        title='Earliest Start Time for Each Software Version')

        # Customize the layout for better readability
        fig.update_layout(xaxis_tickangle=-45, xaxis_title='Software Version', yaxis_title='Start Time')
        fig.update_traces(marker=dict(size=10))

        return(fig)
    except Exception as e:
        logger.error(f'The scatter graph could not be rendered, sending back generic graph: {e}')
        cgf.set_no_results_found_figure()


def patch_to_reboot_analysis(df, df_v):
    '''
    This function will look at the times between the installation time and the reboot time for the same patchset.
    Input:
        df: em_12_kernel_versions
        df_v: em_11_vulnerability_patching
    '''
    try:
        # Get a unified build version
        df['SoftwareVersion'] = (
            df['MajorVersion'].astype(str) + '.' +
            df['MinorVersion'].astype(str) + '.' +
            df['BuildVersion'].astype(str) + ' Build ' +
            df['QfeVersion'].astype(str)
        )
        # Get the first time this unified version was seen
        df['StartTime'] = pd.to_datetime(df['StartTime'])
        earliest_versions = df.groupby('SoftwareVersion')['StartTime'].min().reset_index()

        # Clean the vulnerability dataframe and set the timestamp in a format pd can use
        installed_updates = df_v[(df_v['Software'].str.contains('Cumulative Update for Windows 11', na=False)) & (df_v['EventIdentifier'] == 'Install Started')]
        installed_updates.loc[:, 'TimeGenerated'] = installed_updates['TimeGenerated'].str[:-4]
        installed_updates.loc[:, 'TimeGenerated'] = pd.to_datetime(installed_updates['TimeGenerated'], format='%Y%m%d%H%M%S.%f')
        installed_updates = installed_updates.drop(columns=['UpdateGUID', 'EventIdentifier'])

        # Get a unified timestamp for each of the columns in the dataframe we need to analyse
        earliest_versions['StartTime'] = earliest_versions['StartTime'].dt.tz_localize(None)
        installed_updates['TimeGenerated'] = pd.to_datetime(installed_updates['TimeGenerated']).dt.tz_localize(None)
        combined_df = pd.concat([installed_updates, earliest_versions])
        combined_df['UnifiedTime'] = combined_df['TimeGenerated'].fillna(combined_df['StartTime'])
        combined_df_sorted = combined_df.sort_values(by='UnifiedTime')

        # This will find all consequative rows that are not unique in the 'Software' column
        # this is necessary as I found multiple software versions without a coorosponding event ID 12 so these ned to be removed from the analysis as they cannot be paired
        mask = (
            (combined_df_sorted['Software'] != combined_df_sorted['Software'].shift()) &
            ~(combined_df_sorted['Software'].isna() & combined_df_sorted['Software'].shift().isna())
        )

        combined_df_dropped = combined_df_sorted[mask]
        data = []

        # Compare the rows in the dataframe 2 at a time and do a time differential on them saving the time difference and the start and end times
        for i in range(0, len(combined_df_dropped), 2):
            if i+1 < len(combined_df_dropped):
                software = combined_df_dropped.iloc[i]['Software']
                next_software_version = combined_df_dropped.iloc[i+1]['SoftwareVersion']
                start_time = combined_df_dropped.iloc[i]['UnifiedTime']
                end_time = combined_df_dropped.iloc[i+1]['UnifiedTime']
                time_diff = end_time - start_time
                data.append([software, next_software_version, start_time, end_time, time_diff])
        
        # Create a dataframe from this data and set the time differential to hours
        new_df = pd.DataFrame(data, columns=['Software', 'Next_SoftwareVersion', 'StartTime', 'EndTime', 'TimeDifference'])
        new_df['TimeDifferenceHours'] = new_df['TimeDifference'].dt.total_seconds() / 3600

        fig = px.bar(new_df, 
                    x='Software', 
                    y='TimeDifferenceHours', 
                    labels={'TimeDifferenceHours': 'Install started -> reboot completed', 'Software': 'Software Update'},
                    title='Software Install started to Reboot actualized')

        fig.update_layout(xaxis_tickangle=-45, xaxis_title='Software Update', yaxis_title='Install started -> reboot completed (Hours)')

        return(fig)
    except Exception as e:
        logger.error(f'The bar graph could not be rendered, sending back generic graph: {e}')
        return(cgf.set_no_results_found_figure())


    
model_id = 'em_12_reboot_analysis'
training_modal_graph = cgf.training_modal(model_id, 'Reboot management', 'https://www.youtube-nocookie.com/embed/xtsNTwRg7iM?si=40yydd3SmHuglvlL')
new_windows_version = generate_reboot_graph(em_12_kernel_versions)
patch_reboot_analysis = patch_to_reboot_analysis(em_12_kernel_versions, em_11_vulnerability_patching)


layout = html.Div([
    html.H2('Patch Management (Reboot Analysis)', style={'textAlign': 'center'}),
    dbc.Button("Patching Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Patching", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Rebooting is an integral part of patch management as it allows the new kernel code to be loaded in the operating system.',
        html.Br(),
        'This patches critical security bugs in the operating system and decreases your chances of harm from a vulnerability as the window of opportunity for an attacker is reduced.',
        html.Br(),
        'These patches generally have security updates in them and are vital for keeping your system secure.',
        html.Br(),
        f'Your Mean time to patch, that is mean time from when you downloaded a patch until it was successfully installed was:',
        html.Br(),
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Div([dcc.Graph(figure=new_windows_version, style={'height': '600px', 'width': '100%'})]),
    html.Div([dcc.Graph(figure=patch_reboot_analysis, style={'height': '1000px', 'width': '100%'})]),
    html.Br(),
    html.P([
        'If you notice on the below graph that you have not been receiving updates recently (past month) this could be an indication there is an issue with your system patching.',
        html.Br(),
        'The Microsoft Defender Updates are very busy so you should see a lot of activity there, the Windows System update is your Monthly Patch Tuesday patches.',
        html.Br(),
        'The .NET Framework is less busy and the AntiMalware updates are only a few updates a year.',
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    training_modal_graph,
    dcc.Loading(id=f'loading-{model_id}', type='default', children = [
        dash_table.DataTable(
            id=f'{model_id}-table',
            style_cell=dict(textAlign='left', maxWidth='500px'),
            style_table={
                'overflow-y': 'hidden',
                'overflow-x': 'auto',
            },
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': '''
                line-height: 15px,
                max-height: 30px, min-height: 30px, height: 30px;
                display: block;
                overflow-y: hidden;
                '''
            }],
            export_format='csv',
            columns=[ {'name': i, 'id': i} for i in em_12_reboot_analysis.columns],
            data=em_12_reboot_analysis.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_12_reboot_analysis.to_dict('records')
            ],
            tooltip_duration=None,
            sort_action='native',
            sort_mode='single',
            filter_action='native',
            sort_by=[{'column_id': 'captured_at', 'direction': 'asc'}],
            page_size=10,
        ),
    ]),
])


@callback(
    Output(model_id, "is_open"),
    [Input(f"{model_id}-open-model", "n_clicks"), Input(f"{model_id}-close-modal", "n_clicks")],
    [State(model_id, "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        logger.info(f'{model_id} Help button pressed')
        return not is_open
    return is_open

@callback(
    Output(f"{model_id}-hidden-output", "children"),
    [Input(f"{model_id}-manage", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Manage button pressed')
        try:
            cf.run_powershell_command('Start-Process "ms-settings:windowsupdate"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""

