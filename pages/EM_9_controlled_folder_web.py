#!/usr/bin/env python
# EM-9  - Controlled Folder access management, this is used to prompt for the enablement of a default disabled setting in Microsoft

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash_bootstrap_components as dbc
import utils.common_functions as cf
import utils.common_graph_functions as cgf

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_9_controlled_folder_access = db.read_database_table('em_9_controlled_folder_access')


def gen_button_color(df):
    most_recent = df.sort_values(by='created_at', ascending=False).iloc[0]
    setting_enabled = most_recent['EnableControlledFolderAccess']
    button_color = 'success' if setting_enabled == '1' else 'danger'
    status_text = 'Enabled' if setting_enabled == '1' else 'Disabled'
    return(dbc.Button(status_text, id='controlled-folder-button', color=button_color, className='mr-1', disabled=True))


model_id = 'em_9_controlled_folder'
training_modal_graph = cgf.training_modal(model_id, 'Controlled Folder Management', 'https://www.youtube-nocookie.com/embed/9R_RymHNfvM?si=1P3ajIs7c_-GgBTX')


layout = html.Div([
    html.H2('Controlled Folder Management', style={'textAlign': 'center'}),
    dbc.Button("Controlled Folder Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Controlled Folders", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Br(),
    html.P([
        'Controlled Folders is a setting by Microsoft to help reduce the harm from Ransomware.',
        html.Br(),
        'With this feature you can control folder based authorization to specific applications.',
        html.Br(),
        'You currently have this setting:',
        html.Br(),
        gen_button_color(em_9_controlled_folder_access)
        ],
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Br(),
    html.P([
        'We recommend you enable this setting as it can provide significant Ransomware protection and has little impact to your system',
        html.Br(),
        'This protects your standard user folders and any other folders you may add manually. External backup drives are recommended.',
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
            columns=[ {'name': i, 'id': i} for i in em_9_controlled_folder_access.columns],
            data=em_9_controlled_folder_access.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in em_9_controlled_folder_access.to_dict('records')
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
            cf.run_powershell_command('Start-Process "windowsdefender:"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""

