# Scheduled tasks webpage
# We are going to incorporate this tool into our application as it was very useful
# https://www.nirsoft.net/about_nirsoft_freeware.html

from dash.dependencies import Input, Output, State
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)


def read_scheduled_tasks():
    try:
        with DatabaseManager() as db:
            return(pd.read_sql_query("SELECT * FROM em_4_scheduled_tasks", db.conn))
    except Exception as e:
        logger.error(f'Reading all from the em_4_scheduled_tasks table failed')
        return pd.DataFrame()


def read_scheduled_tasks_decom():
    try:
        with DatabaseManager() as db:
            return(pd.read_sql_query("SELECT * FROM em_4_scheduled_tasks_decommissioned", db.conn))
    except Exception as e:
        logger.error(f'Reading all from the em_4_scheduled_tasks table failed')
        return pd.DataFrame()


scheduled_tasks = read_scheduled_tasks()
decommed_scheduled_tasks = read_scheduled_tasks_decom()
new_scheduled_tasks = cf.get_fresh_dataframe_data(scheduled_tasks, 'created_at')
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
    html.P([
        'Scheduled Tasks run on your computer and are triggered by a number of different actions',
        html.Br(),
        'Common actions include, "At Startup", "At Shutdown", "When user logs in", "At time X" etc.',
        html.Br(),
        'Scheduled tasks are a common method for malware persistance on your system so again just seeing new scheduled tasks and knowing what they are can be an effective method to catch malware of this sort.',
        html.Br(),
        'The third party application is by far the best method for reviewing your scheduled tasks.',
        html.Br(),
        'Interesting filter columns should you choose to look at your scheduled tasks are "Run on Boot/ Logon/ Event", "Run Daily/ Weekly/ Monthly"'
        ], style={'textAlign': 'center'}),
    html.Div([dcc.Graph(figure=scheduled_task_over_time)]),
    html.Div(id="output-container"),
    training_modal,
    html.H4("These are the new scheduled tasks we found on your system in the past 7 days", style={'textAlign': 'center'}),
    cgf.generate_dash_table(new_scheduled_tasks, 'new_scheduled_tasks'),
    html.H4("These are all the scheduled tasks on your system", style={'textAlign': 'center'}),
    cgf.generate_dash_table(scheduled_tasks, 'scheduled_tasks'),
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
    Output("output-container", "children"),
    [Input("launch-button", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        logger.info(f'{model_id} Manage button pressed')
        try:
            cf.run_subprocess_command('C:\\opt\\essential-metrics\\tools\\TaskSchedulerView.exe')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""