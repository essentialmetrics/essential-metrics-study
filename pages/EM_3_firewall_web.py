#!/usr/bin/env python
# EM-3 - Firewall dashboard webpage which displays the data captured by EM_3_firewall
# https://www.youtube.com/watch?v=b5YODEKsOrA

from dash.dependencies import Input, Output, State
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

def firewall_enabled_subplot(em_3_firewall_enabled):
    try:
        em_3_firewall_enabled['Enabled'] = em_3_firewall_enabled['Enabled'].map({'True': 1, 'False': 0})
        em_3_firewall_enabled['created_at'] = pd.to_datetime(em_3_firewall_enabled['created_at'])

        df_domain = em_3_firewall_enabled[em_3_firewall_enabled['Profile'] == 'Domain']
        df_private = em_3_firewall_enabled[em_3_firewall_enabled['Profile'] == 'Private']
        df_public = em_3_firewall_enabled[em_3_firewall_enabled['Profile'] == 'Public']

        fig = make_subplots(rows=2, cols=2, subplot_titles=("Public Profile", "Private Profile", "Domain Profile"), specs = [[{'type': 'scatter', 'colspan': 2},None], [{'type': 'scatter'},{'type': 'scatter'}]])

        fig.add_trace(go.Scatter(x=df_public['created_at'], y=df_public['Enabled'], mode='lines', name='Public'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_private['created_at'], y=df_private['Enabled'], mode='lines', name='Private'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_domain['created_at'], y=df_domain['Enabled'], mode='lines', name='Domain'), row=2, col=2)

        fig.update_yaxes(tickvals=[0, 1], ticktext=['False', 'True'], row=1, col=1)
        fig.update_yaxes(tickvals=[0, 1], ticktext=['False', 'True'], row=2, col=1)
        fig.update_yaxes(tickvals=[0, 1], ticktext=['False', 'True'], row=2, col=2)

        fig.update_layout(height=600, width=1900, title_text="Firewall Enabled Profile Status Over Time (This should always be enabled)")
        return(fig)
    except Exception as e:
        return(cgf.set_no_results_found_figure())


with DatabaseManager() as db:
    em_3_firewall_rules = db.read_database_table('em_3_firewall_rules')

with DatabaseManager() as db:
    em_3_firewall_rules_decommissioned = db.read_database_table('em_3_firewall_rules_decommissioned')

with DatabaseManager() as db:
    em_3_firewall_enabled = db.read_database_table('em_3_firewall_enabled')

firewall_enabled = firewall_enabled_subplot(em_3_firewall_enabled)

model_id = 'em_3_firewall'
training_modal_graph = cgf.training_modal(model_id, 'Firewall Rules Management', 'https://www.youtube.com/embed/b5YODEKsOrA?si=23f_L7PmXjmB2f4U')

firewall_rules_over_time = cgf.generate_line_graph_decoms(em_3_firewall_rules, em_3_firewall_rules_decommissioned, title='Firewall Rules found on system over time', yaxis='Total Firewall Rules')

layout = html.Div([
    html.H2('Firewall Rules', style={'textAlign': 'center'}),
    dbc.Button("Firewall Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Firewall Rules", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Firewall rules manage the connections to and from your system, they should always be enabled',
        html.Div([dcc.Graph(figure=firewall_enabled)])],
        style={'textAlign': 'center'}
    ),
    html.Div([dcc.Graph(figure=firewall_rules_over_time)]),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    training_modal_graph,
    dcc.Loading(id='loading-firewall-rules', type='default', children = [
        dash_table.DataTable(
            id='firewall-rules',
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
            columns=[
            {'name': 'Name', 'id': 'Name'},
            {'name': 'Display Name', 'id': 'DisplayName'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Display Group', 'id': 'DisplayGroup'},
            {'name': 'Enabled', 'id': 'Enabled'},
            {'name': 'Profile', 'id': 'Profile'},
            {'name': 'Direction', 'id': 'Direction'},
            {'name': 'Action', 'id': 'Action'},
            {'name': 'Captured at', 'id': 'created_at'},
            ],
            data=em_3_firewall_rules.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_3_firewall_rules.to_dict('records')
            ],
            tooltip_duration=None,  # Disable automatic hiding of tooltips
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
            cf.run_subprocess_command('wf.msc')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""
