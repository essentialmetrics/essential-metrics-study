#!/usr/bin/env python
# EM-15 - External Ports presentation
# EM-16 - Internal Ports presentation

from dash.dependencies import Input, Output, State
from dash import html, dcc, callback, Input, Output, dash_table, callback_context, dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import networkx as nx
import numpy as np
import utils.common_functions as cf
import utils.common_graph_functions as cgf
import EM_1_asset_register as ar

from utils.database_class import DatabaseManager
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

with DatabaseManager() as db:
    em_15_external_ports = db.read_database_table('em_15_external_ports')

with DatabaseManager() as db:
    em_16_internal_ports = db.read_database_table('em_16_internal_ports')

with DatabaseManager() as db:
    em_16_internal_ports_heatmap = db.read_database_table('em_16_internal_ports_heatmap')

with DatabaseManager() as db:
    em_1_named_asset_register = db.read_database_table('em_1_named_asset_register')


def generate_network_graph(df, gateway):
    '''
    This function will generate a Network hub and spoke graph centered on the default gateway in the network.
    While connections may be possible between the devices the gateway was used as a hub for the network graph as a natural central point for the network
    See https://networkx.org/documentation/stable/ for full details of this software
    Inputs:
        df: dataframe to build the graph off, this is our em_16_internal_ports table
        gateway: central hub for the network graph
    Outputs:
        fig: This is the network graph that we are going to display
    '''
    def _get_asset_name(df, ip):
        '''
        This will get the asset name from the IP address and return the friendly name for the device
        '''
        try:
            ip_only = ip.split(':')[0]
            matching_rows = df.loc[df['ip'] == ip_only, 'asset_name']
            if not matching_rows.empty:
                return f'{matching_rows.iloc[0]} ({ip})'
            else:
                return ip
        except Exception as e:
            return ip
        
    try:
        G = nx.Graph()
        central_node = gateway
        G.add_node(central_node)

        # Add each of our IPs as nodes and connect them to the central node
        for ip in df['ip'].unique():
            if ip != central_node:
                G.add_edge(central_node, ip)
                # Here we need to check for each of the IP addresses ports then we are going to add them to the graph as edge nodes
                ports = df[df['ip'] == ip]['port'].unique()
                for port in ports:
                    port_node = f"{ip}: Port {port}"
                    G.add_edge(ip, port_node)

        # We needed this separate function to add the gateways ports to the graph as adding the IP to itself will not work "G.add_edge(central_node, ip)" from above for loop
        ports = df[df['ip'] == central_node]['port'].unique()
        for port in ports:
            port_node = f"{central_node}: Port {port}"
            G.add_edge(central_node, port_node)

        # After we have added all the IP addresses and their respective ports we need to position them on the graph
        # We are using sin cos and pi to circle the node and ports around the central hub and then circle the ports around the respective spokes
        pos = {central_node: np.array([0.5, 0.5])}
        secondary_nodes = [node for node in G.nodes() if node != central_node and 'Port' not in node]
        num_secondary = len(secondary_nodes)
        secondary_pos = np.array([
            [0.5 + 0.3 * np.sin(2 * np.pi * i / num_secondary), 0.5 + 0.3 * np.cos(2 * np.pi * i / num_secondary)]
            for i in range(num_secondary)
        ])
        for node, p in zip(secondary_nodes, secondary_pos):
            pos[node] = p

        # Position the ports around their respective IPs
        all_nodes = [node for node in G.nodes() if 'Port' not in node]
        for node in all_nodes:
            tertiary_nodes = [n for n in G.neighbors(node) if 'Port' in n]
            num_tertiary = len(tertiary_nodes)
            angle_step = 2 * np.pi / max(num_tertiary, 1)  # Avoid division by zero
            start_angle = np.arctan2(pos[node][1] - 0.5, pos[node][0] - 0.5) - np.pi / 2
            tertiary_pos = [
                pos[node] + 0.1 * np.array([np.sin(start_angle + angle_step * i), np.cos(start_angle + angle_step * i)])
                for i in range(num_tertiary)
            ]
            for n, p in zip(tertiary_nodes, tertiary_pos):
                pos[n] = p

        # Now create edge_trace and node_trace with the positions in 'pos'
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)


        ip_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='red',  # Color for IP addresses
                size=10,
                line=dict(width=2)
            )
        )

        port_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='blue',  # Color for ports
                size=8,
                line=dict(width=2)
            )
        )

        # We are adding the names from the named asset table here so people can see what ports on their devices are open
        for node in G.nodes():
            x, y = pos[node]
            hover_text = _get_asset_name(em_1_named_asset_register, node)
            if 'Port' not in node:
                ip_node_trace['x'] += (x,)
                ip_node_trace['y'] += (y,)
                ip_node_trace['text'] += (hover_text,)
            else:
                port_node_trace['x'] += (x,)
                port_node_trace['y'] += (y,)
                port_node_trace['text'] += (hover_text,)

        fig = go.Figure(data=[edge_trace, ip_node_trace, port_node_trace],
                        layout=go.Layout(
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        return(fig)
    except Exception as e:
        logger.error(f'The network graph graph could not be rendered, sending back generic graph: {e}')
        return(cgf.set_no_results_found_figure())



model_id = 'em_15_external_ports'
gateway_url = ar.get_default_gateway()

training_modal_graph = cgf.training_modal(model_id, 'VLAN Segmentation', 'https://www.youtube-nocookie.com/embed/eqr-vTC7EVk?si=L-2upZdkoTDxYvwJ')

# The current data is from the last run on nmap and the heatmap is all ports ever found open in your network
current_network_hub_and_spoke_graph = generate_network_graph(em_16_internal_ports, gateway_url)
heatmap_network_hub_and_spoke_graph = generate_network_graph(em_16_internal_ports_heatmap, gateway_url)

layout = html.Div([
    dbc.Button("VLAN device management Help", id=f"{model_id}-open-model", n_clicks=0, style= {
        'width': '200px',
        'height': '56px',
        'position': 'absolute',
        'top': '10px',
        'right': '10px',
        }),
    html.A(
        dbc.Button("Connect to Router", id=f"{model_id}-manage", color="secondary", n_clicks=0, style={
            'width': '200px',
            'height': '56px',
            'position': 'absolute',
            'top': '10px',
            'right': '230px'
        }),
        href=f'http://{gateway_url}',
        target="_blank"
    ),
    training_modal_graph,
    html.H2('External/ Internal port Management', style={'textAlign': 'center'}),
    html.P([
        'Regularly scanning your external ports is a great way to ensure there is no misconfigurations in your router.',
        html.Br(),
        'It is unusual for users to open the firewall ports to their networks, as such you should expect to see no open external ports from any of our scans.',
        html.Br(),
        'Having or leaving ports open to your network is extremely dangerous if not done securely.',
        html.Br(),
        'Bad actors scan the entire IPv4 subnet every few minutes looking for weakness in applications presented through open ports to internal networks.',
        html.Br(),
        'There are also for profit enterprises that scan the internet and present a frontend to their dataset which is queryable by anyone.',
        html.Br(),
        'For example this is what they have on you: ',
        html.A('Shodan', href=f'https://www.shodan.io/host/{em_15_external_ports.tail(1)["ip"].iloc[0]}' if not em_15_external_ports.empty else '#', target="_blank")
        ],
        style={'textAlign': 'center'}
    ),
    html.Div(id=f"{model_id}-hidden-output", style={"display": "none"}),
    html.P([
        html.H4("These are the external ports we found when scanning your external IP"),
        'This table should look empty, if you have external ports showing up in this table and you did not explicitly open them in your gateway you should address this immediately.'
        ], 
        style={'textAlign': 'center'}
    ),
    cgf.generate_dash_table(em_15_external_ports, 'em_15_external_ports', page_size=5),
    html.H4("This is your total internal network graph", style={'textAlign': 'center'}),
    html.P([
        'Total here being every internal device and port we have seen open since we started scanning.',
        html.Br(),
        'You should name your devices so you can see what ports on each of your devices are open: ',
        html.A('Name Devices', href=f'http://127.0.0.1:8050/asset_register'),
        ], 
        style={'textAlign': 'center'}
    ),
    html.Div([dcc.Graph(figure=heatmap_network_hub_and_spoke_graph, style={'height': '800px', 'width': '100%'})]),
    html.H4("This is your current internal network graph", style={'textAlign': 'center'}),
    html.P([
        'Current here being what was detected at the last nmap scan we performed.',
        html.Br(),
        ], 
        style={'textAlign': 'center'}
    ),
    html.Div([dcc.Graph(figure=current_network_hub_and_spoke_graph, style={'height': '800px', 'width': '100%'})]),
    html.H4("These are the ports that were identified from the latest scan of your internal network", style={'textAlign': 'center'}),
    cgf.generate_dash_table(em_16_internal_ports, 'em_16_internal_ports'),
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
    [Input(f"{model_id}-help", "n_clicks")]
)
def launch_exe(n_clicks):
    if n_clicks > 0:
        try:
            cf.run_powershell_command('Start-Process "windowsdefender://threat"')
            return "Launched successfully."
        except Exception as e:
            return f"Error: {e}"
    return ""


