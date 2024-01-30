#!/usr/bin/env python
# EM-7 - Password policy and password strength verification

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import zxcvbn
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger
from datetime import datetime, timedelta

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_7_password_policy = db.read_database_table('em_7_password_policy')


def gen_button_color(df):
    try:
        most_recent = df.sort_values(by='created_at', ascending=False).iloc[0]
        password_complexity = most_recent['PasswordComplexity']
        button_color = 'success' if password_complexity == '1' else 'danger'
        status_text = 'Enabled' if password_complexity == '1' else 'Disabled'
        #import pdb; pdb.set_trace()
        return(dbc.Button(status_text, id='password-complexity-button', color=button_color, className='mr-1', disabled=True))
    except Exception as e:
        logger.error(f'The button could not be generated, returning unknown button.')
        return(dbc.Button('Unknown', id='password-complexity-button', color='danger', className='mr-1'))


model_id = 'em_7_password_policy'
training_modal_graph = cgf.training_modal(model_id, 'Password Management', 'https://www.youtube-nocookie.com/embed/vuArJSVNA9c?si=3lYkHNNjxRGlflFA&amp;start=12')


layout = html.Div([
    html.H2('Password Management', style={'textAlign': 'center'}),
    dbc.Button("Password Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Password Policy", id=f"{model_id}-manage", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Your password is the frontdoor to your system and should be complex and not easily guessable.',
        html.Br(),
        'We recommend setting the Password complexity setting for your home system as this will ensure complexity requirements are met for all passwords to get into the system.',
        html.Br(),
        'The Password Complexity on your system is currently:',
        html.Br(),
        gen_button_color(em_7_password_policy)
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Br(),
    html.P([
        'You can test your passwords here and see how long they would take to crack',
        html.Br(),
        'We do not save any of these passwords, they are only used for the purposes of checking security and then are discarded.',
        html.Br(),
        dcc.Input(id='password-input', type='password', placeholder='Enter your password'),
        html.Br(),
        html.Div(id='password-strength'),
        html.Div(id='password-crack-time')
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Br(),
    html.P([
        'We also recommend testing your password on Have I been pwned',
        html.Br(),
        'This website collects all breach data and presents a frontend to test both your password and email address against compromises.',
        html.Br(),
        html.A("Check if your password has been compromised",
            href="https://haveibeenpwned.com/Passwords",
            target="_blank",
            style={'color': 'blue', 'textDecoration': 'underline'}),
        html.Br(),
        'We would also recommend the notification option on this website for your personal or business accounts as this will ensure if your data is released in any future breach you will be notified.',
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
            columns=[ {'name': i, 'id': i} for i in em_7_password_policy.columns],
            data=em_7_password_policy.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_7_password_policy.to_dict('records')
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
            cf.run_powershell_command('secpol.msc')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""

# Callback to update password strength and crack time
@callback(
    [Output('password-strength', 'children'),
     Output('password-crack-time', 'children')],
    Input('password-input', 'value')
)
def update_password_metrics(value):
    if value is None or value == '':
        return ['Password strength will be displayed here.', 'Time to crack will be displayed here.']
    
    # Evaluate the password strength
    strength = zxcvbn.zxcvbn(value)
    score = strength['score']
    feedback = strength['feedback']['warning'] if strength['feedback']['warning'] else 'Good password'
    color = "red" if score == 0 else "amber" if score ==1 else "orange" if score == 2 else "goldenrod" if score == 3 else "green"

    # Get crack times
    crack_times = strength['crack_times_display']
    online_throttling = crack_times['online_throttling_100_per_hour']
    online_no_throttling = crack_times['online_no_throttling_10_per_second']
    offline_slow_hash = crack_times['offline_slow_hashing_1e4_per_second']
    offline_fast_hash = crack_times['offline_fast_hashing_1e10_per_second']

    crack_time_info = (
        f"Time to crack (online, rate-limited): {online_throttling}\n"
        f"Time to crack (online, no rate limiting): {online_no_throttling}\n"
        f"Time to crack (offline, slow hash): {offline_slow_hash}\n"
        f"Time to crack (offline, fast hash): {offline_fast_hash}"
    )

    return [html.Div(f'Strength score: {score}/4. {feedback}', style={'color': color}), crack_time_info]