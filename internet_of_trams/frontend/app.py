import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

from internet_of_trams.frontend.trams_dasahboard_job import TramsDashboardJob
from internet_of_trams.utils.get_config import get_config
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from tortoise import Tortoise, run_async

config = get_config()

job = TramsDashboardJob(
    database_host=config["DATABASE_HOST"],
    database_port=config["DATABASE_PORT"],
    database_password=config["DATABASE_PASSWORD"])

run_async(job.get_static_data())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Internet of Trams"),    
    html.Iframe(id="map_ZTM", width="100%", height='600'),    
    dbc.Col([
        dcc.Dropdown(
            id='line-selector',
            options=[{'label': str(line), 'value': line} for line in config["LINES"]],
            value=None, 
            multi=True
        ),
        html.Br(),
        html.Label("Zoom"),
        dcc.Slider(
            id='zoom-slider',
            min=-0,
            max=5,
            step=0.5,
            value=0,
            marks={i: str(i) for i in range(0, 6, 5)}
        ),
        html.Br(),
        html.Label("X Position"),
        dcc.Slider(
            id='x-slider',
            min=-20,
            max=20,
            step=0.1,
            value=0,
            marks={i: str(i) for i in range(-20, 21, 5)}
        ),
        html.Br(),
        html.Label("Y Position"),
        dcc.Slider(
            id='y-slider',
            min=-20,
            max=20,
            step=0.1,
            value=0,
            marks={i: str(i) for i in range(-20, 21, 5)}
        )
    ], width=7),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # 10 seconds
        n_intervals=0
    )
])

@app.callback(
    Output("map_ZTM", "srcDoc"),
    [Input('interval-component', 'n_intervals'),
     Input("line-selector", "value"),
     Input("zoom-slider", "value"),
     Input("x-slider", "value"),
     Input("y-slider", "value")]
)
def update_map(n_intervals, selected_lines_dropdown, zoom, longitude_shift, latitude_shift):
    if selected_lines_dropdown is None:
        lines = []
    else:
        lines = selected_lines_dropdown
    
    return job.get_map_html(lines, zoom, longitude_shift, latitude_shift)

if __name__ == '__main__':
    app.run_server(debug=False, port = 3000, host="0.0.0.0")
