#!/usr/bin/env python
# EM-2 - Software asset register which displays the data captured by EM_2_software_register

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timezone
from dash import html, dcc, callback, Input, Output, dash_table, callback_context
import dash
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

from utils.database_class import DatabaseManager
import utils.common_graph_functions as cgf
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)


def read_software_register():
    try:
        with DatabaseManager() as db:
            logger.info("Reading all from the software_register SQL table")
            return(pd.read_sql_query("SELECT * FROM em_2_software_register", db.conn))
    except Exception as e:
        logger.error(f'Reading all from the software_register table failed')
        return pd.DataFrame()

software_register = read_software_register()
s = read_software_register()

with DatabaseManager() as db:
    em_2_software_register = pd.read_sql_query("SELECT * FROM em_2_software_register", db.conn)

with DatabaseManager() as db:
    em_2_software_register_decommissioned = pd.read_sql_query("SELECT * FROM em_2_software_register_decommissioned", db.conn)

model_id = 'em_2_software_registry'
training_modal_graph = cgf.training_modal(model_id, 'Software Management', 'https://www.youtube.com/embed/CyF4nvAwieI?si=MlYgmQzidlkNXhhD&amp;start=26')


def software_installs_over_time(em_2_software_register, em_2_software_register_decommissioned):
    '''
    This function will return the software installs over time
    This needs its own function as the install date is in a differnt format than the rest of the captured data
    '''
    try:
        today = datetime.now(timezone.utc)
        em_2_software_register['InstallDate'] = pd.to_datetime(em_2_software_register['InstallDate'], format='%Y%m%d')
        installations = em_2_software_register['InstallDate'].value_counts().reset_index()
        installations.columns = ['Date', 'Count']

        em_2_software_register_decommissioned['InstallDate'] = pd.to_datetime(em_2_software_register_decommissioned['InstallDate'], format='%Y%m%d')
        installs_removed = em_2_software_register_decommissioned['InstallDate'].value_counts().reset_index()
        installs_removed.columns = ['Date', 'Count']

        em_2_software_register_decommissioned['removed_at'] = pd.to_datetime(em_2_software_register_decommissioned['removed_at'])
        removals = em_2_software_register_decommissioned['removed_at'].dt.date.value_counts().reset_index()
        removals.columns = ['Date', 'Count']
        removals['Count'] = removals['Count'] * -1

        combined = pd.concat([installations, installs_removed, removals])

        combined['Date'] = pd.to_datetime(combined['Date'])
        combined = combined.groupby('Date').sum().sort_index().cumsum().reset_index()

        # Is there is no new rows for today take the last value from the series and add it to todays date to keep a running tally of the elements in the index
        if today not in combined['Date'].dt.date.values:
            last_count = combined.iloc[-1]['Count']
            new_row_df = pd.DataFrame([{'Date': pd.Timestamp(str(today)), 'Count': last_count}])
            combined = pd.concat([combined, new_row_df], ignore_index=True)
            logger.debug(f"Today's date is not in the DataFrame. Last date's count value: {last_count}")
        else:
            logger.debug("Today's date is found in the DataFrame.")

        # Plotting
        fig = px.line(combined, x='Date', y='Count', title='Software Installations Over Time')
        fig.update_xaxes(title_text='Date of Installation').update_yaxes(title_text='Total Software')
        fig.update_layout(title={ 'x':0.5, 'xanchor': 'center', 'yanchor': 'top' })
        return fig
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic error for the line graph: {e}')
        return(cgf.set_no_results_found_figure())

installs_over_time = software_installs_over_time(em_2_software_register, em_2_software_register_decommissioned)


def generate_software_removals():
    # This will get the decommissioned software, we need to join the tables left to ensure we are not getting an updated piece of software as a removed piece of software
    try:
        query = '''
            SELECT em_2_software_register_decommissioned.*
            FROM em_2_software_register_decommissioned
            LEFT JOIN em_2_software_register ON em_2_software_register_decommissioned.Publisher = em_2_software_register.Publisher AND em_2_software_register_decommissioned.DisplayName = em_2_software_register.DisplayName
            WHERE em_2_software_register.Publisher IS NULL AND em_2_software_register.DisplayName IS NULL;
        '''
        
        with DatabaseManager() as db:
            removed_software = pd.read_sql_query(query, db.conn)
        
        removed_software['removed_at'] = pd.to_datetime(removed_software['removed_at'])
        removed_software['removed_at_date'] = removed_software['removed_at'].dt.date
        removal_counts = removed_software.groupby('removed_at_date').size().reset_index(name='count')
        fig_removed_date = px.line(removal_counts, x='removed_at_date', y='count', title="Daily Software Removals", markers=True)
        removal_counts['total_count'] = removal_counts['count'].cumsum()
        fig_removed_total = px.line(removal_counts, x='removed_at_date', y='total_count', title="Cumulative Software Removals", markers=True)
        return(removed_software, fig_removed_date, fig_removed_total)
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic graph: {e}')
        return(pd.DataFrame(), cgf.set_no_results_found_figure(), cgf.set_no_results_found_figure())


def generate_updated_software():
    try:
        # Get software updates for all software
        query = '''
            SELECT em_2_software_register_decommissioned.*
            FROM em_2_software_register_decommissioned
            INNER JOIN em_2_software_register 
            ON em_2_software_register_decommissioned.Publisher = em_2_software_register.Publisher AND em_2_software_register_decommissioned.DisplayName = em_2_software_register.DisplayName;
        '''
        
        with DatabaseManager() as db:
            updated_software = pd.read_sql_query(query, db.conn)
        
        updated_software['removed_at'] = pd.to_datetime(updated_software['removed_at'])
        updated_software['removed_at_date'] = updated_software['removed_at'].dt.date
        add_counts = updated_software.groupby('removed_at_date').size().reset_index(name='count')
        add_counts = add_counts.sort_values('removed_at_date')
        fig_sw_updated_total = px.line(add_counts, x='removed_at_date', y='count', title="Cumulative Software upgrades", markers=True)
        return(updated_software, fig_sw_updated_total)
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic graph: {e}')
        return(pd.DataFrame(), cgf.set_no_results_found_figure())


def generate_new_software():
    try:
        # Get new software installs for all software
        query = '''
            SELECT em_2_software_register.*
            FROM em_2_software_register
            WHERE NOT EXISTS (
                SELECT 1
                FROM em_2_software_register_decommissioned
                WHERE em_2_software_register.Publisher = em_2_software_register_decommissioned.Publisher
                AND em_2_software_register.DisplayName = em_2_software_register_decommissioned.DisplayName
            );
        '''
        
        with DatabaseManager() as db:
            em_2_software_register = pd.read_sql_query(query, db.conn)
        
        with DatabaseManager() as db:
            install_date = pd.read_sql_query("Select min(timestamp) from app_install_date;", db.conn)
        
        em_2_software_register['InstallDate'] = pd.to_datetime(em_2_software_register['InstallDate'], format='%Y%m%d')
        min_install_date = pd.to_datetime(install_date['min(timestamp)'].iloc[0], format='%Y%m%d')
        new_software = em_2_software_register[em_2_software_register['InstallDate'] > min_install_date]
        install_counts = new_software['InstallDate'].value_counts().reset_index().rename(columns={'index': 'InstallDate', 0: 'count'})
        install_counts = install_counts.sort_values('InstallDate')
        fig_new_installs = px.line(install_counts, x='InstallDate', y='count', title="New Software Installations by Date", markers=True)
        return(new_software, fig_new_installs)
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic graph: {e}')
        return(pd.DataFrame(), cgf.set_no_results_found_figure())


def generate_software_subplots(new_software, updated_software, software_removals_day, software_removals_count):
    try:    
        asset_subplot = make_subplots(rows=2, cols=2)
        
        for trace in new_software.data:
            asset_subplot.add_trace(go.Scatter(x=trace.x, y=trace.y, mode='lines+markers', name=trace.name), row=1, col=1)
            
        for trace in updated_software.data:
            asset_subplot.add_trace(go.Scatter(x=trace.x, y=trace.y, mode='lines+markers', name=trace.name), row=1, col=2)
            
        for trace in software_removals_day.data:
            asset_subplot.add_trace(go.Scatter(x=trace.x, y=trace.y, mode='lines+markers', name=trace.name), row=2, col=1)
            
        for trace in software_removals_count.data:
            asset_subplot.add_trace(go.Scatter(x=trace.x, y=trace.y, mode='lines+markers', name=trace.name), row=2, col=2)
            
        asset_subplot.update_layout(height=600, autosize=True, title_text="Subplots of Software changes on your system over time")
        asset_subplot.update_xaxes(title_text="Date", row=1, col=1)
        asset_subplot.update_xaxes(title_text="Date", row=1, col=2)
        asset_subplot.update_xaxes(title_text="Date", row=2, col=1)
        asset_subplot.update_xaxes(title_text="Date", row=2, col=2)
        asset_subplot.update_yaxes(title_text="Count of new software installed", row=1, col=1)
        asset_subplot.update_yaxes(title_text="Count of software updates per day", row=1, col=2)
        asset_subplot.update_yaxes(title_text="Count of software removals per day", row=2, col=1)
        asset_subplot.update_yaxes(title_text="Count of all software removals", row=2, col=2)
        
        return(asset_subplot)
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic graph: {e}')
        return(cgf.set_no_results_found_figure())


new_software_df, new_software_graph = generate_new_software()
updated_software_df, updated_software_graph = generate_updated_software()
removed_software_df, software_removals_day, software_removals_count = generate_software_removals()
software_subplot = generate_software_subplots(new_software_graph, updated_software_graph, software_removals_day, software_removals_count)


layout = html.Div([
    html.H2('Software register', style={'textAlign': 'center'}),
    training_modal_graph,
    dbc.Button("Software Help", id=f"{model_id}-open-model", n_clicks=0, style={
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px'
    }),
    dbc.Button("Manage Software", id=f"{model_id}-manage", color="success", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '230px'
        }),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    html.Br(),
    html.P([
        'A software register is used to track all of your installed software in your home network.',
        html.Br(),
        'Like the asset register it is a good idea to know what is installed on your system and remove any old outdated software that is no longer needed.',
        html.Br(),
        'These graphs can help you see when things changed on your system, software updates can occur often and unprompted by you, new software should be examined closely (Check the table below for details)',
        html.Div([dcc.Graph(figure=software_subplot)]),
        html.H3("Total Software on the system over time"),
        'This graph tracks all your installed software on the system, it looks at decommissions and installations and graphs them together to give you a complete picture of your software on your system.',
        html.Br(),
        'If software did not add the install date to the registry we have added the install date as 1st Jan 2019 so you may see software here with an incorrect install date because of this design decision.',
        html.Br(),
        'Software should be kept up to date if it is needed or removed entirely if there is no longer a need for it on your system.',
        html.Div([dcc.Graph(figure=installs_over_time)]),
        ], style={'textAlign': 'center'}),
    html.P([
        html.H3("Software tables"),
        html.H5("New software"),
        'This is all the software that is new from the start of the study period',
        html.Br(),
        cgf.generate_dash_table(new_software_df, 'new_software_df'),
        html.H5("Updated software"),
        'This is all the software that has been updated since the start of the study period',
        html.Br(),
        cgf.generate_dash_table(updated_software_df, 'updated_software_df'),
        html.H5("Decommissioned software"),
        'This is all the software that has been removed since the start of the study period',
        html.Br(),
        cgf.generate_dash_table(removed_software_df, 'removed_software_df'),
        html.H5("All software currently on the system"),
        'This is all the software that we have found on the system at our last scanning',
        html.Br(),
        cgf.generate_dash_table(em_2_software_register, 'em_2_software_register'),
        ],
        style={'textAlign': 'center'}
    ),
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
            cf.popen_subprocess_command('control appwiz.cpl')
            return ""
        except Exception as e:
            logger.error(f'Failed to launch management program, error: {e}')
            return ""
    return ""