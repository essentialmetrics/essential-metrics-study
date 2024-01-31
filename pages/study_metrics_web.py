#!/usr/bin/env python
# This web page will present all gathered study metrics so subjects can see exactly what we are gathering from their systems at all times.

from dash import html
import utils.common_graph_functions as cgf
from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)


def get_study_tables():
    '''
    This function will get all data from the study-metrics.db database and present it in tables on this webpage
    '''
    try:
        with DatabaseManager(database_name='study-metrics.db') as db:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            db.execute_query(query)
            tables = db.cursor.fetchall()
            
        table_data = {}
        
        for table in tables:
            table_name = table[0]
            with DatabaseManager(database_name='study-metrics.db') as db:
                table_data[table_name] = db.read_database_table(table_name)
                
        table_components = []
        table_names = list(table_data.keys())
        
        for table_name in table_names:
            df = table_data[table_name]
            dash_table_component = cgf.generate_dash_table(df, f'{table_name}-study')
            table_components.append(html.Div([html.H3(table_name), dash_table_component]))
        
        return(table_components)
    except Exception as e:
        logger.error(f'The study tables could not be queried presenting generic graph: {e}')
        return([html.Div([html.H3('Failed to query study-metrics.db'), cgf.set_no_results_found_figure()])])


table_components = get_study_tables()

layout = html.Div([
    html.H2('Study data', style={'textAlign': 'center'}),
    html.P([
        'This is all the study data which we want to collect at the end of this study.',
        html.Br(),
        'There should be no personal data in any of these tables, if you see any personal data please reach out to us and we will help correct this issue.',
        *[html.Div(component) for component in table_components]
        ],
        style={'textAlign': 'center'}
    ),
])