#!/usr/bin/env python
# EM-13 - Antivirus test against the system
# EM-14 - Threat scanning data presentation
# We decided to group these together as the data makes sense to present together as they are both from windows Defender and Windows threat scanning

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context, dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pytz
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_13_eicar_removed = db.read_database_table('em_13_eicar_removed')


def get_em_14_threat_scanning():
    with DatabaseManager() as db:
        em_14_threat_scanning = db.read_database_table('em_14_threat_scanning')
    return em_14_threat_scanning

em_14_threat_scanning = get_em_14_threat_scanning()

def gen_scatter_file_removed_over_time(df):
    try:
        fig = px.scatter(df, x='created_at', y='Removed', title='EICAR File Removal Over Time')
        fig.update_layout(xaxis_title='File Removed Date', yaxis_title='Removed Success/ Failed')
        return(fig)
    except Exception as e:
        logger.error(f'The scatter graph graph could not be rendered, sending back generic graph: {e}')
        cgf.set_no_results_found_figure()


def gen_button_color(df):
    try:
        most_recent = df.sort_values(by='created_at', ascending=False).iloc[0]
        setting_enabled = most_recent['Removed']
        button_color = 'success' if setting_enabled == 'Success' else 'danger'
        status_text = 'Enabled' if setting_enabled == 'Success' else 'Disabled'
    except Exception as e:
        logger.error(f'Could not set button color, returning Disabled: {e}')
        button_color = 'danger'
        status_text = 'Disabled'
    return(dbc.Button(status_text, id='eicar-removed', color=button_color, className='mr-1', disabled=True))


def gen_threat_count_over_time(df):
    try:
        df['InitialDetectionTime'] = pd.to_datetime(df['InitialDetectionTime'])
        threat_count_per_day = df.groupby(df['InitialDetectionTime'].dt.date).size()

        threat_count_df = threat_count_per_day.reset_index()
        threat_count_df.columns = ['Date', 'Threat Count']
        fig = px.scatter(threat_count_df, x='Date', y='Threat Count', size='Threat Count', title='Total Threat Counts Over Time')
        return(fig)
    except Exception as e:
        logger.error(f'The scatter graph graph could not be rendered, sending back generic graph: {e}')
        cgf.set_no_results_found_figure()


model_id = 'em_13_eicar_removed'
scatter_antivirus_working = gen_scatter_file_removed_over_time(em_13_eicar_removed)
threat_count_over_time = gen_threat_count_over_time(em_14_threat_scanning)


layout = html.Div([
    dcc.Interval(
        id='refresh-dashboard',
        interval=1*60*1000,  # in milliseconds, 1*60*1000 for 1 minute
        n_intervals=0
    ),
    html.A(
        dbc.Button("AntiVirus EICAR Help", id=f"{model_id}-help", color="danger", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '10px'
    }),
    href=f'https://www.eicar.org/download-anti-malware-testfile/',
    target="_blank"
    ),
    html.Div(id=f'{model_id}-dummy-div', style={'display': 'none'}),
    dbc.Button("Manage AntiVirus", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.H2('AntiVirus/ Threat Management', style={'textAlign': 'center'}),
    html.P([
        'Regularly testing your AntiVirus to ensure it is enabled and working is a good idea.',
        html.Br(),
        'We are using the EICAR file to test your system and ensure that you have AntiVirus enabled',
        html.Br(),
        'Our last run shows that your Antivirus was:',
        html.Br(),
        gen_button_color(em_13_eicar_removed)
        ],
        style={'textAlign': 'center'}
    ),
    html.Div(id='threats-found'),
    html.Div([dcc.Graph(figure=scatter_antivirus_working)]),
    html.Br(),
    html.P([
        'This will show you your threats over time, you should not see many threats in this graph, if you do your daily practices are tripping Microsoft Defender.',
        html.Br(),
        'You may need to either configure Defender to allow the action or if you are not seeing many events that is great and you may not need to do anything.',
        html.Div([dcc.Graph(figure=threat_count_over_time)]),
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    html.H4("These are the EICAR database entries, the above graphs are generated from", style={'textAlign': 'center'}),
    dcc.Loading(id=f'loading-{model_id}-eicar', type='default', children = [
        cgf.generate_dash_table(em_13_eicar_removed, 'em_13_eicar_removed')
    ]),
    html.H4("These are the Threat Database entries the above graphs are generated from", style={'textAlign': 'center'}),
    dcc.Loading(id=f'loading-{model_id}', type='default', children = [
        cgf.generate_dash_table(em_14_threat_scanning, 'em_14_threat_scanning')
    ]),
])


@callback(
    Output('threats-found', 'children'),
    Input('refresh-dashboard', 'n_intervals')
)
def refresh_table(n):    
    df = get_em_14_threat_scanning()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_localize('UTC')
    now_utc = datetime.now(pytz.utc)
    seven_days_ago = now_utc - timedelta(days=7)
    df = df[df['created_at'] >= seven_days_ago]
    if df.empty:
        return html.H4(f"We found {len(df)} new threats over the past week, Great Job.", style={'textAlign': 'center'})
    else:
        return html.H4(f"We found {len(df)} new threats over the past week:", style={'textAlign': 'center'}), cgf.generate_dash_table(df, 'em_14_threats_found_past_week')


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
            cf.run_powershell_command('Start-Process "windowsdefender://threat"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""