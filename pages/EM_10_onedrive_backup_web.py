#!/usr/bin/env python
# EM-10 - Microsoft Onedrive system backup enabled

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_10_onedrive_enabled = db.read_database_table('em_10_onedrive_enabled')


def gen_button_color(df):
    most_recent = df.sort_values(by='created_at', ascending=False).iloc[0]
    setting_enabled = most_recent['AccountName']
    button_color = 'success' if setting_enabled != 'NotConfigured' else 'danger'
    status_text = 'Enabled' if setting_enabled != 'NotConfigured' else 'Disabled'
    return(dbc.Button(status_text, id='onedrive-enabled', color=button_color, className='mr-1', disabled=True))


model_id = 'em_10_onedrive_enabled'
training_modal_graph = cgf.training_modal(model_id, 'Manage Onedrive Backups', 'https://www.youtube-nocookie.com/embed/xtsNTwRg7iM?si=40yydd3SmHuglvlL')


layout = html.Div([
    html.H2('OneDrive Backup Management', style={'textAlign': 'center'}),
    dbc.Button("OneDrive Backup Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage OneDrive Backup", id=f"{model_id}-manage", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Microsofts inbuild OneDrive backup solution is a great method for backing up your personal data.',
        html.Br(),
        'The solution is available in the settings -> Virus & threat protection -> Ransomware protection section.',
        html.Br(),
        'The backup is currently:',
        html.Br(),
        gen_button_color(em_10_onedrive_enabled)
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Br(),
    html.P([
        'There are many factors with a backup solution such as this and as such we recommend you watch the OneDrive Backup Help video in full at the top of this webpage before you enable any backups with this solution.',
        html.Br(),
        'If you do not currently have any backup solution for your files and you have an online Microsoft account this is a simple free (5G) method for backup and data resiliancy.',
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
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
            columns=[ {'name': i, 'id': i} for i in em_10_onedrive_enabled.columns],
            data=em_10_onedrive_enabled.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_10_onedrive_enabled.to_dict('records')
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
            cf.run_powershell_command('Start-Process "windowsdefender:"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""

