#!/usr/bin/env python
# EM-8 - WiFi password settings display page, this will present all WiFi password strengths and suggest updates if they are not ideal

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context

import dash_bootstrap_components as dbc
import utils.common_graph_functions as cgf
import EM_1_asset_register as ar

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_8_wlan_settings = db.read_database_table('em_8_wlan_settings')

model_id = 'em_8_wlan_settings'
training_modal_graph = cgf.training_modal(model_id, 'WLAN Settings', 'https://www.youtube-nocookie.com/embed/CCWS6qQ1k5k?si=oZzQdxrB30D3MeeW')
router_settings_model = cgf.training_modal(f'{model_id}-router-settings', 'Router Settings', 'https://www.youtube-nocookie.com/embed/mJnIgjyjEtc?si=2Cx_VuZ0JXJDa4a7&amp;start=132')

gateway_url = ar.get_default_gateway()


layout = html.Div([
    html.H2('WiFi Management', style={'textAlign': 'center'}),
    dbc.Button("WiFi Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Router Help", id=f"{model_id}-open-router-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
    }),
    html.A(
        dbc.Button("Connect to Router", id=f"{model_id}-manage", color="secondary", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '450px'
        }),
        href=f'http://{gateway_url}',
        target="_blank"
    ),
    html.Div(id=f'{model_id}-dummy-div', style={'display': 'none'}),
    html.Br(),
    html.P([
        'Your WiFi password is the frontdoor to your network and should be complex and not easily guessable.',
        html.Br(),
        'If your password does not present as "Strongest" you could make your home more secure by setting a more complex password.',
        html.Br(),
        'The Password Complexity of you WiFi settings is currently:',
        html.Br(),
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    training_modal_graph,
    router_settings_model,
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
            columns=[ {'name': i, 'id': i} for i in em_8_wlan_settings.columns],
            data=em_8_wlan_settings.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_8_wlan_settings.to_dict('records')
            ],
            tooltip_duration=None,
            sort_action='native',
            sort_mode='single',
            filter_action='native',
            sort_by=[{'column_id': 'captured_at', 'direction': 'asc'}],
            page_size=10,
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{PasswordStrength} = "Strongest"',
                },
                'backgroundColor': 'green',
                'color': 'white'
                }
            ],
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
        logger.info(f'{model_id} WiFi Help button pressed')
        return not is_open
    return is_open

@callback(
    Output(f"{model_id}-router-settings", "is_open"),
    [Input(f"{model_id}-open-router-model", "n_clicks"), Input(f"{model_id}-router-settings-close-modal", "n_clicks")],
    [State(f"{model_id}-router-settings", "is_open")],
)
def toggle_router_modal(n1, n2, is_open):
    if n1 or n2:
        logger.info(f'{model_id} Router Help button pressed')
        return not is_open
    return is_open

@callback(
    Output(f'{model_id}-dummy-div', 'children'),
    [Input(f"{model_id}-manage", "n_clicks")]
)
def toggle_modal(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Connect to router pressed')
        return ""
    return ""
