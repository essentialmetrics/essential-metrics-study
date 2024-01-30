#!/usr/bin/env python
# EM-19 - USBs attached, this present all attached USBs to the system

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, callback_context
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime, timedelta

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_19_usb_devices = db.read_database_table('em_19_usb_devices')

def new_devices(df):
    try:
        current_date = datetime.now()
        one_week_back = current_date - timedelta(days=7)
        df['created_at'] = pd.to_datetime(df['created_at'])
        new_devices = df[df['created_at'] > one_week_back]
        return(new_devices)
    except Exception as e:
        logger.error(f'Could not get new USB devices: {e}')
        return(pd.DataFrame())
    


model_id = 'em_19_usb_devices'
new_usb_devices = new_devices(em_19_usb_devices)

training_modal_graph = cgf.training_modal(model_id, 'USB Restriction Policy', 'https://www.youtube-nocookie.com/embed/8VOYV4Po_fs?si=Y-8Kga_rRx0MtJXG')

layout = html.Div([
    dbc.Button("USB Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage USB Settings", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    training_modal_graph,
    html.H2('USB Devices connected to your system', style={'textAlign': 'center'}),
    html.P([
        'This list is all the USB devices that have ever been connected to your system.',
        html.Br(),
        'This should be a pretty static list, unexpected new items that show up here should be investigated.',
        html.Br(),
        f'We found {len(new_usb_devices)} new USB devices over the past week:',
        html.Br(),
        cgf.generate_dash_table(new_usb_devices, 'new_usb_devices')
        ],
        style={'textAlign': 'center'}
    ),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    html.H4("These are all the USB devices we have found on your system", style={'textAlign': 'center'}),
        html.P([
        'We can use the Vendor ID (Vid) and Product ID (Pid) to check who the manufacturer was for your device, we can also check the product associated with the Pid',
        html.Br(),
        'We have downloaded a database of the most known Pids and Vids and are performing that lookup here.',
        html.Br(),
        'You can perform your own lookups here: ',
        html.A('USB lookup', href=f'http://www.linux-usb.org/usb.ids', target="_blank"),
        ],
        style={'textAlign': 'center'}
    ),
    dcc.Loading(id=f'loading-{model_id}-eicar', type='default', children = [
        cgf.generate_dash_table(em_19_usb_devices, 'em_19_usb_devices')
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
            cf.run_powershell_command('gpedit.msc')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""