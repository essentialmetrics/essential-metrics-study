# index.py

from dash import html, Input, Output, dcc, State
import dash_bootstrap_components as dbc

from app import app
server = app.server

from pages import (
    home,
    EM_1_asset_register_web, 
    EM_2_software_register_web, 
    EM_3_firewall_web,
    EM_4_scheduled_tasks_web,
    EM_5_enabled_services_web,
    EM_6_defender_updates_web,
    EM_7_password_policy_web,
    EM_8_wlan_settings_web,
    EM_9_controlled_folder_web,
    EM_10_onedrive_backup_web,
    EM_11_vulnerability_patching_web,
    EM_12_reboot_analysis_web,
    EM_13_14_antivirus_working_web,
    EM_15_16_int_ext_ports_web,
    EM_18_rdp_settings_web,
    EM_19_usb_attached_web,
    EM_20_admin_logins_web
    #EM_21_phishing_training_web
    )

inventory_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href='/home'),
        dbc.DropdownMenuItem("Asset Register", href='/asset_register'),
        dbc.DropdownMenuItem("External/ Internal ports", href='/port_management'),
        dbc.DropdownMenuItem("Software Register", href='/software_register'),
        dbc.DropdownMenuItem("Firewall rules", href='/firewall_rules'),
        dbc.DropdownMenuItem("Scheduled Tasks", href='/scheduled_tasks'),
        dbc.DropdownMenuItem("Enabled Services", href='/enabled_services'),
        dbc.DropdownMenuItem("USB Devices", href='/usb_devices'),
    ],
    nav = True,
    in_navbar=True,
    label="Explore System Inventory",
)

metrics_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href='/home'),
        dbc.DropdownMenuItem("Microsoft Defender", href='/defender_management'),
        dbc.DropdownMenuItem("Password Policy", href='/password_management'),
        dbc.DropdownMenuItem("WiFi Settings", href='/wifi_management'),
        dbc.DropdownMenuItem("Controlled Folder Access", href='/controlled_folder_management'),
        dbc.DropdownMenuItem("Manage OneDrive Backups", href='/onedrive_backup_management'),
        dbc.DropdownMenuItem("Vulnerability patching", href='/vulnerability_patching'),
        dbc.DropdownMenuItem("Reboot Analysis", href='/reboot_analysis'),
        dbc.DropdownMenuItem("AntiVirus Working", href='/antivirus_management'),
        dbc.DropdownMenuItem("RDP Settings/ Sessions", href='/rdp_management'),
        dbc.DropdownMenuItem("Users/ Groups and Admin Logins", href='/admin_logins_management'),
    ],
    nav = True,
    in_navbar=True,
    label="Explore System Metrics",
)

# 
# 


advice_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href='/home'),
        dbc.DropdownMenuItem("NCSC Essential Training (External)", href="https://www.ncsc.gov.uk/training/cyber-security-for-small-organisations-scorm-v2/scormcontent/index.html#/", target="_blank"),
        dbc.DropdownMenuItem("NCSC Staff Training (External)", href="https://www.ncsc.gov.uk/training/top-tips-for-staff-scorm-v3/scormcontent/index.html#/", target="_blank"),
    ],
    nav = True,
    in_navbar=True,
    label="Explore Advice and Training",
)


navbar = dbc.Navbar(
    style={'display': 'grid'},
    children = dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="assets/oxford-logo.png", height="60px")),
                    ]
                ),
                href="/",
            ),
            dbc.NavbarToggler(id='inventory-dropdown'),
            dbc.Collapse(
                dbc.Nav(
                    [inventory_dropdown], navbar=True
                ),
                id="inventory_dropdown",
                navbar=True,
            ),
            dbc.NavbarToggler(id='metrics-dropdown'),
            dbc.Collapse(
                dbc.Nav(
                    [metrics_dropdown], navbar=True
                ),
                id="metrics_dropdown",
                navbar=True,
            ),
            dbc.NavbarToggler(id='advice-dropdown'),
            dbc.Collapse(
                dbc.Nav(
                    [advice_dropdown], navbar=True
                ),
                id="advice_dropdown",
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    class_name="navbar navbar-collapse-md",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [1]:
    app.callback(
        Output(f'navbar-collapse{i}', "is_open"),
        [Input(f'navbar-toggler{i}', 'n_clicks')],
        [State(f'navbar-collapse{i}', 'is_open')],
    )(toggle_navbar_collapse)

app.layout = html.Div([dcc.Location(id='url', refresh=False),
                       navbar,
                       html.Div(id='page-content')
                       ])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return home.layout
    elif pathname == '/asset_register':
        return EM_1_asset_register_web.layout
    elif pathname == '/software_register':
        return EM_2_software_register_web.layout
    elif pathname == '/firewall_rules':
        return EM_3_firewall_web.layout
    elif pathname == '/scheduled_tasks':
        return EM_4_scheduled_tasks_web.layout
    elif pathname == '/enabled_services':
        return EM_5_enabled_services_web.layout
    elif pathname == '/defender_management':
        return EM_6_defender_updates_web.layout
    elif pathname == '/password_management':
        return EM_7_password_policy_web.layout
    elif pathname == '/wifi_management':
        return EM_8_wlan_settings_web.layout
    elif pathname == '/controlled_folder_management':
        return EM_9_controlled_folder_web.layout
    elif pathname == '/onedrive_backup_management':
        return EM_10_onedrive_backup_web.layout
    elif pathname == '/vulnerability_patching':
        return EM_11_vulnerability_patching_web.layout
    elif pathname == '/reboot_analysis':
        return EM_12_reboot_analysis_web.layout
    elif pathname == '/antivirus_management':
        return EM_13_14_antivirus_working_web.layout
    elif pathname == '/port_management':
        return EM_15_16_int_ext_ports_web.layout
    elif pathname == '/rdp_management':
        return EM_18_rdp_settings_web.layout
    elif pathname == '/usb_devices':
        return EM_19_usb_attached_web.layout
    elif pathname == '/admin_logins_management':
        return EM_20_admin_logins_web.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(debug=True)