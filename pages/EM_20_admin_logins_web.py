#!/usr/bin/env python
# EM-20 - admin logins to the system, group and user management

from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

import utils.common_functions as cf
import utils.common_graph_functions as cgf
from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_20_admin_logins = db.read_database_table('em_20_admin_logins')

with DatabaseManager() as db:
    em_20_users = db.read_database_table('em_20_users')

em_20_users['account_disabled_int'] = em_20_users['account_disabled'].map({'True': 1, 'False': 0})


def generate_admin_logins(df, df_users):
    '''
    This function will generate two graphs from the event ID that were collected from the event log
    The first is a timeline graph of the login and logout times and the associated users
    The second is a pie chart detailing the % of time each user spends on the system
    '''
    try:
        # This merge will get all user account logins and drop all system logins as we are merging on the users SID
        df = pd.merge(df, df_users, left_on='Uid', right_on='sid')

        df = df[['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'TimeGenerated', 'priv']]

        def append_priv(user, priv):
            if priv == '2':
                return f'{user} (admin)'
            elif priv == '1':
                return f'{user} (user)'
            else:
                return f'{user} ({priv})'

        # Apply this function to each row in the DataFrame as I need the privileges of the user which I am presenting with
        df['User'] = df.apply(lambda row: append_priv(row['User'], row['priv']), axis=1)

        df.loc[:, 'TimeGenerated'] = df['TimeGenerated'].str[:-4]
        df.loc[:, 'TimeGenerated'] = pd.to_datetime(df['TimeGenerated'], format='%Y%m%d%H%M%S.%f')

        df = df.sort_values('RecordNumber')
        df = df.reset_index(drop=True)

        results = []

        for i, row in df.iterrows():
            if row['EventIdentifier'] == '4624':
                logon_id = row['LogonID']
                start_time = row['TimeGenerated']
                
                # Search for the matching LogonID starting from the next row
                for forward_row in df.iloc[i+1:].itertuples():
                    if forward_row.LogonID == logon_id:
                        end_time = forward_row.TimeGenerated
                        time_diff = end_time - start_time
                        
                        # Add the record to the results list
                        results.append([row['RecordNumber'], row['User'], row['LogonType'],
                                        row['EventIdentifier'], row['LogonID'], row['ElevatedToken'],
                                        start_time, end_time, time_diff])
                        break


        results_df = pd.DataFrame(results, columns=['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'StartTime', 'EndTime', 'TimeDifference'])
        '''
        I need to drop any login that is below 2 seconds because the system logs in and rapidly logs back out on every user login
        This tracks as imperceptibly small time differences of less than 1 second (usually around .3 of a second)
        Tt also skews the graphs and does not add any value as it is not user login tracking sessions, it is only event based data that we can drop here
        '''
        results_df = results_df[results_df['TimeDifference'] > pd.Timedelta(seconds=2)]
        try:
            results_df.loc[results_df['LogonType'] == '10', 'LogonType'] = '10 RDP'
            results_df.loc[results_df['LogonType'] == '3', 'LogonType'] = '3 Network'
            results_df.loc[results_df['LogonType'] == '2', 'LogonType'] = '2 Interactive'
        except Exception as e:
            logger.error(f'Could not generate logon types as part of the figure: {e}')

        timeline_fig = px.timeline(results_df, x_start="StartTime", x_end="EndTime", y="User", color="LogonType",
                        title="Login Events Timeline (This does not track sleep or hibernation events so if you use them this will not update until a logout)")
        timeline_fig.update_yaxes(autorange="reversed")

        results_df['DurationSeconds'] = results_df['TimeDifference'].dt.total_seconds()
        sum_duration_per_user = results_df.groupby('User')['DurationSeconds'].sum()

        total_duration = sum_duration_per_user.sum()
        percentage_duration_per_user = (sum_duration_per_user / total_duration) * 100

        percentage_fig = px.pie(percentage_duration_per_user, 
                    values=percentage_duration_per_user, 
                    names=percentage_duration_per_user.index, 
                    title='Percentage of Total Duration by User')
        
        return(timeline_fig, percentage_fig)
    except Exception as e:
        logger.error(f'Could not render the users and groups graphs, returning generic graphs: {e}')
        return(cgf.set_no_results_found_figure(), cgf.set_no_results_found_figure())


timeline_fig, percentage_fig = generate_admin_logins(em_20_admin_logins, em_20_users)
model_id = 'em_20_admin_logins'

layout = html.Div([
    html.A(
        dbc.Button("Admin User Advice", id=f"{model_id}-help", color="danger", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '10px'
        }),
        href=f'https://cybersmart.co.uk/blog/whats-the-difference-between-users-and-admin-users/',
        target="_blank"
    ),
    html.Div(id=f'{model_id}-dummy-div', style={'display': 'none'}),
    dbc.Button("Manage Users", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.H2('Users/ Groups and Admin logins', style={'textAlign': 'center'}),
    html.P([
        'On this page we are tracking all the users and groups on the system.',
        html.Br(),
        f'You currently have {len(em_20_users)} users on the system with {em_20_users["account_disabled_int"].sum()} Disabled and {len(em_20_users) - em_20_users["account_disabled_int"].sum()} Enabled.',
        html.Br(),
        html.H3('This is a list of your users on the system'),
        'The important colunm here is the priv colunm 2=admin, 1=user, 0=no-permissions',
        html.Br(),
        'The DefaultAccount, Administrator and Guest account should be disabled, if any of these accounts are Enabled you should disable them as they are not needed.',
        cgf.generate_dash_table(em_20_users, 'em_20_users', style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{priv} = "2" AND {account_disabled} = "False"',
                    },
                'backgroundColor': 'red',
                'color': 'white'
                },
                                {
                    'if': {
                        'filter_query': '{priv} = "1" AND {account_disabled} = "False"',
                    },
                'backgroundColor': 'green',
                'color': 'white'
                },
            ]),
        html.Br(),
        html.H3('User login tracking'),
        'Here we are tracking all the user logins to determine if you use an administrator account or a regular account for your day to day activities.',
        html.Br(),
        'Using an administrator account for your day to day work is generally a bad idea, this makes explotition of your system much easier for an attacker.',
        html.Br(),
        html.A('BeyondTrust', href=f'https://assets.beyondtrust.com/assets/documents/BeyondTrust-Microsoft-Vulnerabilities-Report-2021.pdf', target="_blank"),
        f' found 70% of all critical windows vulneribilities would have been mitigated by removing admin rights.',
        html.Div([dcc.Graph(figure=timeline_fig, style={'height': '800px', 'width': '100%'})]),
        html.Div([dcc.Graph(figure=percentage_fig, style={'height': '800px', 'width': '100%'})]),
        html.Br(),
        html.H4("These are all the raw login events for your system"),
        'There are many system login events we are not presenting in the graphs above. Windows uses system accounts to perform actions and they are tracked',
        cgf.generate_dash_table(em_20_admin_logins, 'em_20_admin_logins'),
        ],
        style={'textAlign': 'center'}
    ),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
])


@callback(
    Output(f'{model_id}-dummy-div', 'children'),
    [Input(f"{model_id}-help", "n_clicks")]
)
def toggle_modal(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Advice button pressed')
        return ""
    return ""


@callback(
    Output(f"{model_id}-hidden-output", "children"),
    [Input(f"{model_id}-manage", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Manage button pressed')
        try:
            cf.run_powershell_command('control.exe /name Microsoft.UserAccounts')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""
