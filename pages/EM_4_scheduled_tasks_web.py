# Scheduled tasks webpage
# Useful help section: https://www.youtube.com/watch?v=8sDoQ4sbtCA
# We are going to incorporate this tool into our application as it was very useful
# https://www.nirsoft.net/about_nirsoft_freeware.html
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/


from dash.dependencies import Input, Output, State
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
# import dash
#import plotly.express as px
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

def read_scheduled_tasks():
    try:
        with DatabaseManager() as db:
            logger.info("Reading all from the em_4_scheduled_tasks SQL table")
            return(pd.read_sql_query("SELECT * FROM em_4_scheduled_tasks", db.conn))
    except Exception as e:
        logger.error(f'Reading all from the em_4_scheduled_tasks table failed')
        return pd.DataFrame()

def read_scheduled_tasks_decom():
    try:
        with DatabaseManager() as db:
            logger.info("Reading all from the em_4_scheduled_tasks SQL table")
            return(pd.read_sql_query("SELECT * FROM em_4_scheduled_tasks_decommissioned", db.conn))
    except Exception as e:
        logger.error(f'Reading all from the em_4_scheduled_tasks table failed')
        return pd.DataFrame()


scheduled_tasks = read_scheduled_tasks()
decommed_scheduled_tasks = read_scheduled_tasks_decom()
scheduled_task_over_time = cgf.generate_line_graph_decoms(scheduled_tasks, decommed_scheduled_tasks, title='Tasks found on system over time', yaxis='Total Scheduled Tasks')


model_id = 'em_4_scheduled_tasks'
training_modal = cgf.training_modal(model_id, 'Scheduled Tasks Management', 'https://www.youtube.com/embed/8sDoQ4sbtCA?rel=0&modestbranding=1&autohide=1&showinfo=0&controls=1')


layout = html.Div([
    html.H2('Scheduled Tasks', style={'textAlign': 'center'}),
    dbc.Button("Scheduled Tasks Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Scheduled Tasks", id="launch-button", color="warning", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Scheduled Tasks run on your computer and are triggered by a number of different Actions',
        html.Br(),
        'Common actions include, "At Startup", "At Shutdown", "When user logs in", "At time X" etc'], style={'textAlign': 'center'}),
    html.Div([dcc.Graph(figure=scheduled_task_over_time)]),
    html.Div(id="output-container"),
    training_modal,
    dcc.Loading(id='loading-scheduled-tasks', type='default', children = [
        dash_table.DataTable(
            id='scheduled-tasks',
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
            {'name': 'Enabled', 'id': 'Enabled'},
            {'name': 'Path', 'id': 'Path'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Command', 'id': 'Command'},
            {'name': 'Last Run Time', 'id': 'LastRunTime'},
            {'name': 'Next Run Time', 'id': 'NextRunTime'},
            {'name': 'Captured at', 'id': 'created_at'},
            ],
            data=scheduled_tasks.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in scheduled_tasks.to_dict('records')
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
        return not is_open
    return is_open


@callback(
    Output("output-container", "children"),
    [Input("launch-button", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        try:
            # Replace 'path_to_exe' with the actual path to your .exe file
            cf.run_subprocess_command('C:\\opt\\essential-metrics\\tools\\TaskSchedulerView.exe')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""
