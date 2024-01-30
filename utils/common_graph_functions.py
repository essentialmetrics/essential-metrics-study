# Common Graph functions used by many dashboards

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from dash import html, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timezone

from utils.logger_config  import configure_logger

logger = configure_logger(__name__)


def set_no_results_found_figure():
    '''
    This function is used to return a text box when one of the dash or plotly graphs fails to render
    '''
    fig = go.Figure()
    fig.update_layout(
        xaxis = { "visible": False},
        yaxis = { "visible": False},
        annotations = [
            {
                "text": "There was an issue rendering the data or there has not been enough data collected yet.<br>Check back tomorrow",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 28}
            }
        ],
    )
    return(fig)


def plot_cumulative_assets(dataframe, title='Cumulative Count of Assets Over Time', x='Date found', y='Total Count'):
    """
    Plots a cumulative count of assets over time.

    :param dataframe: A pandas DataFrame with a 'created_at' column representing the dates.
    :return: A Plotly Express figure object.
    """
    try:
        if not pd.api.types.is_datetime64_any_dtype(dataframe['created_at']):
            dataframe['created_at'] = pd.to_datetime(dataframe['created_at'])
        sorted_df = dataframe.sort_values(by='created_at')
        sorted_df['cumulative_count'] = range(1, len(sorted_df) + 1)
        fig = px.line(sorted_df, x='created_at', y='cumulative_count', markers=True, 
                      title=title,
                      labels={'created_at': x, 'cumulative_count': y})
        fig.update_layout(title_x=0.5)
    except Exception as e:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='text',
                                 text=['Data was not parsed successfully', str(e)],
                                 textposition='bottom center'))
        fig.update_layout(title='Error in Data Parsing',
                          title_x=0.5,
                          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    return fig


def generate_line_graph_decoms(table, table_decomm, title='Elements found over time', xaxis='Date Found', yaxis='Count of elements found'):
    '''
    This function will take two tables that are used for tracking elements over time the regular table and the decommission table.
    The function will use both of these tables to generate a line graph of the elements over time
    Inputs:
        table:          The database table we wish to graph data on
        table_decomm:   The decommission table which is paired to the table above
        title:          This will be the graph title message
        x_axis:         This will be the graphs x_axis title
        y_axis:         This will be the graphs y axis title
    Outputs:
        fig:            This will be a plotly express line graph
    '''
    try:
        today = datetime.now(timezone.utc)
        # Get the number of rows that were added on x date
        table['created_at'] = pd.to_datetime(table['created_at'])
        addations = table['created_at'].dt.date.value_counts().reset_index()
        addations.columns = ['Date', 'Count']
        
        # Get the number of rows that were added on x date from the decommissioned table
        table_decomm['created_at'] = pd.to_datetime(table_decomm['created_at'])
        addations_from_decom = table_decomm['created_at'].dt.date.value_counts().reset_index()
        addations_from_decom.columns = ['Date', 'Count']
        
        # Get the number of rows that were removed on x date
        table_decomm['removed_at'] = pd.to_datetime(table_decomm['removed_at'])
        removals = table_decomm['removed_at'].dt.date.value_counts().reset_index()
        removals.columns = ['Date', 'Count']
        removals['Count'] = removals['Count'] * -1
        
        combined = pd.concat([addations, addations_from_decom, removals])
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
        #import pdb; pdb.set_trace()
        fig = px.line(combined, x='Date', y='Count', title=f'{last_count} {title}')
        fig.update_xaxes(title_text=xaxis).update_yaxes(title_text=yaxis)
        fig.update_layout(title={ 'x':0.5, 'xanchor': 'center', 'yanchor': 'top' })
        return fig
    except Exception as e:
        logger.error(f'The line graph could not be rendered, sending back generic error for the line graph: {e}')
        return(set_no_results_found_figure())
        

def training_modal(id, name, video):
    '''
    This function will return a training model wih a video embedded inside
    '''
    return dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(name, className="text-center-title")),
        dbc.ModalBody(
            html.Iframe(
                src=video,
                title="YouTube video player",
                style={'width': '100%', 'height': '315px'}, 
            )
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id=f"{id}-close-modal", className="ms-auto", n_clicks=0)
        ),
    ],
    id=id,
    is_open=False,  # Start with the modal hidden
    size="xl",  # Large modal
    centered=True,
)


def generate_dash_table(df, table_name, style_data_conditional=[], page_size=10):
    '''
    This function will return a data table
    This gives us a standard way to generate a table to give our application consistancy with each of our web pages
    Inputs:
        df: This is our dataframe to create a table from
        table_name: This will be used to generate our table id
        page_size: This is how many rows to show in the table
    Outputs:
        dash_table.datatable
    '''
    try:
        table = dash_table.DataTable(
            id=f'{table_name}-table',
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
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            tooltip_data=[
                {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
                for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            sort_action='native',
            sort_mode='single',
            filter_action='native',
            sort_by=[{'column_id': 'created_at', 'direction': 'desc'}],
            page_size=page_size,
            style_data_conditional=style_data_conditional,
        )
        return table
    except Exception as e:
        logger.error(f'Could not generate dash_table, returning error DIV: {e}')
        return html.H4("Data Table could not be rendered, see logs", style={'textAlign': 'center'}),
        

def gen_button_1(display_text, metric, hyperlink=False,):
    if hyperlink:
        return html.A(
            dbc.Button(display_text, id=f"{metric}-b1", n_clicks=0, style={
                'width': '200px',
                'height': '56px',
                'position': 'absolute',
                'top': '10px',
                'right': '10px'
            }),
            href=f'http://{hyperlink}',
            target="_blank"
            )
    else:
        return dbc.Button(display_text, id=f"{metric}-b1", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '10px'
        })





def gen_button_2(display_text, metric, hyperlink=False,):
    if hyperlink:
        return html.A(
            dbc.Button(display_text, id=f"{metric}-b2", n_clicks=0, style={
                'width': '200px',
                'height': '56px',
                'position': 'absolute',
                'top': '10px',
                'right': '230px'
            }),
            href=f'http://{hyperlink}',
            target="_blank"
            )
    else:
        return dbc.Button(display_text, id=f"{metric}-b2", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '230px'
        }),




'''
em_20_users['account_disabled_int'] = em_20_users['account_disabled'].map({'True': 1, 'False': 0})
sum_disabled_accounts = em_20_users['account_disabled_int'].sum()





from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, callback_context
import dash_bootstrap_components as dbc
import common_functions as cf
import common_graph_functions as cgf
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime, timedelta

from database_class import DatabaseManager
from logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_20_admin_logins = db.read_database_table('em_20_admin_logins')


with DatabaseManager() as db:
    em_20_users = db.read_database_table('em_20_users')


df = em_20_admin_logins

# This merge will get all user account logins and drop all system logins as we are merging on the users SID
df = pd.merge(df, em_20_users, left_on='Uid', right_on='sid')

df = df[['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'TimeGenerated', 'priv']]

def append_priv(user, priv):
    if priv == '2':
        return f'{user} (2 admin)'
    elif priv == '1':
        return f'{user} (1 user)'
    else:
        return f'{user} ({priv})'

# Apply this function to each row in the DataFrame
df['User'] = df.apply(lambda row: append_priv(row['User'], row['priv']), axis=1)






df.loc[:, 'TimeGenerated'] = df['TimeGenerated'].str[:-4]
df.loc[:, 'TimeGenerated'] = pd.to_datetime(df['TimeGenerated'], format='%Y%m%d%H%M%S.%f')

df = df.sort_values('RecordNumber')
df = df.reset_index(drop=True)

results = []




for i, row in df.iterrows():
    if row['EventIdentifier'] == '4624':
        logon_id = row['LogonID']
        start_time = row['TimeGenerated']
        
        # Search for the matching LogonID starting from the next row
        for forward_row in df.iloc[i+1:].itertuples():
            if forward_row.LogonID == logon_id:
                end_time = forward_row.TimeGenerated
                time_diff = end_time - start_time
                
                # Add the record to the results list
                results.append([row['RecordNumber'], row['User'], row['LogonType'],
                                row['EventIdentifier'], row['LogonID'], row['ElevatedToken'],
                                start_time, end_time, time_diff])
                break





results_df = pd.DataFrame(results, columns=['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'StartTime', 'EndTime', 'TimeDifference'])

# Display the results
print(results_df)


fig = px.timeline(results_df, x_start="StartTime", x_end="EndTime", y="User", color="LogonType",
                  title="Login Events Timeline")

fig.update_yaxes(autorange="reversed")  # Optional: reverse the Y-axis
fig.show()


results_df['DurationSeconds'] = results_df['TimeDifference'].dt.total_seconds()

# Create a bar chart
#fig = px.bar(results_df, x="User", y="DurationSeconds", color="LogonType",
#             title="Duration of Login Events by User")

#fig.show()



sum_duration_per_user = results_df.groupby('User')['DurationSeconds'].sum()

total_duration = sum_duration_per_user.sum()
percentage_duration_per_user = (sum_duration_per_user / total_duration) * 100

fig = px.pie(percentage_duration_per_user, 
             values=percentage_duration_per_user, 
             names=percentage_duration_per_user.index, 
             title='Percentage of Total Duration by User')

# Show the plot
fig.show()









'''

'''
results = []



for i, row in df.iterrows():
    if row['EventIdentifier'] == '4624':
        logon_id = row['LogonID']
        start_time = row['TimeGenerated']
        
        # Search for the matching LogonID starting from the next row
        for forward_row in df.iloc[i+1:].itertuples():
            if forward_row.LogonID == logon_id:
                end_time = forward_row.TimeGenerated
                time_diff = end_time - start_time
                
                
                
                # Add the record to the results list
                results.append([row['RecordNumber'], row['User'], forward_row.User, row['LogonType'],
                                row['EventIdentifier'], row['LogonID'], row['ElevatedToken'],
                                start_time, end_time, time_diff])
                break


results_df = pd.DataFrame(results, columns=['RecordNumber', 'User', 'LogoffUser', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'StartTime', 'EndTime', 'TimeDifference'])

# Display the results
print(results_df)

results_df = results_df[results_df['LogonType'] != '5']

















from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, callback_context
import dash_bootstrap_components as dbc
import common_functions as cf
import common_graph_functions as cgf
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime, timedelta

from database_class import DatabaseManager
from logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_20_admin_logins = db.read_database_table('em_20_admin_logins')


with DatabaseManager() as db:
    em_20_users = db.read_database_table('em_20_users')


df = em_20_admin_logins


df = pd.merge(df, em_20_users, left_on='Uid', right_on='sid')

df = df[['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'TimeGenerated', 'priv']]

def append_priv(user, priv):
    if priv == '2':
        return f'{user} (2 admin)'
    elif priv == '1':
        return f'{user} (1 user)'
    else:
        return f'{user} ({priv})'

# Apply this function to each row in the DataFrame
df['User'] = df.apply(lambda row: append_priv(row['User'], row['priv']), axis=1)

df.loc[:, 'TimeGenerated'] = df['TimeGenerated'].str[:-4]
df.loc[:, 'TimeGenerated'] = pd.to_datetime(df['TimeGenerated'], format='%Y%m%d%H%M%S.%f')

df = df.sort_values('RecordNumber')
df = df.reset_index(drop=True)

results = []

for i, row in df.iterrows():
    if row['EventIdentifier'] == '4624':
        logon_id = row['LogonID']
        start_time = row['TimeGenerated']
        
        # Search for the matching LogonID starting from the next row
        for forward_row in df.iloc[i+1:].itertuples():
            if forward_row.LogonID == logon_id:
                end_time = forward_row.TimeGenerated
                time_diff = end_time - start_time
                
                # Add the record to the results list
                results.append([row['RecordNumber'], row['User'], row['LogonType'],
                                row['EventIdentifier'], row['LogonID'], row['ElevatedToken'],
                                start_time, end_time, time_diff])
                break


results_df = pd.DataFrame(results, columns=['RecordNumber', 'User', 'LogonType', 'EventIdentifier', 'LogonID', 'ElevatedToken', 'StartTime', 'EndTime', 'TimeDifference'])















'''