#!/usr/bin/env python
# EM-6 - Defender Updates webpage, this will show data collected from the EM_6_defender_updates automation

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_6_defender_updates = db.read_database_table('em_6_defender_updates')


def generate_line_updates(df):
    try:
        antispyware_updates = pd.DataFrame(df['AntispywareSignatureLastUpdated'].unique(), columns=['AntispywareSignatureLastUpdated'])
        antivirus_updates = pd.DataFrame(df['AntivirusSignatureLastUpdated'].unique(), columns=['AntivirusSignatureLastUpdated'])
        nis_updates = pd.DataFrame(df['NISSignatureLastUpdated'].unique(), columns=['NISSignatureLastUpdated'])
        quickscan_updates = pd.DataFrame(df['QuickScanEndTime'].unique(), columns=['QuickScanEndTime'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=antispyware_updates.index, x=antispyware_updates['AntispywareSignatureLastUpdated'], mode='lines', name='Antispyware Signature Last Updated'))
        fig.add_trace(go.Scatter(y=antivirus_updates.index, x=antivirus_updates['AntivirusSignatureLastUpdated'], mode='lines', name='Antivirus Signature Last Updated'))
        fig.add_trace(go.Scatter(y=nis_updates.index, x=nis_updates['NISSignatureLastUpdated'], mode='lines', name='NIS Signature Last Updated'))
        fig.add_trace(go.Scatter(y=quickscan_updates.index, x=quickscan_updates['QuickScanEndTime'], mode='lines', name='Quick Scan End Time'))
        fig.update_layout(title='Defender Signiture Updates and Scan times', xaxis_title='Date installed/ Scanned', yaxis_title='Incremental updates')
        return(fig)
    except Exception as e:
        logger.error(f'The line chart could not be rendered, sending back generic error: {e}')
        cgf.set_no_results_found_figure()


def gen_defender_enabled(df):
    try:
        fig = make_subplots(rows=3, cols=3, subplot_titles=(
            "Anti Malware Service Enabled",
            "AntiSpyware Enabled",
            "AntiVirus Enabled",
            "Behavior Monitor Enabled",
            "Ioav Protection Enabled (Scans Downloaded files)",
            "Tamper Protection Enabled",
            "Network Inspection Service Enabled",
            "On Access Protection Enabled",
            "Real Time Protection Enabled"
            ),
            specs = [
                [{'type': 'scatter'},{'type': 'scatter'},{'type': 'scatter'}],
                [{'type': 'scatter'},{'type': 'scatter'},{'type': 'scatter'}],
                [{'type': 'scatter'},{'type': 'scatter'},{'type': 'scatter'}]
                ])


        fig.add_trace(go.Scatter(x=df['created_at'], y=df['AMServiceEnabled'], mode='lines'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['AntispywareEnabled'], mode='lines'), row=1, col=2)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['AntivirusEnabled'], mode='lines'), row=1, col=3)

        fig.add_trace(go.Scatter(x=df['created_at'], y=df['BehaviorMonitorEnabled'], mode='lines'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['IoavProtectionEnabled'], mode='lines'), row=2, col=2)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['IsTamperProtected'], mode='lines'), row=2, col=3)

        fig.add_trace(go.Scatter(x=df['created_at'], y=df['NISEnabled'], mode='lines'), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['OnAccessProtectionEnabled'], mode='lines'), row=3, col=2)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['RealTimeProtectionEnabled'], mode='lines'), row=3, col=3)

        for row in range(1, 4):
            for col in range(1, 4):
                fig.update_yaxes(tickvals=[1], ticktext=['True'], row=row, col=col)

        fig.update_layout(height=600, width=1900, title_text="Enabled Defender Services Over Time (This should always be enabled)")
        return(fig)
    except Exception as e:
        logger.error(f'The line chart could not be rendered, sending back generic error: {e}')
        cgf.set_no_results_found_figure()


model_id = 'em_6_defender_updates'
training_modal_graph = cgf.training_modal(model_id, 'Defender Management', 'https://www.youtube-nocookie.com/embed/yXPWDAH1emo?si=0JCek1kWpDpP8Dqi')
windows_updates = generate_line_updates(em_6_defender_updates)
defender_enabled = gen_defender_enabled(em_6_defender_updates)

layout = html.Div([
    html.H2('Defender Management', style={'textAlign': 'center'}),
    dbc.Button("Defender Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Defender", id=f"{model_id}-manage", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Microsoft Defender is an inbuilt antivirus and antimalware solution, if you do not have any other after market solution this should be always enabled.',
        html.Br(),
        'If you notice this has ever been disabled this is an indication something may be interfering with your system security.'
        ],
        style={'textAlign': 'center'}
    ),
    html.Div([dcc.Graph(figure=defender_enabled)]),
    html.Div([dcc.Graph(figure=windows_updates)]),
    html.P([
        'If you notice one of the above settings are disabled and do not know how to enable the setting after going through the Defender Help video Powershell can be used to manage these settings.',
        html.Br(),
        'Open Powershell as Administrator by right clicking on Powershell and clicking "Run As Administrator".',
        html.Br(),
        '# Enable Real-Time Protection',
        html.Br(),
        'Set-MpPreference -DisableRealtimeMonitoring $false',
        html.Br(),
        '# Enable Behavior Monitoring',
        html.Br(),
        'Set-MpPreference -DisableBehaviorMonitoring $false',
        html.Br(),
        '# Enable IOAV Protection',
        html.Br(),
        'Set-MpPreference -DisableIOAVProtection $false',
        html.Br(),
        '# Enable Intrusion Prevention System (NIS)',
        html.Br(),
        'Set-MpPreference -DisableIntrusionPreventionSystem $false',
        html.Br(),
        'Etc.'
        ],
        style={'textAlign': 'center'}
    ),
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
            columns=[ {'name': i, 'id': i} for i in em_6_defender_updates.columns],
            data=em_6_defender_updates.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_6_defender_updates.to_dict('records')
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
        return not is_open
    return is_open

@callback(
    Output(f"{model_id}-hidden-output", "children"),
    [Input(f"{model_id}-manage", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        try:
            cf.run_powershell_command('Start-Process "windowsdefender://threat"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""
