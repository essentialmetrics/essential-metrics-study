from dash import html
import dash_bootstrap_components as dbc

from app import app

layout = html.Div([
    html.H1('Home page', style={'textAlign': 'center'}),
    html.P([
        'Thanks again for participating in this study.',
        html.Br(),
        'We have designed this study to assess the effectiveness of security metrics for personal and micro business users.',
        html.Br(),
        'Recent data is converging that this group is increasingly doing business online since the pandemic.',
        html.Br(),
        'Their increased usage online has not been met with the necessary cyber upskilling leaving them at risk and the frequent target of attack.',
        html.Br(),
        html.Br(),
        'We have added individual advice throughout the dashboard and specific governmental advice in its own section.',
        html.Br(),
        'While much of the advice is general some is more targeted to UK customers as that is our target base.',
        html.Br(),
        'Hopefully you can learn something about your systems.',
        html.Br(),
        html.Br(),
        'There are several buttons throughout the dashboard application, the cottons are color codded.',
        html.Br(),
        'These are there meanings:',
        html.Br(),
        dbc.Button("Help Video (embedded youtube)", color="primary", className="me-1"),
        dbc.Button("Connect to Gateway", color="secondary", className="me-1"),
        dbc.Button("Windows system application", color="success", className="me-1"),
        dbc.Button("External advice", color="danger", className="me-1"),
        dbc.Button("Third party application", color="warning", className="me-1"),
        ],
        style={'textAlign': 'center'}
    ),
])