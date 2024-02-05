#!/usr/bin/env python
# EM-1 - Hardware asset register dashboard page which uses the data gathered from the EM_1_asset_register collection automation

from dash.dependencies import Input, Output, State
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from ping3 import ping
from scapy.all import ARP, Ether, srp
import dash_bootstrap_components as dbc

import utils.common_graph_functions as cgf
import EM_1_asset_register as ar
from utils.database_class import DatabaseManager
from utils.logger_config import configure_logger

logger = configure_logger(__name__)

def read_asset_register():
    with DatabaseManager() as db:
        logger.debug("Getting all the named assets")
        return(pd.read_sql_query("SELECT * FROM em_1_named_asset_register", db.conn))

def read_assets_found():
    with DatabaseManager() as db:
        logger.debug("Getting all the un-named assets, that have not been added to the register")
        return(pd.read_sql_query("SELECT A.* FROM em_1_asset_register A LEFT JOIN em_1_named_asset_register B ON A.mac = B.mac WHERE B.mac IS NULL;", db.conn))

def read_total_asset_register():
    with DatabaseManager() as db:
        logger.debug("Getting all the assets")
        return(pd.read_sql_query("SELECT * FROM em_1_asset_register", db.conn))

def read_os_matches():
    with DatabaseManager() as db:
        logger.debug("Reading all from the os_matches SQL table")
        return(pd.read_sql_query("SELECT * FROM em_1_os_matches", db.conn))

asset_register = read_asset_register()
assets_found = read_assets_found()
total_assets_found = read_total_asset_register()


def is_ip_live(ip_address, original_dataframe):
    print(f'Running ARP on {ip_address}')
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, pdst=ip_address)
    answered, unanswered = srp(arp_request, timeout=1, verbose=False)
    
    for sent, received in answered:
        print(f"IP: {received.psrc} - MAC: {received.hwsrc}")
        if received.psrc == ip_address:
            mac_address = received.hwsrc.upper()
            print(f"MAC found: {mac_address}, MAC in Dataframe: {original_dataframe.loc[original_dataframe['ip'] == ip_address, 'mac'].values}")
            # Compare the discovered MAC address with the MAC addresses in the original DataFrame
            if mac_address in original_dataframe.loc[original_dataframe['ip'] == ip_address, 'mac'].values:
                #print(f"MAC found: {mac_address}, MAC in Dataframe: {original_dataframe.loc[original_dataframe['ip'] == ip_address, 'mac'].values}")
                response = ping(ip_address)
                if isinstance(response, float):
                    return 'Live'
                else:
                    return 'Not Live'
    response = ping(ip_address)
    if isinstance(response, float):
        return 'Live'
    else:
        return 'Not Live' 


def update_live_status(dataframe):
    if dataframe is None or dataframe.empty:
        print(f'The dataframe is empty')
        return dataframe
    dataframe['Live Status'] = dataframe['ip'].apply(lambda x: is_ip_live(x, dataframe))
    return dataframe


def calculate_metric_totals(em_1_asset_register, em_1_named_asset_register):
    '''
    This function will calculate the totals for our metrics and present it in:
    Total Assets
    Total Named assets
    % of named assets
    '''
    def _percentage(part, whole):
        if whole == 0:
            return
        return (float(part) / float(whole))

    asset_subplot = make_subplots(
        rows = 2,
        cols = 2,
        specs = [[{'type': 'indicator', 'colspan': 2},None], [{'type': 'indicator'},{'type': 'indicator'}]],
    )
    asset_subplot.add_trace(go.Indicator(mode='number', value=_percentage(len(em_1_named_asset_register.index), len(em_1_asset_register.index)), number={'valueformat': '.0%'}, title={'text': f'Percentage of assets named'}), row=1, col=1)
    asset_subplot.add_trace(go.Indicator(mode='number', value=len(em_1_asset_register.index), title={'text': f'Total number of assets found'}), row=2, col=1)
    asset_subplot.add_trace(go.Indicator(mode='number', value=len(em_1_named_asset_register.index), title={'text': f'Total number of assets named'}), row=2, col=2)
    
    return(asset_subplot)


model_id = 'em_1_asset_register'
training_modal_graph = cgf.training_modal(model_id, 'Name Assets Help', 'assets/asset_name_help.mp4')

layout = html.Div([
    html.H2('Asset register', style={'textAlign': 'center'}),
    html.Br(),
    cgf.gen_button_1('Named Asset Help', model_id),
    html.A(
        dbc.Button("Asset Register Advice", id=f"{model_id}-help", color="danger", n_clicks=0, style= {
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '230px',
            'background-color': 'red !important',
            }),
            href=f'https://www.ncsc.gov.uk/guidance/asset-management',
            target="_blank"
    ),
    html.Div(id=f'{model_id}-dummy-div', style={'display': 'none'}),
    training_modal_graph,
    html.P('A physical asset register is used to track hardware in your internal network. This top register is your named (known devices).', style={'textAlign': 'center'}),
    dcc.Loading(id='loading-metrics-totals', type='default', children=[dcc.Graph(id='metrics-totals')]),
    dcc.Loading(id='loading-asset-register', type='default', children = [
        dash_table.DataTable(
            id='asset-register',
            columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Asset Name', 'id': 'asset_name', 'editable': True},
            {'name': 'MAC', 'id': 'mac'},
            {'name': 'IP', 'id': 'ip'},
            {'name': 'Vendor', 'id': 'vendor', 'editable': True},
            {'name': 'OS', 'id': 'os', 'editable': True},
            {'name': 'Confidence', 'id': 'confidence', 'editable': True},
            {'name': 'CPE', 'id': 'cpe', 'editable': True},
            {'name': 'Notes', 'id': 'notes', 'editable': True},
            {'name': 'Added On', 'id': 'created_at'},
        ],
            row_selectable="multi",
            data=asset_register.to_dict('records'),
        ),
    ]),
    html.Br(),
    html.P([
        'This table is the assets found on your primary subnet in your environment. The three buttons below will help you identify, add and remove assets to your known devices register.',
        html.Br(),
        'The Scan New Assets button take some time to complete so please be patient, this is running a full port scan on your internal subnet looking for hosts.',
        ], style={'textAlign': 'center'}
    ),
    html.Div(id='table-edits', style={'display': 'none'}),
    #html.Div(id='page-refresh', children=str(datetime.datetime.now()), style={'display': 'none'}),
    html.Div(id='output-div'),
    html.Div([
        html.Button('Ping Assets', id='ping-assets', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Scan New Assets', id='scan-assets', n_clicks=0, style={'marginRight': '10px'}),
        html.Button('Delete Selected Rows', id='delete-selected-rows', n_clicks=0, style={'marginRight': '10px'})
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
    dcc.Loading(id='loading-assets_found', type='default', children = [
        dash_table.DataTable(
            id='assets_found',
            columns=[
                {'name': 'Asset Name', 'id': 'asset_name', 'editable': True},
                {'name': 'MAC', 'id': 'mac'},
                {'name': 'IP', 'id': 'ip'},
                {'name': 'Vendor', 'id': 'vendor'},
                {'name': 'OS', 'id': 'os'},
                {'name': 'Confidence', 'id': 'confidence'},
                {'name': 'CPE', 'id': 'cpe'},
                {'name': 'Found On', 'id': 'created_at'},
                {'name': 'Live Status', 'id': 'Live Status'},
            ],
            data=assets_found.to_dict('records'),
                    style_data_conditional=[
                {
                    'if': {'filter_query': '{Live Status} eq "Live"'},
                    'backgroundColor': 'green',
                    'color': 'white',
                },
                {
                    'if': {'filter_query': '{Live Status} eq "Not Live"'},
                    'backgroundColor': 'red',
                    'color': 'white',
                },
            ],
        ),
    ]),
    html.Br(),
    html.P('This next table is a list of the possible OS matches from the NMAP scan, you can use this to populate the asset register if you believer there is a match', style={'textAlign': 'center'}),
    html.Div([
        html.Button('Show OS matches', id='os-matches', n_clicks=0, style={'marginRight': '10px'}),
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
    html.Div(id='os-matches-table')
])


@callback(
    [
        Output('assets_found', 'data'), 
        Output('asset-register', 'data'),
        Output('asset-register', 'selected_rows'),
        Output('metrics-totals', component_property='figure')
    ],
    [
        Input('ping-assets', 'n_clicks'),
        Input('scan-assets', 'n_clicks'),
        Input('delete-selected-rows', 'n_clicks'),
        Input('assets_found', 'data')
    ],
    [
        State('assets_found', 'data_previous'),
        State('asset-register', 'selected_rows'),
        State('asset-register', 'data')
    ]
)
def combined_callback(n_clicks_ping, n_clicks_scan, n_clicks_delete_selected_rows, current_data, previous_data, selected_rows, asset_register):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'ping-assets':
        if n_clicks_ping > 0:
            df_updated = update_live_status(pd.DataFrame(current_data).copy())
            return df_updated.to_dict('records'), \
                dash.no_update, \
                [], \
                calculate_metric_totals(pd.DataFrame(total_assets_found).copy(), read_asset_register())

    elif trigger_id == 'scan-assets':
            if n_clicks_scan > 0:
                ar.run_port_scan()
                return read_assets_found().to_dict('records'), \
                read_asset_register().to_dict('records'), \
                [], \
                calculate_metric_totals(pd.DataFrame(total_assets_found).copy(), read_asset_register())

    elif trigger_id == 'delete-selected-rows':
        if n_clicks_delete_selected_rows > 0:
            for i in sorted(selected_rows, reverse=True):
                mac_to_delete = asset_register[i]['mac']
                print(mac_to_delete)
                with DatabaseManager() as db:
                    db.execute_query('DELETE FROM em_1_named_asset_register WHERE mac=?', (mac_to_delete,))
                    
            return read_assets_found().to_dict('records'), \
            read_asset_register().to_dict('records'), \
            [], \
            calculate_metric_totals(pd.DataFrame(total_assets_found).copy(), \
            read_asset_register())
    
    if previous_data is None:
        return dash.no_update, \
        dash.no_update, \
        [], \
        calculate_metric_totals(pd.DataFrame(total_assets_found).copy(), read_asset_register())
    
    df_updated = pd.DataFrame(current_data).copy()
    edited_data = df_updated.to_dict('records')

    for i, row in enumerate(edited_data):
        previous_name = previous_data[i].get('asset_name')
        if previous_name is not None and row['asset_name'] != previous_name:
            df_updated.at[i, 'asset_name'] = row['asset_name']
    
    df_cleaned = df_updated[df_updated['asset_name'] != '']
    if 'Live Status' in df_cleaned.columns:
        df_cleaned = df_cleaned.drop(columns='Live Status')
    df_cleaned = df_cleaned.drop(columns='created_at')

    with DatabaseManager() as db:
        db.add_new_rows('em_1_named_asset_register', df_cleaned, ['mac'])
    
    return read_assets_found().to_dict('records'), \
        read_asset_register().to_dict('records'), \
        [], calculate_metric_totals(pd.DataFrame(total_assets_found).copy(), read_asset_register())



# Update cells in the asset table and database
@callback(
    Output("table-edits", "children"),
    [Input('asset-register', 'data' )],
    [State('asset-register', 'data_previous')]
)
def detect_edits(curr_data, prev_data):
    if not prev_data:
        raise dash.exceptions.PreventUpdate

    # Logic to identify which cell(s) changed
    for i, (prev_row, curr_row) in enumerate(zip(prev_data, curr_data)):
        for col in curr_row:
            if prev_row[col] != curr_row[col]:
                mac_value = curr_row.get('mac', 'MAC column not found in this row')
                with DatabaseManager() as db:
                    db.execute_query(f"UPDATE em_1_named_asset_register SET {col}='{curr_row[col]}' WHERE mac='{mac_value}';")
                return ''
    return ''


@callback(
    Output('os-matches-table', 'children'),
    [Input('os-matches', 'n_clicks')]
)
def display_table(n_clicks):
    if n_clicks and n_clicks % 2 != 0:
        return dash_table.DataTable(
            data=read_os_matches().to_dict('records'),
            columns=[{'name': col, 'id': col} for col in read_os_matches().columns],
            filter_action='native',
            sort_action='native'
        )
    else:
        return []


@callback(
    Output(model_id, "is_open"),
    [Input(f"{model_id}-b1", "n_clicks"), Input(f"{model_id}-close-modal", "n_clicks")],
    [State(model_id, "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        logger.info(f'{model_id} Help button pressed')
        return not is_open
    return is_open


@callback(
    Output(f'{model_id}-dummy-div', 'children'),
    [Input(f"{model_id}-help", "n_clicks")]
)
def toggle_modal(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Advice button pressed')
        return ""
    return ""
