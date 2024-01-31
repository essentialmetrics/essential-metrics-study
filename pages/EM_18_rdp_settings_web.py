#!/usr/bin/env python
# EM-18 - RDP settings and session details, this will track data from em_18_rdp_enabled table
# This will also show data from the logins table: em_20_admin_logins
# https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc732713(v=ws.11)
# https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc753488(v=ws.10)

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, callback_context
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_18_rdp_enabled = db.read_database_table('em_18_rdp_enabled')


def generate_rdp_subplot(df):
    try:
        df['created_at'] = pd.to_datetime(df['created_at'])

        fig = make_subplots(rows=1, cols=2, subplot_titles=("RDP Enabled (If not using this should be Disabled (False is good))", "NLA Enabled (Network Level Authentication) (This should be enabled)"), specs = [[{'type': 'scatter'},{'type': 'scatter'}]])

        fig.add_trace(go.Scatter(x=df['created_at'], y=df['RDPEnabled'], mode='lines', name='RDP Enabled'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['NLAEnabled'], mode='lines', name='NLA Enabled'), row=1, col=2)
        fig.update_yaxes(tickvals=[0, 1], ticktext=['False', 'True'], row=1, col=1)
        fig.update_yaxes(tickvals=[0, 1], ticktext=['False', 'True'], row=2, col=1)

        fig.update_layout(height=600, width=1900, title_text="RDP Settings enabled over time")
        return(fig)
    except Exception as e:
        return(cgf.set_no_results_found_figure())


model_id = 'em_18_rdp_enabled'
rdp_settings_enabled = generate_rdp_subplot(em_18_rdp_enabled)


layout = html.Div([
    dbc.Button("RDP Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage RDP Settings", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.H2('RDP Settings and sessions', style={'textAlign': 'center'}),
    html.P([
        'Remote Desktop (RDP) is a protocol used by Windows systems to allow remote management and access of windows systems.',
        html.Br(),
        'Because of the remote management functionality inbuilt in RDP this is a common protocol used by attackers and as such should be disabled if not in use and should be used securely if needed.',
        html.Br(),
        html.Div([dcc.Graph(figure=rdp_settings_enabled, style={'height': '600px', 'width': '100%'})]),
        ],
        style={'textAlign': 'center'}
    ),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    html.H4("These are the RDP settings and the users which are allowed to RDP to your system if it is enabled", style={'textAlign': 'center'}),
    dcc.Loading(id=f'loading-{model_id}-eicar', type='default', children = [
        cgf.generate_dash_table(em_18_rdp_enabled, 'em_18_rdp_enabled')
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
            cf.run_powershell_command('SystemPropertiesRemote')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""
