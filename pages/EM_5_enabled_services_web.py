#!/usr/bin/env python
# EM-5 - Enabled services webpage, this will show data collected from the EM_5_enabled_services automation

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger
from datetime import datetime, timedelta

logger = configure_logger(__name__)


with DatabaseManager() as db:
    em_5_enabled_services = db.read_database_table('em_5_enabled_services')

with DatabaseManager() as db:
    em_5_enabled_services_decommissioned = db.read_database_table('em_5_enabled_services_decommissioned')


def generate_pie_chart(df):
    '''
    This function will generate a pie chart from 3 items in a column
    '''
    try:
        # Get column totals for each item
        start_type_counts = df['StartType'].value_counts()
        df = start_type_counts.reset_index()
        df.columns = ['StartType', 'Count']
        
        colors = {
            "Manual": "yellow",
            "Automatic": "green",
            "Disabled": "red"
        }
        
        fig = px.pie(
            df, 
            names='StartType', 
            values='Count', 
            title='Distribution of Start Types',
            color='StartType',
            color_discrete_map=colors
        )
        return(fig)
    except Exception as e:
        logger.error(f'The pie chart could not be rendered, sending back generic error for the pie chart: {e}')
        cgf.set_no_results_found_figure()


def generate_subplot(df, df_decommissioned):
    try:
        current_date = datetime.now()
        one_week_back = current_date - timedelta(days=7)

        # I am removing the BITS service as Microsoft adds and removes this service several times an hour
        new_rows_last_week  = df[
            (df['ServiceName'] != 'BITS') &
            (df['created_at'] > one_week_back.strftime("%Y-%m-%d"))
        ]

        rows_removed_last_week = df_decommissioned[
            (df_decommissioned['ServiceName'] != 'BITS') &
            (df_decommissioned['created_at'] > one_week_back.strftime("%Y-%m-%d"))
        ]

        pie_trace = generate_pie_chart(df).data[0]

        asset_subplot = make_subplots(
            rows = 2,
            cols = 2,
            specs = [[{'type': 'indicator', 'colspan': 2},None], [{'type': 'indicator'},{'type': 'indicator'}]],
        )
        asset_subplot.add_trace(go.Indicator(mode='number', value=len(new_rows_last_week), title={'text': f'New Services found last week'}), row=1, col=1)
        asset_subplot.add_trace(go.Indicator(mode='number', value=len(rows_removed_last_week), title={'text': f'Services removed last week'}), row=2, col=1)
        asset_subplot.add_trace(pie_trace, row=2, col=2)
        return(asset_subplot)
    except Exception as e:
        logger.error(f'The subplot could not be rendered, sending back generic graph: {e}')
        cgf.set_no_results_found_figure()


model_id = 'em_5_enabled_services'

enabled_services_over_time = cgf.generate_line_graph_decoms(em_5_enabled_services, em_5_enabled_services_decommissioned, title='Services found over time', yaxis='Total Services')
training_modal_graph = cgf.training_modal(model_id, 'Services Management', 'https://www.youtube-nocookie.com/embed/uRsBpDR2CNg?si=axS88lDXPYAmAiea')
services_subplot = generate_subplot(em_5_enabled_services, em_5_enabled_services_decommissioned,)

layout = html.Div([
    html.H2('Enabled Services', style={'textAlign': 'center'}),
    dbc.Button("Services Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Services", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Firewall rules manage the connections to and from your system, they should always be enabled',
        ],
        style={'textAlign': 'center'}
    ),
    dcc.Loading(id=f'loading-{model_id}-subplot', type='default', children=[dcc.Graph(figure=services_subplot)]),
    html.Div([dcc.Graph(figure=enabled_services_over_time)]),
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
            columns=[
            {'name': 'Display Name', 'id': 'DisplayName'},
            {'name': 'Service Name', 'id': 'ServiceName'},
            {'name': 'Start Type', 'id': 'StartType'},
            {'name': 'Captured at', 'id': 'created_at'},
            ],
            data=em_5_enabled_services.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_5_enabled_services.to_dict('records')
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
            cf.run_subprocess_command('services.msc')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""